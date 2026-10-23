"""Grafo LangGraph do LuxCar, compilado uma única vez."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from openai import OpenAI

from .config import API_KEY, BASE_URL, CHECKPOINT_DB, HITL_TIMEOUT_HOURS, MODEL, PROVIDER, USE_LLM
from .contracts import AgentOutput, HumanDecision, SourceEvidence, TriageDecision
from .memory import MemoryStore
from .prompt_loader import load_prompt, prompt_versions
from .retrieval import find_vehicles, load_vehicles, normalize, search_corpus, vehicle_evidence
from .state import LuxCarState

MEMORY = MemoryStore()
TRIAGE_PROMPT, TRIAGE_VERSION = load_prompt("triage-v2.md")
load_prompt("answer-v2.md")  # valida o recurso procedural na importação
KNOWN_ATTRIBUTES = {
    "cambio": ("câmbio", "cambio", "transmissão", "transmissao", "marchas", "manual", "automático", "automatico"),
    "motor": ("motor", "motorização", "motorizacao"),
    "potencia_cv": ("potência", "potencia", "cv"),
    "torque_kgfm": ("torque", "kgfm"),
    "combustivel": ("combustível", "combustivel", "flex", "gasolina", "etanol"),
    "versoes": ("versões", "versoes", "versão", "versao"),
}


def _event(kind: str, **details: Any) -> list[dict[str, Any]]:
    return [{"at": datetime.now(timezone.utc).isoformat(), "kind": kind, **details}]


def _fallback_triage(text: str) -> TriageDecision:
    normal = normalize(text)
    automotive = ("carro", "veiculo", "polo", "golf", "jetta", "a3", "civic", "luxcar", "marca", "modelo")
    if not any(term in normal for term in automotive):
        return TriageDecision(route="out_of_scope", reason="Nenhum assunto automotivo identificado", confidence=0.98)
    if any(term in normal for term in ("como funciona", "politica", "privacidade", "tempo real", "aprova", "fonte")):
        return TriageDecision(route="document_query", attribute="politica", reason="Pergunta sobre política do LuxCar", confidence=0.92)
    register = any(term in normal for term in ("registre meu interesse", "registrar meu interesse", "cadastre meu interesse"))
    marca = modelo = versao = None
    for vehicle in load_vehicles():
        if normalize(vehicle["modelo"]) in normal:
            marca, modelo = vehicle["marca"], vehicle["modelo"]
            if normalize(vehicle["versao"]) in normal:
                versao = vehicle["versao"]
            break
    brand_match = re.search(r"marca\s+([\w-]+)", text, re.IGNORECASE)
    model_match = re.search(r"modelo\s+([\w-]+)", text, re.IGNORECASE)
    marca = marca or (brand_match.group(1) if brand_match else None)
    modelo = modelo or (model_match.group(1) if model_match else None)
    years = [int(year) for year in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    year = years[0] if len(set(years)) == 1 else None
    attribute = "geral"
    for name, terms in KNOWN_ATTRIBUTES.items():
        if any(normalize(term) in normal for term in terms):
            attribute = name
            break
    if len(set(years)) > 1:
        return TriageDecision(route="clarify", marca=marca, modelo=modelo, versao=versao, attribute=attribute,
                              missing=["um único ano"], reason="Mais de um ano foi informado", confidence=0.99)
    if register:
        missing = [field for field, value in (("modelo", modelo), ("ano", year)) if not value]
        return TriageDecision(route="register_interest" if not missing else "clarify", marca=marca, modelo=modelo,
                              ano=year, versao=versao, attribute=attribute, missing=missing,
                              reason="Pedido explícito de registro de interesse", confidence=0.99)
    missing = [field for field, value in (("modelo", modelo), ("ano", year)) if not value]
    return TriageDecision(route="clarify" if missing else "vehicle_query", marca=marca, modelo=modelo,
                          ano=year, versao=versao, attribute=attribute, missing=missing,
                          reason="Classificação local conservadora", confidence=0.85)


def _llm_triage(text: str) -> tuple[TriageDecision, dict[str, Any]]:
    if not USE_LLM or not API_KEY:
        return _fallback_triage(text), {"mode": "deterministic_fallback", "reason": "LLM desabilitado ou sem chave"}
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=15.0)
    schema = json.dumps(TriageDecision.model_json_schema(), ensure_ascii=False)
    try:
        response = client.chat.completions.create(
            model=MODEL, temperature=0, response_format={"type": "json_object"},
            messages=[{"role": "system", "content": TRIAGE_PROMPT + "\nSchema:\n" + schema},
                      {"role": "user", "content": text}],
        )
        decision = TriageDecision.model_validate_json(response.choices[0].message.content or "{}")
        return decision, {"mode": "llm", "provider": PROVIDER, "model": MODEL, "prompt_version": TRIAGE_VERSION}
    except Exception as error:
        return _fallback_triage(text), {"mode": "deterministic_fallback", "reason": f"{type(error).__name__}: {error}"}


def initialize(state: LuxCarState) -> dict[str, Any]:
    return {"started_at": time.monotonic(), "steps": 1, "sources": [], "tool_calls": [],
            "events": _event("run_started", prompts=prompt_versions(), model=MODEL),
            "retrieval_calls": 0, "recalled_memories": []}


def recall_memory(state: LuxCarState) -> dict[str, Any]:
    request = state["input"]
    facts = MEMORY.get_facts(request["user_id"])
    episodes = MEMORY.similar_episodes(request["user_id"], request["text"])
    recalled = [{"type": "semantic", **item} for item in facts] + [{"type": "episodic", **item} for item in episodes]
    return {"steps": state["steps"] + 1, "recalled_memories": recalled,
            "events": _event("memory_recalled", count=len(recalled))}


def triage(state: LuxCarState) -> dict[str, Any]:
    decision, metadata = _llm_triage(state["input"]["text"])
    normal_text = normalize(state["input"]["text"])
    if decision.route == "register_interest" and "interesse" not in normal_text:
        decision.route = "vehicle_query"
        decision.reason += "; rota de escrita bloqueada pelo guardrail"
    unsupported = ("consumo", "preco", "quilometragem", "seguro", "autonomia")
    if decision.route == "vehicle_query" and any(term in normal_text for term in unsupported):
        decision.attribute = "geral"
        decision.reason += "; atributo não existe no schema da base"
    return {"steps": state["steps"] + 1, "decision": decision.model_dump(),
            "events": _event("triage", decision=decision.model_dump(), **metadata)}


def route_after_triage(state: LuxCarState) -> str:
    return state["decision"]["route"]


def lookup_vehicle(state: LuxCarState) -> dict[str, Any]:
    decision = TriageDecision.model_validate(state["decision"])
    matches = find_vehicles(decision.marca, decision.modelo, decision.ano, decision.versao)
    evidence = [vehicle_evidence(vehicle).model_dump() for vehicle in matches]
    return {"steps": state["steps"] + 1, "sources": evidence, "tool_calls": ["buscar_veiculo"],
            "retrieval_calls": 1, "events": _event("structured_retrieval", matches=len(matches))}


def retrieve_documents(state: LuxCarState) -> dict[str, Any]:
    evidence = [item.model_dump() for item in search_corpus(state["input"]["text"])]
    return {"steps": state["steps"] + 1, "sources": evidence, "tool_calls": ["buscar_corpus_textual"],
            "retrieval_calls": 1, "events": _event("text_retrieval", matches=len(evidence))}


def _output(state: LuxCarState, **values: Any) -> dict[str, Any]:
    output = AgentOutput(thread_id=state["thread_id"], retrieval_calls=state.get("retrieval_calls", 0),
                         tool_calls=state.get("tool_calls", []),
                         sources=[SourceEvidence.model_validate(item) for item in state.get("sources", [])], **values)
    return {"steps": state["steps"] + 1, "output": output.model_dump(mode="json")}


def clarify(state: LuxCarState) -> dict[str, Any]:
    missing = state["decision"].get("missing") or ["identificação do veículo"]
    return _output(state, result="Preciso de " + ", ".join(missing) + " para responder sem adivinhar.",
                   sufficient=False, status="clarification_needed", termination_reason="insufficient_input")


def refuse(state: LuxCarState) -> dict[str, Any]:
    return _output(state, result="Essa solicitação está fora do escopo. O LuxCar consulta especificações e políticas sobre veículos.",
                   sufficient=False, status="refused", termination_reason="out_of_scope")


def synthesize(state: LuxCarState) -> dict[str, Any]:
    current_sources = [source for source in state.get("sources", []) if source.get("current", True)]
    decision = TriageDecision.model_validate(state["decision"])
    if not current_sources:
        return _output(state, result="Não encontrei uma fonte vigente que responda a essa pergunta. Posso consultar apenas os dados cadastrados no LuxCar.",
                       sufficient=False, status="not_found", termination_reason="source_missing")
    if decision.route == "document_query":
        return _output(state, result=current_sources[0]["excerpt"], sufficient=True,
                       status="answered", termination_reason="completed")
    vehicles = find_vehicles(decision.marca, decision.modelo, decision.ano, decision.versao)
    if not vehicles:
        return _output(state, result="O veículo informado não foi encontrado na base do LuxCar.",
                       sufficient=False, status="not_found", termination_reason="source_missing")
    if len(vehicles) > 1 and not decision.versao and decision.attribute != "versoes":
        versions = ", ".join(vehicle["versao"] for vehicle in vehicles)
        return _output(state, result=f"Há mais de uma versão cadastrada ({versions}). Qual versão você quer consultar?",
                       sufficient=False, status="clarification_needed", termination_reason="insufficient_input")
    if decision.attribute == "versoes":
        value, label = ", ".join(vehicle["versao"] for vehicle in vehicles), "versões cadastradas"
    elif decision.attribute in {"geral", "politica"}:
        return _output(state, result="A base não possui o atributo pedido ou a pergunta não especifica qual dado técnico consultar.",
                       sufficient=False, status="not_found", termination_reason="source_missing")
    else:
        vehicle = vehicles[0]
        if decision.attribute not in vehicle:
            return _output(state, result=f"A base não contém {decision.attribute} para esse veículo.",
                           sufficient=False, status="not_found", termination_reason="source_missing")
        value = vehicle[decision.attribute]
        labels = {"cambio": "câmbio", "motor": "motor", "potencia_cv": "potência",
                  "torque_kgfm": "torque", "combustivel": "combustível"}
        label = labels[decision.attribute]
    identity = f"{vehicles[0]['marca']} {vehicles[0]['modelo']} {vehicles[0]['versao']} {vehicles[0]['ano']}"
    question = normalize(state["input"]["text"])
    contradiction = decision.attribute == "cambio" and any(term in question for term in ("manual", "8 marchas", "8 velocidades"))
    prefix = "A premissa informada diverge da fonte. " if contradiction else ""
    result = prefix + f"Segundo o cadastro, o {identity} tem {label}: {value}."
    MEMORY.add_episode(state["input"]["user_id"], f"Consultou {identity}: {label}={value}")
    return _output(state, result=result, sufficient=True, status="answered", termination_reason="completed")


def prepare_action(state: LuxCarState) -> dict[str, Any]:
    text, decision = state["input"]["text"], state["decision"]
    contact_match = re.search(r"(?:telefone|contato|whatsapp)\s*[:=]?\s*([+()\d\s-]{8,})", text, re.IGNORECASE)
    action = {"type": "registrar_interesse", "marca": decision.get("marca"), "modelo": decision.get("modelo"),
              "ano": decision.get("ano"), "versao": decision.get("versao"),
              "contact": contact_match.group(1).strip() if contact_match else None,
              "prepared_at": datetime.now(timezone.utc).isoformat()}
    return {"steps": state["steps"] + 1, "proposed_action": action,
            "events": _event("action_prepared", action=action)}


def human_approval(state: LuxCarState) -> dict[str, Any]:
    action = state["proposed_action"]
    prepared_at = datetime.fromisoformat(action["prepared_at"])
    if datetime.now(timezone.utc) > prepared_at + timedelta(hours=HITL_TIMEOUT_HOURS):
        return {"steps": state["steps"] + 1, "action_result": {"approved": False, "expired": True},
                "events": _event("approval_expired")}
    payload = {"question": "Revise a ação antes da gravação.", "action": action,
               "consequence": "Cria uma solicitação persistente para atendimento humano.",
               "accepted": ["approve", "reject", "edit"], "timeout_hours": HITL_TIMEOUT_HOURS}
    response = HumanDecision.model_validate(interrupt(payload))
    if response.decision == "reject":
        return {"steps": state["steps"] + 1, "action_result": {"approved": False, "reviewer": response.reviewer},
                "events": _event("human_rejected", reviewer=response.reviewer)}
    return {"steps": state["steps"] + 1, "proposed_action": {**action, **response.edits},
            "action_result": {"approved": True, "edited": response.decision == "edit", "reviewer": response.reviewer},
            "events": _event("human_approved", reviewer=response.reviewer, edited=response.decision == "edit")}


def route_after_approval(state: LuxCarState) -> str:
    if state["action_result"].get("expired"):
        return "expired"
    return "write" if state["action_result"].get("approved") else "rejected"


def write_action(state: LuxCarState) -> dict[str, Any]:
    result = MEMORY.record_action(state["input"]["user_id"], state["proposed_action"])
    output = AgentOutput(result="Solicitação já existente; nenhuma duplicata foi criada." if result["ja_existia"] else "Solicitação de interesse registrada.",
                         sources=[SourceEvidence(source_id=result["idempotency_key"], source_type="tool",
                                                 location=".runtime/memory.sqlite#actions", excerpt="Resultado da escrita idempotente")],
                         sufficient=True, status="approved", termination_reason="completed",
                         retrieval_calls=state.get("retrieval_calls", 0), tool_calls=state.get("tool_calls", []) + ["registrar_interesse"],
                         thread_id=state["thread_id"], action=result)
    return {"steps": state["steps"] + 1, "action_result": result, "output": output.model_dump(mode="json"),
            "events": _event("action_written", **result)}


def rejected(state: LuxCarState) -> dict[str, Any]:
    return _output(state, result="A solicitação foi rejeitada e nada foi gravado.", sufficient=False,
                   status="rejected", termination_reason="human_rejected", action=state.get("action_result"))


def expired(state: LuxCarState) -> dict[str, Any]:
    return _output(state, result="O prazo de aprovação venceu; nada foi gravado.", sufficient=False,
                   status="expired", termination_reason="approval_expired", action=state.get("action_result"))


builder = StateGraph(LuxCarState)
for name, node in {"initialize": initialize, "recall_memory": recall_memory, "triage": triage,
                   "lookup_vehicle": lookup_vehicle, "retrieve_documents": retrieve_documents,
                   "clarify": clarify, "refuse": refuse, "synthesize": synthesize,
                   "prepare_action": prepare_action, "human_approval": human_approval,
                   "write_action": write_action, "rejected": rejected, "expired": expired}.items():
    builder.add_node(name, node)
builder.add_edge(START, "initialize")
builder.add_edge("initialize", "recall_memory")
builder.add_edge("recall_memory", "triage")
builder.add_conditional_edges("triage", route_after_triage, {
    "vehicle_query": "lookup_vehicle", "document_query": "retrieve_documents", "clarify": "clarify",
    "out_of_scope": "refuse", "register_interest": "prepare_action"})
builder.add_edge("lookup_vehicle", "synthesize")
builder.add_edge("retrieve_documents", "synthesize")
builder.add_edge("prepare_action", "human_approval")
builder.add_conditional_edges("human_approval", route_after_approval,
                              {"write": "write_action", "rejected": "rejected", "expired": "expired"})
for terminal in ("clarify", "refuse", "synthesize", "write_action", "rejected", "expired"):
    builder.add_edge(terminal, END)

CHECKPOINT_DB.parent.mkdir(parents=True, exist_ok=True)
_checkpoint_connection = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)
_checkpointer = SqliteSaver(_checkpoint_connection)
_checkpointer.setup()
graph = builder.compile(checkpointer=_checkpointer)

