"""Executa e grava os seis casos obrigatórios, sem fabricar saídas."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

os.environ["LUXCAR_USE_LLM"] = os.getenv("LUXCAR_USE_LLM", "0")

from src.contracts import AgentInput
from src.config import API_KEY, MODEL, PROVIDER
from src.graph import MEMORY, graph
from src.main import resume_agent, run_agent
from src.prompt_loader import prompt_versions

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
CASES = [
    ("01-simples", "Qual câmbio o Polo TSI 2018 possui?"),
    ("02-divergencia", "O Polo TSI 2018 é manual, certo?"),
    ("03-registro-inexistente", "Qual câmbio o Golf R 2020 possui?"),
    ("04-nao-dispara-acao", "Quero comprar o Polo TSI 2018. Qual é o preço dele?"),
    ("05-fora-do-corpus", "Qual é o consumo rodoviário do Polo TSI 2018?"),
    ("06-human-in-the-loop", "Registre meu interesse no Polo TSI 2018, telefone 11999998888"),
]


def source_digest() -> str:
    digest = hashlib.sha256()
    for path in sorted((ROOT / "src").rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def git_metadata() -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip())
    return {"git_head": head, "worktree_dirty": dirty, "source_tree_sha256": source_digest()}


def checkpoint(thread_id: str) -> dict:
    snapshot = graph.get_state({"configurable": {"thread_id": thread_id}})
    values = dict(snapshot.values)
    return {key: values.get(key) for key in ("steps", "decision", "tool_calls", "retrieval_calls", "events", "action_result") if key in values}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    base_metadata = {
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "provider": PROVIDER,
        "model": MODEL,
        "prompt_versions": prompt_versions(),
        **git_metadata(),
    }
    for slug, text in CASES:
        request = AgentInput(text=text, user_id="demonstracao", session_id=base_metadata["executed_at"], case_id=slug)
        initial = run_agent(request)
        initial_state = checkpoint(request.thread_id)
        triage_events = [event for event in initial_state.get("events", []) if event.get("kind") == "triage"]
        triage_event = triage_events[-1] if triage_events else {}
        metadata = {**base_metadata, "execution_mode": triage_event.get("mode", "unknown"),
                    "llm_attempted": bool(API_KEY and os.getenv("LUXCAR_USE_LLM") == "1"),
                    "llm_error": triage_event.get("reason") if triage_event.get("mode") == "deterministic_fallback" and API_KEY else None}
        record = {"case": slug, "metadata": metadata, "input": request.model_dump(),
                  "initial_output": initial.model_dump(mode="json"), "initial_state": initial_state}
        if slug == "06-human-in-the-loop":
            resumed = resume_agent(request.thread_id, {
                "decision": "edit", "edits": {"contact": "11888887777"}, "reviewer": "operador-demo"
            })
            repeated = resume_agent(request.thread_id, {"decision": "approve", "reviewer": "operador-demo"})
            action_key = resumed.action["idempotency_key"]
            record.update({
                "resume_with_edit_output": resumed.model_dump(mode="json"),
                "repeated_approval_output": repeated.model_dump(mode="json"),
                "action_rows_after_two_approvals": MEMORY.count_action(action_key),
                "final_state": checkpoint(request.thread_id),
            })
        path = LOGS / f"parte2-caso-{slug}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
        print(path.relative_to(ROOT), record.get("action_rows_after_two_approvals", initial.status))


if __name__ == "__main__":
    main()

