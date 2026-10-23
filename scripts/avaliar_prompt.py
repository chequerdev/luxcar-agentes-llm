"""Ablation curta e reproduzível do prompt de triagem."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

from src.config import API_KEY, BASE_URL, MODEL, PROVIDER
from src.contracts import TriageDecision
from src.prompt_loader import load_prompt

ROOT = Path(__file__).resolve().parents[1]
PROMPT, VERSION = load_prompt("triage-v2.md")
REMOVED = "Nunca complete ano,\nversão, telefone ou veículo por suposição."
CASES = ["Qual câmbio ele usa?", "Quais versões do Polo existem?", "Registre meu interesse nesse carro."]


def call(client: OpenAI, prompt: str, text: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt + "\nSchema:\n" + json.dumps(TriageDecision.model_json_schema())},
                  {"role": "user", "content": text}],
    )
    return TriageDecision.model_validate_json(response.choices[0].message.content or "{}").model_dump()


if not API_KEY:
    raise SystemExit("Configure uma chave antes da ablação")
if REMOVED not in PROMPT:
    raise SystemExit("Frase de ablação não encontrada; atualize o experimento")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=20.0)
ablated = PROMPT.replace(REMOVED, "")
results = []
for text in CASES:
    results.append({"input": text, "with_sentence": call(client, PROMPT, text),
                    "without_sentence": call(client, ablated, text)})
record = {"executed_at": datetime.now(timezone.utc).isoformat(), "provider": PROVIDER, "model": MODEL,
          "prompt_version": VERSION, "removed_sentence": REMOVED.replace("\n", " "), "cases": results}
path = ROOT / "logs" / "parte2-ablation-prompt.json"
path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(path.relative_to(ROOT))

