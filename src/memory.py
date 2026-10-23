"""Memória semântica, episódica e escrita idempotente."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import MEMORY_DB


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_key(namespace: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{namespace}:{canonical}".encode("utf-8")).hexdigest()


class MemoryStore:
    def __init__(self, path: Path = MEMORY_DB):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._setup()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _setup(self) -> None:
        with self.connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    user_id TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL,
                    content_hash TEXT NOT NULL, updated_at TEXT NOT NULL,
                    PRIMARY KEY (user_id, key)
                );
                CREATE TABLE IF NOT EXISTS episodic_memory (
                    id TEXT PRIMARY KEY, user_id TEXT NOT NULL, summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS actions (
                    idempotency_key TEXT PRIMARY KEY, user_id TEXT NOT NULL,
                    payload TEXT NOT NULL, created_at TEXT NOT NULL
                );
            """)

    def put_fact(self, user_id: str, key: str, value: str) -> dict[str, Any]:
        payload = {"user_id": user_id, "key": key, "value": value}
        digest = content_key("semantic", payload)
        with self.connect() as connection:
            previous = connection.execute(
                "SELECT content_hash FROM semantic_memory WHERE user_id=? AND key=?", (user_id, key)
            ).fetchone()
            existed = bool(previous and previous["content_hash"] == digest)
            if not existed:
                connection.execute(
                    "INSERT INTO semantic_memory VALUES (?, ?, ?, ?, ?) "
                    "ON CONFLICT(user_id,key) DO UPDATE SET value=excluded.value, "
                    "content_hash=excluded.content_hash, updated_at=excluded.updated_at",
                    (user_id, key, value, digest, utc_now()),
                )
        return {"key": digest, "ja_existia": existed}

    def get_facts(self, user_id: str) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT key,value,updated_at FROM semantic_memory WHERE user_id=? ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_episode(self, user_id: str, summary: str) -> dict[str, Any]:
        payload = {"user_id": user_id, "summary": summary}
        digest = content_key("episode", payload)
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO episodic_memory VALUES (?, ?, ?, ?)",
                (digest, user_id, summary, utc_now()),
            )
        return {"key": digest, "ja_existia": cursor.rowcount == 0}

    def similar_episodes(self, user_id: str, query: str, limit: int = 3) -> list[dict[str, Any]]:
        query_tokens = set(re.findall(r"\w+", query.lower()))
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT summary,created_at FROM episodic_memory WHERE user_id=?", (user_id,)
            ).fetchall()
        ranked = []
        for row in rows:
            episode_tokens = set(re.findall(r"\w+", row["summary"].lower()))
            score = len(query_tokens & episode_tokens) / max(len(query_tokens | episode_tokens), 1)
            if score:
                ranked.append((score, dict(row)))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [{**row, "score": round(score, 4)} for score, row in ranked[:limit]]

    def record_action(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        stable_payload = {
            key: payload[key] for key in sorted(payload)
            if key not in {"reviewer", "reviewed_at", "prepared_at"}
        }
        digest = content_key("action", {"user_id": user_id, **stable_payload})
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO actions VALUES (?, ?, ?, ?)",
                (digest, user_id, json.dumps(payload, ensure_ascii=False, sort_keys=True), utc_now()),
            )
        return {"idempotency_key": digest, "ja_existia": cursor.rowcount == 0, "payload": payload}

    def count_action(self, idempotency_key: str) -> int:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM actions WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
        return int(row["total"])

    def forget_user(self, user_id: str) -> dict[str, int]:
        removed: dict[str, int] = {}
        with self.connect() as connection:
            for table in ("semantic_memory", "episodic_memory", "actions"):
                cursor = connection.execute(f"DELETE FROM {table} WHERE user_id=?", (user_id,))
                removed[table] = cursor.rowcount
        return removed

