"""Demonstra o comportamento real do LangGraph 1.0.7 sem reducer."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

ROOT = Path(__file__).resolve().parents[1]


class StateWithoutReducer(TypedDict):
    evidence: list[str]


def branch_a(_state):
    return {"evidence": ["A"]}


def branch_b(_state):
    return {"evidence": ["B"]}


builder = StateGraph(StateWithoutReducer)
builder.add_node("branch_a", branch_a)
builder.add_node("branch_b", branch_b)
builder.add_edge(START, "branch_a")
builder.add_edge(START, "branch_b")
builder.add_edge("branch_a", END)
builder.add_edge("branch_b", END)
demo = builder.compile()

record = {"executed_at": datetime.now(timezone.utc).isoformat(), "langgraph": "1.0.7"}
try:
    record["result"] = demo.invoke({"evidence": []})
    record["observed"] = "updates accepted"
except Exception as error:
    record["observed"] = "exception"
    record["exception_type"] = type(error).__name__
    record["message"] = str(error)

path = ROOT / "logs" / "parte2-reducer-sem-reducer.json"
path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, ensure_ascii=False, indent=2))

