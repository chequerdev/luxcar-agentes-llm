from uuid import uuid4

from src.contracts import AgentInput
from src.main import resume_agent, run_agent
from src.graph import MEMORY


def request(text: str, case: str) -> AgentInput:
    return AgentInput(text=text, user_id=f"pytest-{uuid4()}", session_id="s", case_id=case)


def test_happy_path_has_source_and_sufficiency(monkeypatch):
    monkeypatch.setattr("src.graph.USE_LLM", False)
    output = run_agent(request("Qual câmbio o Polo TSI 2018 possui?", "happy"))
    assert output.status == "answered"
    assert output.sufficient is True
    assert output.sources[0].source_id == "veiculo:1"
    assert output.retrieval_calls == 1


def test_out_of_scope_refuses_without_retrieval(monkeypatch):
    monkeypatch.setattr("src.graph.USE_LLM", False)
    output = run_agent(request("Qual é a previsão do tempo?", "scope"))
    assert output.status == "refused"
    assert output.sufficient is False
    assert output.retrieval_calls == 0


def test_missing_attribute_refuses_usefully(monkeypatch):
    monkeypatch.setattr("src.graph.USE_LLM", False)
    output = run_agent(request("Qual o consumo na estrada do Polo TSI 2018?", "missing"))
    assert output.status == "not_found"
    assert output.sufficient is False


def test_hitl_edit_and_repeated_resume_do_not_duplicate(monkeypatch):
    monkeypatch.setattr("src.graph.USE_LLM", False)
    req = request("Registre meu interesse no Polo TSI 2018, telefone 11999998888", "hitl")
    pending = run_agent(req)
    assert pending.status == "pending_approval"
    approved = resume_agent(req.thread_id, {"decision": "edit", "edits": {"contact": "11888887777"}})
    assert approved.status == "approved"
    repeated = resume_agent(req.thread_id, {"decision": "approve"})
    assert repeated.action["idempotency_key"] == approved.action["idempotency_key"]
    assert MEMORY.count_action(approved.action["idempotency_key"]) == 1

