"""CLI e API pública do LuxCar Parte 2."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langgraph.types import Command

from src.config import MAX_STEPS, MODEL, RECURSION_LIMIT
from src.contracts import AgentInput, AgentOutput, HumanDecision
from src.graph import graph

MAX_PASSOS = MAX_STEPS  # compatibilidade com a suíte histórica da Parte 1


def _pending_output(request: AgentInput, result: dict[str, Any]) -> AgentOutput:
    interrupts = result.get("__interrupt__", [])
    action = interrupts[0].value if interrupts else {"question": "Aguardando aprovação"}
    return AgentOutput(
        result="A execução está pausada aguardando revisão humana.", sources=[], sufficient=False,
        status="pending_approval", termination_reason="awaiting_human", thread_id=request.thread_id,
        action=action,
    )


def run_agent(request: AgentInput | str, **identity: Any) -> AgentOutput:
    if isinstance(request, str):
        request = AgentInput(text=request, **identity)
    config = {"configurable": {"thread_id": request.thread_id}, "recursion_limit": RECURSION_LIMIT}
    result = graph.invoke({"input": request.model_dump(), "thread_id": request.thread_id}, config=config)
    if "__interrupt__" in result:
        return _pending_output(request, result)
    return AgentOutput.model_validate(result["output"])


def resume_agent(thread_id: str, decision: HumanDecision | dict[str, Any]) -> AgentOutput:
    decision = HumanDecision.model_validate(decision)
    config = {"configurable": {"thread_id": thread_id}, "recursion_limit": RECURSION_LIMIT}
    result = graph.invoke(Command(resume=decision.model_dump()), config=config)
    if "__interrupt__" in result:
        request = AgentInput.model_validate(result["input"])
        return _pending_output(request, result)
    return AgentOutput.model_validate(result["output"])


def main() -> None:
    parser = argparse.ArgumentParser(description="LuxCar — consulta em linguagem natural")
    parser.add_argument("text", nargs="?", help="Pergunta em texto livre")
    parser.add_argument("--user-id", default="cli")
    parser.add_argument("--session-id", default="default")
    parser.add_argument("--case-id")
    parser.add_argument("--resume-thread")
    parser.add_argument("--decision", choices=["approve", "reject", "edit"])
    parser.add_argument("--edits", default="{}", help="JSON com campos editados")
    args = parser.parse_args()
    if args.resume_thread:
        if not args.decision:
            parser.error("--decision é obrigatório com --resume-thread")
        output = resume_agent(args.resume_thread, HumanDecision(decision=args.decision, edits=json.loads(args.edits)))
    else:
        text = args.text or input("Usuário: ")
        output = run_agent(AgentInput(text=text, user_id=args.user_id, session_id=args.session_id, case_id=args.case_id))
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

