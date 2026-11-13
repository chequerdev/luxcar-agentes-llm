"""Cria ficha de rotulagem e mede concordância do juiz com rótulos humanos."""
import argparse
import csv
import json
from pathlib import Path

from dotenv import load_dotenv

from evals.rodar import DATASET, ROOT

RUBRIC = ROOT / "evals/juiz/rubrica-v1.0.0.md"
THRESHOLD = 0.90
FIELDS = ("id", "entrada", "saida", "status", "humano", "nota_humana", "revisor")


def prepare(round_dir, labels):
    cases = {c["id"]: c for c in json.loads(DATASET.read_text(encoding="utf-8"))["casos"]}
    with labels.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator=chr(10))
        writer.writeheader()
        for line in (round_dir / "casos.jsonl").read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("inicial"):
                writer.writerow({"id": row["id"], "entrada": cases[row["id"]]["entrada"],
                                 "saida": row["inicial"]["result"], "status": row["inicial"]["status"]})


def measure(labels, output):
    with labels.open(encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r["humano"] in {"0", "1"} and
                r["nota_humana"].strip() and r["revisor"].strip()]
    if len({r["id"] for r in rows}) < 20 or len({r["humano"] for r in rows}) < 2:
        raise ValueError("Rotule ao menos 20 saídas distintas, das duas classes, com nota e revisor.")
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Há saídas duplicadas.")
    load_dotenv(ROOT / ".env")
    from src.config import API_KEY, BASE_URL, MODEL
    from openai import OpenAI
    if not API_KEY:
        raise ValueError("Configure a chave no .env para chamar o juiz.")
    matrix = {f"humano_{h}_juiz_{j}": 0 for h in (0, 1) for j in (0, 1)}
    evidence = []
    with OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=20, max_retries=0) as client:
        for row in rows:
            res = client.chat.completions.create(
                model=MODEL, temperature=0, max_completion_tokens=512, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": RUBRIC.read_text(encoding="utf-8")},
                          {"role": "user", "content": json.dumps({k: row[k] for k in ("entrada", "saida")}, ensure_ascii=False)}])
            verdict = json.loads(res.choices[0].message.content or "{}")
            if type(verdict.get("util")) is not bool or not isinstance(verdict.get("nota"), str):
                raise ValueError(f"Resposta inválida do juiz: {row['id']}")
            h, j = int(row["humano"]), int(verdict["util"])
            matrix[f"humano_{h}_juiz_{j}"] += 1
            evidence.append({"id": row["id"], "humano": h, "juiz": j, "nota_juiz": verdict["nota"],
                             "nota_humana": row["nota_humana"], "revisor": row["revisor"],
                             "status_original": row["status"],
                             "classificacao_desacordo": "pendente" if h != j else None})
    agreement = (matrix["humano_0_juiz_0"] + matrix["humano_1_juiz_1"]) / len(rows)
    report = {"rubrica": "1.0.0", "modelo": MODEL, "n": len(rows), "limiar": THRESHOLD, "matriz": matrix,
              "concordancia": agreement, "adotado": False, "decisao": "revisar_desacordos_e_falsos_positivos",
              "casos": evidence}
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    prep = sub.add_parser("preparar")
    prep.add_argument("rodada", type=Path)
    prep.add_argument("rotulos", type=Path)
    run = sub.add_parser("medir")
    run.add_argument("rotulos", type=Path)
    run.add_argument("saida", type=Path)
    args = p.parse_args()
    try:
        if args.cmd == "preparar":
            prepare(args.rodada, args.rotulos)
        else:
            measure(args.rotulos, args.saida)
    except (ValueError, FileExistsError) as err:
        p.error(str(err))


if __name__ == "__main__":
    main()
