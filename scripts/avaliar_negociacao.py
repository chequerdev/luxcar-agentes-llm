"""Executa a mesma suíte rotulada no modo local ou em três modelos reais."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import statistics
import tempfile

from dotenv import load_dotenv

from src.negociacao.agent import ROOT, build_agent

RATES = {
    "openai/gpt-oss-20b": ("0.075", "0.30"),
    "openai/gpt-oss-120b": ("0.15", "0.60"),
    "qwen/qwen3.8-27b": ("0.80", "4.00"),
}


def check(case, initial, pre, final, post):
    return (initial["motivo"] == case["motivo"] and pre == 0 and
            (final or {}).get("motivo") == case.get("depois") and post == case["linhas"])


def evaluate(mode, directory, model=None):
    cases = json.loads((ROOT / "evals/negociacao-casos.json").read_text(encoding="utf-8"))
    directory.mkdir(parents=True, exist_ok=True)
    results, latency = [], []
    cost = Decimal(0)
    measured = 0
    for case in cases:
        log = directory / f"caso-{case['id']}.jsonl"
        log.unlink(missing_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            agent = build_agent(Path(tmp) / "test.sqlite", log, mode=mode, model=model)
            result = agent.execute("vendedor_demo", text=case["mensagem"], case=case["id"])
            pre = agent.store.count()
            final = (agent.execute("vendedor_demo", review=result["revisao_id"],
                                   approval=case["confirmar"], case=case["id"])
                     if "confirmar" in case and result.get("revisao_id") else None)
            post = agent.store.count()
            results.append({"id": case["id"], "esperado": case["motivo"], "obtido": result["motivo"],
                            "antes": pre, "apos": post, "apos_decisao": (final or {}).get("motivo"),
                            "passou": check(case, result, pre, final, post)})
        trace = json.loads(log.read_text(encoding="utf-8").splitlines()[0])
        latency.append(trace["latencia_total_ms"])
        if model and trace["tokens"]["entrada"] > 0:
            price_in, price_out = map(Decimal, RATES[model])
            cost += (trace["tokens"]["entrada"] * price_in + trace["tokens"]["saida"] * price_out) / 1_000_000
            measured += 1
    summary = {"modo": mode, "modelo": model, "aprovados": sum(x["passou"] for x in results),
               "total": len(results), "latencia_mediana_ms": statistics.median(latency), "casos": results}
    if model:
        summary["chamadas_com_uso_reportado"] = measured
        summary["custo_usd"] = ({"media_execucao": str(cost / measured), "100_execucoes": str(cost / measured * 100),
                                 "semestre_2000": str(cost / measured * 2000)} if measured == len(cases) else None)
    (directory / "resumo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=("local", "comparar"), default="local")
    parser.add_argument("--saida", type=Path, default=ROOT / ".runtime/eval-negociacao")
    args = parser.parse_args()
    if args.modo == "local":
        summaries = [evaluate("local", args.saida)]
    else:
        try:
            build_agent(args.saida / "unused.sqlite", args.saida / "unused.jsonl", mode="llm")
        except ValueError as err:
            parser.error(str(err))
        summaries = [evaluate("llm", args.saida / model.replace("/", "--"), model) for model in RATES]
    for summary in summaries:
        print(summary["modo"], summary["modelo"] or "-", f"{summary['aprovados']}/{summary['total']}")
    return int(any(s["aprovados"] != s["total"] for s in summaries))


if __name__ == "__main__":
    raise SystemExit(main())
