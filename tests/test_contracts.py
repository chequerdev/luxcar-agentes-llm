import pytest
from pydantic import ValidationError

from src.contracts import AgentInput, AgentOutput


def test_input_is_free_text_and_builds_thread_id():
    request = AgentInput(text="  Qual câmbio?  ", user_id="u1", session_id="s1", case_id="c1")
    assert request.text == "Qual câmbio?"
    assert request.thread_id == "u1:s1:c1"


def test_empty_input_is_rejected():
    with pytest.raises(ValidationError):
        AgentInput(text="   ")


def test_output_forbids_unknown_fields():
    with pytest.raises(ValidationError):
        AgentOutput(result="x", sources=[], sufficient=True, status="answered",
                    termination_reason="completed", thread_id="t", invented=True)

