"""Cria ficha de rotulagem e mede concordância do juiz com rótulos humanos."""
import argparse
import csv
import json
import math
import re
import time
from hashlib import sha256
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


def request_verdict(client, model, rubric, row, *, sleep=time.sleep):
    from openai import BadRequestError, RateLimitError

    json_failures = 0
    rate_failures = 0
    while True:
        try:
            return client.chat.completions.create(
                model=model, temperature=0, max_completion_tokens=512, response_format={"type": "json_object"},
                messages=[{"role": "system", "content": rubric},
                          {"role": "user", "content": json.dumps(
                              {k: row[k] for k in ("entrada", "saida")}, ensure_ascii=False)}])
        except BadRequestError as err:
            if err.code != "json_validate_failed":
                raise
            json_failures += 1
            if json_failures >= 4:
                raise ValueError(
                    f"A API não conseguiu gerar JSON válido no caso {row['id']} após quatro tentativas. "
                    "O progresso foi preservado. Rode o mesmo comando para retomar."
                ) from None
            delay = 2 * json_failures
            print(f"JSON rejeitado pela API no caso {row['id']}. Tentando de novo em {delay}s.", flush=True)
            sleep(delay)
        except RateLimitError as err:
            rate_failures += 1
            if rate_failures >= 7:
                raise ValueError("A Groq ainda está limitando chamadas. Rode o mesmo comando depois para retomar.") from None
            raw = err.response.headers.get("retry-after")
            match = re.search(r"try again in (?:([0-9.]+)m)?\s*([0-9.]+)s", str(err), re.I)
            try:
                delay = float(raw) if raw else 0
            except ValueError:
                delay = 0
            if not math.isfinite(delay) or delay <= 0:
                delay = (60 * float(match[1] or 0) + float(match[2])) if match else 0
            if delay > 90:
                raise ValueError("A API pediu uma espera maior que 90 segundos. Rode o mesmo comando mais tarde.") from None
            delay = max(delay + 1, min(60, 5 * 2 ** (rate_failures - 1)))
            print(f"Limite da API no caso {row['id']}. Aguardando {delay:.1f}s para tentar de novo.", flush=True)
            sleep(delay)


def atomic_json(path, value):
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


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
    rubric = RUBRIC.read_text(encoding="utf-8")
    signature = sha256(json.dumps([rows, rubric, MODEL, BASE_URL, 0, 512],
                                  ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    partial = output.with_name(output.name + ".parcial")
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence = []
    if partial.exists():
        checkpoint = json.loads(partial.read_text(encoding="utf-8"))
        if checkpoint.get("assinatura") != signature:
            raise ValueError("A rodada parcial é de outra configuração. Use um nome de saída novo.")
        evidence = checkpoint["casos"]
        if [item["id"] for item in evidence] != [row["id"] for row in rows[:len(evidence)]]:
            raise ValueError("A rodada parcial não corresponde à ordem do CSV.")
        print(f"Retomando: {len(evidence)}/{len(rows)} casos já salvos.", flush=True)
    with OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=20, max_retries=0) as client:
        for index, row in enumerate(rows[len(evidence):], start=len(evidence) + 1):
            res = request_verdict(client, MODEL, rubric, row)
            verdict = json.loads(res.choices[0].message.content or "{}")
            if type(verdict.get("util")) is not bool or not isinstance(verdict.get("nota"), str):
                raise ValueError(f"Resposta inválida do juiz: {row['id']}")
            h, j = int(row["humano"]), int(verdict["util"])
            evidence.append({"id": row["id"], "humano": h, "juiz": j, "nota_juiz": verdict["nota"],
                             "nota_humana": row["nota_humana"], "revisor": row["revisor"],
                             "status_original": row["status"],
                             "classificacao_desacordo": "pendente" if h != j else None})
            atomic_json(partial, {"assinatura": signature, "casos": evidence})
            print(f"{index}/{len(rows)} — caso {row['id']} avaliado.", flush=True)
    for item in evidence:
        matrix[f"humano_{item['humano']}_juiz_{item['juiz']}"] += 1
    agreement = (matrix["humano_0_juiz_0"] + matrix["humano_1_juiz_1"]) / len(rows)
    report = {"rubrica": "1.0.0", "modelo": MODEL, "n": len(rows), "limiar": THRESHOLD, "matriz": matrix,
              "concordancia": agreement, "adotado": False, "decisao": "revisar_desacordos_e_falsos_positivos",
              "casos": evidence}
    atomic_json(output, report)
    partial.unlink(missing_ok=True)
    print(f"Resultado salvo em {output}", flush=True)


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
