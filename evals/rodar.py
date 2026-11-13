"""Roda o ponto de entrada do README com bancos descartáveis e registra os resultados."""
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
import os
from pathlib import Path
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evals/golden_dataset_v2.0.0.json"


def fingerprint():
    digest = sha256()
    files = [*ROOT.glob("src/**/*.py"), *ROOT.glob("src/**/*.md"), *ROOT.glob("dados/**/*.json")]
    for path in sorted(files):
        digest.update(str(path.relative_to(ROOT)).encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def actions(memory, user):
    with memory.connect() as conn:
        return [json.loads(row["payload"]) for row in conn.execute(
            "SELECT payload FROM actions WHERE user_id=?", (user,))]


def run(directory, mode):
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    directory.mkdir(parents=True, exist_ok=False)
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        os.environ.update(LUXCAR_CHECKPOINT_DB=f"{tmp}/checkpoint.db",
                          LUXCAR_MEMORY_DB=f"{tmp}/memory.db", LUXCAR_TRACE_FILE=str(directory / "traces.jsonl"), LUXCAR_USE_LLM="0" if mode == "local" else "1")
        from src.config import API_KEY
        from src.graph import MEMORY, graph
        from src.main import run_agent, resume_agent
        if mode == "llm" and not API_KEY:
            raise ValueError("Modo llm exige chave de um provedor configurado no README.")
        for case in data["casos"]:
            expected = case["esperado"]
            user = "suite-" + case["id"]
            measured = {"id": case["id"], "classe": case["classe"], "origem": case["origem"]}
            start = time.perf_counter_ns()
            try:
                before = actions(MEMORY, user)
                output = run_agent(case["entrada"], user_id=user, session_id="rodada", case_id=case["id"])
                pending = actions(MEMORY, user)
                initial_state = graph.get_state({"configurable": {"thread_id": output.thread_id}}).values
                actual_mode = next((e.get("mode") for e in initial_state.get("events", []) if e.get("kind") == "triage"), None)
                final = repeated = None
                review = expected.get("revisao")
                if review and output.status == "pending_approval":
                    decision = {"decision": review["decisao"], "reviewer": "operador-teste", "edits": review.get("edits", {})}
                    final = resume_agent(output.thread_id, decision)
                    if review["linhas"] == 1:
                        repeated = resume_agent(output.thread_id, decision)
                after = actions(MEMORY, user)
                expected_rows = (review or expected)["linhas"]
                checks = {
                    "deterministico": output.status == expected["status"] and
                        (not expected.get("trecho") or expected["trecho"].casefold() in output.result.casefold()) and
                        (not review or bool(final and final.status == review["status"])),
                    "trajetoria": "ferramentas" not in expected or output.tool_calls == expected["ferramentas"],
                    "resultado": len(before) == len(pending) == 0 and len(after) == expected_rows and
                        (not review or not review.get("edits") or
                         bool(after and all(after[0].get(k) == v for k, v in review["edits"].items()))),
                    "provedor": mode == "local" or actual_mode == "llm",
                }
                measured.update({"checks": checks, "aprovado": all(checks.values()), "modo_observado": actual_mode,
                                 "inicial": output.model_dump(mode="json"),
                                 "final": final.model_dump(mode="json") if final else None,
                                 "repetida": repeated.status if repeated else None,
                                 "linhas": {"antes": len(before), "antes_de_confirmar": len(pending), "depois": len(after)}})
            except Exception as err:
                measured.update({"aprovado": False, "erro": type(err).__name__})
            measured["latencia_ms"] = round((time.perf_counter_ns() - start) / 1e6, 3)
            results.append(measured)
    classes = defaultdict(list)
    for result in results:
        classes[result["classe"]].append(result["aprovado"])
    report = {"dataset": data["versao"], "dataset_sha256": sha256(DATASET.read_bytes()).hexdigest(),
              "sistema_sha256": fingerprint(), "modo": mode, "executado_em": datetime.now(timezone.utc).isoformat(),
              "juiz": None, "aprovados": sum(row["aprovado"] for row in results), "total": len(results),
              "classes": {k: {"aprovados": sum(v), "total": len(v)} for k, v in sorted(classes.items())}}
    (directory / "resumo.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (directory / "casos.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument("--modo", choices=("local", "llm"), default="local")
    args = parser.parse_args()
    try:
        report = run(args.saida, args.modo)
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))
    print(f"{report['aprovados']}/{report['total']} | {args.saida}")


if __name__ == "__main__":
    main()
