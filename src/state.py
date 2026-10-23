"""Estado explícito do StateGraph e reducers."""
from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class LuxCarState(TypedDict, total=False):
    input: dict[str, Any]
    thread_id: str
    started_at: float
    steps: int
    decision: dict[str, Any]
    sources: Annotated[list[dict[str, Any]], operator.add]
    tool_calls: Annotated[list[str], operator.add]
    events: Annotated[list[dict[str, Any]], operator.add]
    retrieval_calls: Annotated[int, operator.add]
    recalled_memories: Annotated[list[dict[str, Any]], operator.add]
    proposed_action: dict[str, Any]
    action_result: dict[str, Any]
    output: dict[str, Any]

