"""Resume o JSONL de spans por versão sem misturar retomadas e entradas."""
from collections import Counter, defaultdict
from math import ceil
import argparse
import json
from pathlib import Path

GOOD = {"completed", "source_missing", "out_of_scope", "insufficient_input", "awaiting_human",
        "human_rejected", "approval_expired"}
TARGET = 0.95


def summarize(rows):
    roots = defaultdict(list)
    children = defaultdict(list)
    for row in rows:
        attrs = row["atributos"]
        if attrs.get("gen_ai.operation.name") == "invoke_agent":
            roots[attrs["luxcar.versao"]].append(row)
        else:
            children[row["trace_id"]].append(row)
    for version, group in sorted(roots.items()):
        lat = sorted((r["fim_ns"] - r["inicio_ns"]) / 1e6 for r in group)
        term = Counter(r["atributos"]["luxcar.motivo_termino"] for r in group)
        tools = defaultdict(Counter)
        model_calls = 0
        for root in group:
            for child in children[root["trace_id"]]:
                attrs = child["atributos"]
                if attrs["gen_ai.operation.name"] == "chat":
                    model_calls += 1
                if attrs["gen_ai.operation.name"] == "execute_tool":
                    tools[attrs["gen_ai.tool.name"]]["total"] += 1
                    tools[attrs["gen_ai.tool.name"]]["erros"] += child["status"] == "ERROR"
        good = sum(term[key] for key in GOOD)
        n = len(group)
        yield {"versao": version, "n": n, "p50_ms": round(lat[ceil(.50*n)-1], 3),
               "p95_ms": round(lat[ceil(.95*n)-1], 3), "motivos": dict(term),
               "ferramentas": {k: dict(v, taxa_erro=v["erros"]/v["total"]) for k, v in tools.items()},
               "chamadas_modelo": model_calls, "custo_api_usd_por_execucao": 0 if not model_calls else None,
               "sli": good/n, "slo": TARGET, "erros": n-good, "orcamento_consumido": (n-good)/(n*(1-TARGET))}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("traces", type=Path)
    args = p.parse_args()
    rows = [json.loads(line) for line in args.traces.read_text(encoding="utf-8").splitlines()]
    print(json.dumps(list(summarize(rows)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
