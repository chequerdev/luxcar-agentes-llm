from uuid import uuid4

from src.main import run_agent


def test_inexistent_vehicle_cannot_reach_approval():
    result = run_agent("Registre meu interesse no Polo TSI 2030, telefone 11999998888",
                       user_id="controle", session_id=uuid4().hex)
    assert result.status == "not_found"
    assert result.action is None


def test_edit_cannot_change_vehicle():
    from src.main import resume_agent
    result = run_agent("Registre meu interesse no Polo TSI 2018, telefone 11999998888",
                       user_id="controle", session_id=uuid4().hex)
    assert result.status == "pending_approval"
    result = resume_agent(result.thread_id, {"decision": "edit", "edits": {"modelo": "Golf"}})
    assert result.status == "rejected"
    assert "registrar_interesse" not in result.tool_calls


def test_suspension_prevents_resume(monkeypatch):
    from src.main import resume_agent
    initial = run_agent("Registre meu interesse no Polo TSI 2018, telefone 11999998888",
                        user_id="controle", session_id=uuid4().hex)
    assert initial.status == "pending_approval"
    monkeypatch.setenv("LUXCAR_SUSPENSO", "1")
    result = resume_agent(initial.thread_id, {"decision": "approve"})
    assert result.status == "refused"
    assert result.action is None


def test_memory_entry_accepts_only_structured_reference(tmp_path):
    import pytest
    from src.memory import MemoryStore
    store = MemoryStore(tmp_path / "memory.sqlite")
    with pytest.raises(ValueError):
        store.remember_vehicle_lookup("controle", 1, "texto livre não verificado")
    assert not store.similar_episodes("controle", "veiculo")
