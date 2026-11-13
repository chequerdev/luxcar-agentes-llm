from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace as NS

import pytest

from scripts.avaliar_negociacao import evaluate
from src.negociacao.agent import Agent, OUTPUT_ALLOWANCE, build_agent

POLO = "Abra uma proposta para o Polo por R$ 70.000,00"


@pytest.fixture
def agent(tmp_path):
    return build_agent(tmp_path / "data.sqlite", tmp_path / "run.jsonl")


def test_golden(tmp_path):
    result = evaluate("local", tmp_path)
    assert result["aprovados"] == result["total"] == 5


def test_only_same_seller_can_confirm(agent):
    request = agent.execute("ana", text=POLO)
    assert agent.store.count() == 0
    review = request["revisao_id"]
    assert agent.execute("bruno", review=review, approval=True)["motivo"] == "revisao_nao_encontrada"
    assert agent.execute("ana", review=review, approval=True)["motivo"] == "gravada"
    assert agent.execute("ana", review=review, approval=True)["motivo"] == "ja_registrada"
    assert agent.store.count() == 1


def test_reject(agent):
    review = agent.execute("ana", text=POLO)["revisao_id"]
    assert agent.execute("ana", review=review, approval=False)["motivo"] == "rejeitada"
    assert agent.execute("ana", review=review, approval=True)["motivo"] == "rejeitada"
    assert agent.store.count() == 0


def test_expiry(agent):
    initial = datetime.now(timezone.utc)
    agent.store.clock = lambda: initial
    review = agent.execute("ana", text=POLO)["revisao_id"]
    agent.store.clock = lambda: initial + timedelta(minutes=15)
    assert agent.execute("ana", review=review, approval=True)["motivo"] == "confirmacao_expirada"
    assert agent.store.count() == 0


def test_race(agent):
    reviews = [(name, agent.execute(name, text=POLO)["revisao_id"]) for name in ("ana", "bruno")]
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda pair: agent.execute(pair[0], review=pair[1], approval=True)["motivo"], reviews))
    assert sorted(outcomes) == ["gravada", "negociacao_ativa"]
    assert agent.store.count() == 1


@pytest.mark.parametrize("contents", [None, "INVALID JSON", '[{"id": 1}]'])
def test_invalid_source(agent, tmp_path, contents):
    agent.store.catalog = tmp_path / "catalog.json"
    if contents:
        agent.store.catalog.write_text(contents, encoding="utf-8")
    assert agent.execute("ana", text=POLO)["motivo"] == "erro_dados"
    record = json.loads(agent.logfile.read_text(encoding="utf-8"))
    assert record["trajetoria"][-1]["erro"] == record["motivo_termino"] == "erro_dados"
    assert agent.store.count() == 0


@pytest.mark.parametrize(("arguments", "tokens", "reason"), [
    ({"veiculo_id": 1, "valor_centavos": 7000000}, 30, "aguardando_confirmacao"),
    ({"veiculo_id": True, "valor_centavos": 7000000}, 30, "erro_modelo"),
    ({"veiculo_id": 2, "valor_centavos": 7000000}, 30, "erro_modelo"),
    ({"veiculo_id": 1, "valor_centavos": 7000000}, OUTPUT_ALLOWANCE + 1, "limite_tokens"),
])
def test_tool_call_contract(agent, arguments, tokens, reason):
    def create(**params):
        assert params["max_completion_tokens"] == OUTPUT_ALLOWANCE
        return NS(id="test-not-live", usage=NS(prompt_tokens=400, completion_tokens=tokens),
                  choices=[NS(finish_reason="tool_calls", message=NS(tool_calls=[
                      NS(function=NS(name="registrar_proposta", arguments=json.dumps(arguments)))
                  ]))])
    client = NS(chat=NS(completions=NS(create=create)))
    llm = Agent(agent.store, agent.logfile, mode="llm", client=client)
    assert llm.execute("ana", text=POLO)["motivo"] == reason
    assert agent.store.count() == 0


def test_revalidates_inventory_after_confirmation(agent, tmp_path):
    review = agent.execute("ana", text=POLO)["revisao_id"]
    changed = json.loads(agent.store.inventory.read_text(encoding="utf-8"))
    changed[0]["status"] = "vendido"
    agent.store.inventory = tmp_path / "inventory.json"
    agent.store.inventory.write_text(json.dumps(changed), encoding="utf-8")
    assert agent.execute("ana", review=review, approval=True)["motivo"] == "veiculo_indisponivel"
    assert agent.store.count() == 0


@pytest.mark.parametrize("request_text", [
    "Abra uma proposta para o veículo 1 ano 2020 por R$ 70.000,00",
    "Abra uma proposta para o Audi Polo por R$ 70.000,00",
    "Não abra uma proposta para o Polo por R$ 70.000,00",
])
def test_ambiguous_input_is_blocked(agent, request_text):
    assert agent.execute("ana", text=request_text)["motivo"] == "divergencia"
    assert agent.store.count() == 0


def test_openai_sdk_end_to_end(agent):
    """O SDK serializa ferramentas e consumo. Transporte simulado, não chamada à Groq."""
    import httpx
    from openai import OpenAI

    calls = []

    def transport(request):
        assert request.url.path == "/openai/v1/chat/completions"
        body = json.loads(request.content)
        calls.append(body)
        assert body["tool_choice"] == "required"
        assert len(body["tools"]) == 3
        return httpx.Response(200, json={
            "id": "sdk-mock", "object": "chat.completion", "created": 0,
            "model": "openai/gpt-oss-20b",
            "choices": [{"index": 0, "finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": None, "tool_calls": [{"id": "tool-1", "type": "function",
                    "function": {"name": "registrar_proposta",
                                 "arguments": '{"veiculo_id":1,"valor_centavos":7000000}'}}]}}],
            "usage": {"prompt_tokens": 900, "completion_tokens": 45, "total_tokens": 945},
        })

    http = httpx.Client(transport=httpx.MockTransport(transport))
    with OpenAI(api_key="test-only", base_url="https://mock.invalid/openai/v1", http_client=http) as client:
        llm = Agent(agent.store, agent.logfile, mode="llm", client=client)
        initial = llm.execute("ana", text=POLO)
        assert initial["motivo"] == "aguardando_confirmacao"
        assert agent.store.count() == 0
        final = llm.execute("ana", review=initial["revisao_id"], approval=True)
        assert final["motivo"] == "gravada"
        assert agent.store.count() == len(calls) == 1
    first, second = (json.loads(line) for line in agent.logfile.read_text(encoding="utf-8").splitlines())
    assert first["tokens"] == {"entrada": 900, "saida": 45}
    assert second["modo"] == "confirmacao_humana"
    assert second["tokens"] == {"entrada": 0, "saida": 0}
