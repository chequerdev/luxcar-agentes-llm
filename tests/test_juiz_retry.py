import csv
from contextlib import nullcontext
import json
from types import SimpleNamespace

import httpx
import openai
import pytest

from evals import validar_juiz as judge


def rate_error():
    return openai.RateLimitError(
        "Please try again in 3.69s.",
        response=httpx.Response(429, request=httpx.Request("POST", "https://example.invalid")),
        body=None,
    )


def test_rate_limit_waits_and_retries():
    calls, delays = [], []

    def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise rate_error()
        return "accepted"

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    assert judge.request_verdict(client, "model", "rubric", {"id": "1", "entrada": "x", "saida": "y"},
                                 sleep=delays.append) == "accepted"
    assert delays == [5]
    assert calls[0] == calls[1]


def test_measure_preserves_progress_and_resumes(tmp_path, monkeypatch):
    import src.config
    monkeypatch.setattr(src.config, "API_KEY", "test")
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: nullcontext(None))
    labels, out = tmp_path / "labels.csv", tmp_path / "result.json"
    with labels.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(judge.FIELDS)
        for i in range(20):
            writer.writerow((i, "entrada", "saida", "ok", int(i != 0), "nota", "revisor"))
    calls = []

    def verdict(client, model, rubric, row):
        calls.append(row["id"])
        if calls == ["0", "1"]:
            raise ValueError("falha transitória")
        content = json.dumps({"util": row["id"] != "0", "nota": "teste"})
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])

    monkeypatch.setattr(judge, "request_verdict", verdict)
    with pytest.raises(ValueError, match="transitória"):
        judge.measure(labels, out)
    assert not out.exists()
    judge.measure(labels, out)
    assert calls[:4] == ["0", "1", "1", "2"]
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["matriz"] == {"humano_0_juiz_0": 1, "humano_0_juiz_1": 0,
                               "humano_1_juiz_0": 0, "humano_1_juiz_1": 19}
    assert not out.with_name(out.name + ".parcial").exists()
