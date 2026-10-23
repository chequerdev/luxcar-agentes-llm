"""Recuperação estruturada e textual, sem dependência de embeddings."""
from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import CORPUS_DIR, RAG_TOP_K, VEHICLES_FILE
from .contracts import SourceEvidence


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize(text))


def load_vehicles() -> list[dict[str, Any]]:
    return json.loads(VEHICLES_FILE.read_text(encoding="utf-8"))


def find_vehicles(
    marca: str | None, modelo: str | None, ano: int | None, versao: str | None = None
) -> list[dict[str, Any]]:
    found = []
    for vehicle in load_vehicles():
        if marca and normalize(vehicle["marca"]) != normalize(marca):
            continue
        if modelo and normalize(vehicle["modelo"]) != normalize(modelo):
            continue
        if ano is not None and vehicle["ano"] != ano:
            continue
        if versao and normalize(vehicle["versao"]) != normalize(versao):
            continue
        found.append(vehicle)
    return found


def vehicle_evidence(vehicle: dict[str, Any]) -> SourceEvidence:
    identity = f'{vehicle["marca"]} {vehicle["modelo"]} {vehicle["versao"]} {vehicle["ano"]}'
    return SourceEvidence(
        source_id=f'veiculo:{vehicle["id"]}',
        source_type="structured_record",
        location=f"dados/veiculos.json#id={vehicle['id']}",
        excerpt=f"{identity}: " + ", ".join(
            f"{key}={value}" for key, value in vehicle.items() if key not in {"id", "marca", "modelo", "versao", "ano"}
        ),
        score=1.0,
        current=True,
    )


@dataclass(frozen=True)
class CorpusChunk:
    source_id: str
    location: str
    text: str
    current: bool


def load_corpus() -> list[CorpusChunk]:
    chunks: list[CorpusChunk] = []
    for path in sorted(CORPUS_DIR.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        for index, section in enumerate(document["sections"], start=1):
            chunks.append(CorpusChunk(
                source_id=f'{document["id"]}#s{index}',
                location=f"dados/corpus/{path.name}#s{index}",
                text=f'{section["title"]}. {section["text"]}',
                current=document.get("status") == "vigente",
            ))
    return chunks


def search_corpus(query: str, top_k: int = RAG_TOP_K) -> list[SourceEvidence]:
    chunks = load_corpus()
    query_terms = tokens(query)
    if not query_terms:
        return []
    document_frequency = Counter()
    tokenized = []
    for chunk in chunks:
        terms = tokens(chunk.text)
        tokenized.append(terms)
        document_frequency.update(set(terms))
    scored: list[tuple[float, CorpusChunk]] = []
    for chunk, terms in zip(chunks, tokenized):
        counts = Counter(terms)
        score = sum(
            counts[term] * (math.log((len(chunks) + 1) / (document_frequency[term] + 1)) + 1)
            for term in query_terms
        )
        if score > 0:
            scored.append((score / max(len(terms) ** 0.5, 1), chunk))
    scored.sort(key=lambda pair: (pair[1].current, pair[0]), reverse=True)
    return [SourceEvidence(
        source_id=chunk.source_id,
        source_type="corpus_excerpt",
        location=chunk.location,
        excerpt=chunk.text,
        score=round(score, 4),
        current=chunk.current,
    ) for score, chunk in scored[:top_k]]

