"""Contratos de entrada, decisões intermediárias e saída."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, description="Texto livre digitado pelo usuário")
    user_id: str = Field(default="anonimo", min_length=1)
    session_id: str = Field(default="default", min_length=1)
    case_id: str | None = None

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A entrada deve conter texto")
        return value

    @property
    def thread_id(self) -> str:
        case = self.case_id or "sem-caso"
        return f"{self.user_id}:{self.session_id}:{case}"


class SourceEvidence(BaseModel):
    source_id: str
    source_type: Literal["structured_record", "corpus_excerpt", "memory", "tool"]
    location: str
    excerpt: str
    score: float | None = None
    current: bool = True


class AgentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    result: str
    sources: list[SourceEvidence] = Field(default_factory=list)
    sufficient: bool
    status: Literal[
        "answered", "clarification_needed", "refused", "not_found",
        "pending_approval", "approved", "rejected", "expired", "error"
    ]
    termination_reason: Literal[
        "completed", "insufficient_input", "out_of_scope", "source_missing",
        "awaiting_human", "human_rejected", "approval_expired",
        "step_limit", "time_limit", "recoverable_error", "fatal_error"
    ]
    retrieval_calls: int = 0
    tool_calls: list[str] = Field(default_factory=list)
    thread_id: str
    action: dict | None = None


Route = Literal[
    "vehicle_query", "document_query", "clarify", "out_of_scope", "register_interest"
]


class TriageDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Route
    marca: str | None = None
    modelo: str | None = None
    ano: int | None = None
    versao: str | None = None
    attribute: Literal[
        "cambio", "motor", "potencia_cv", "torque_kgfm", "combustivel",
        "versoes", "geral", "politica"
    ] = "geral"
    missing: list[str] = Field(default_factory=list)
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class HumanDecision(BaseModel):
    decision: Literal["approve", "reject", "edit"]
    edits: dict[str, str | int | None] = Field(default_factory=dict)
    reviewer: str = "operador"

