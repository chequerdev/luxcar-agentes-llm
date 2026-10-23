from pathlib import Path

from src.memory import MemoryStore


def test_semantic_last_write_wins_and_same_content_is_idempotent(tmp_path: Path):
    store = MemoryStore(tmp_path / "memory.sqlite")
    first = store.put_fact("u", "combustivel_preferido", "Flex")
    repeated = store.put_fact("u", "combustivel_preferido", "Flex")
    changed = store.put_fact("u", "combustivel_preferido", "Gasolina")
    assert first["ja_existia"] is False
    assert repeated["ja_existia"] is True
    assert changed["ja_existia"] is False
    assert store.get_facts("u")[0]["value"] == "Gasolina"


def test_action_idempotency_ignores_operational_timestamp(tmp_path: Path):
    store = MemoryStore(tmp_path / "memory.sqlite")
    base = {"type": "registrar_interesse", "modelo": "Polo", "ano": 2018, "contact": "1199"}
    first = store.record_action("u", {**base, "prepared_at": "2026-01-01T00:00:00+00:00"})
    second = store.record_action("u", {**base, "prepared_at": "2026-01-02T00:00:00+00:00"})
    assert first["ja_existia"] is False
    assert second["ja_existia"] is True
    assert store.count_action(first["idempotency_key"]) == 1


def test_forget_user_covers_all_long_term_structures(tmp_path: Path):
    store = MemoryStore(tmp_path / "memory.sqlite")
    store.put_fact("u", "k", "v")
    store.add_episode("u", "Consultou um Polo")
    store.record_action("u", {"type": "registrar_interesse", "modelo": "Polo"})
    removed = store.forget_user("u")
    assert removed == {"semantic_memory": 1, "episodic_memory": 1, "actions": 1}

