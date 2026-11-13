"""Cronômetro da linha de base. O operador decide sem usar o agente."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time

ROOT = Path(__file__).resolve().parents[1]
CHOICES = {"aguardando_confirmacao", "divergencia", "veiculo_inexistente", "elegivel",
           "abaixo_do_minimo"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operador", required=True, help="Identificador fictício")
    parser.add_argument("--saida", type=Path, default=ROOT / ".runtime/linha-base-manual.json")
    args = parser.parse_args()
    cases = json.loads((ROOT / "evals/negociacao-casos.json").read_text(encoding="utf-8"))
    print("Use apenas dados/veiculos.json e dados/estoque-demo.json. Cada caso começa sem propostas ativas.")
    print("Sem agente. Escolha o motivo ao terminar. Não conte o tempo de confirmação do vendedor.")
    print("Motivos válidos:", ", ".join(sorted(CHOICES)), flush=True)
    measurements = []
    for case in cases:
        input(f"Enter para começar {case['id']}: ")
        start = time.perf_counter_ns()
        print(case["mensagem"], flush=True)
        while True:
            decision = input("Decisão: ").strip()
            if decision in CHOICES:
                break
            print("Use um dos motivos listados.")
        seconds = round((time.perf_counter_ns() - start) / 1e9, 3)
        measurements.append({"caso": case["id"], "segundos": seconds, "decisao": decision,
                             "correto": decision == case["motivo"]})
    result = {"schema": "luxcar.linha-base-manual.v1", "contexto": "bancada com dados simulados",
              "operador": args.operador, "utc": datetime.now(timezone.utc).isoformat(),
              "mediana_segundos": statistics.median(row["segundos"] for row in measurements),
              "acertos": sum(row["correto"] for row in measurements), "total": len(measurements),
              "medicoes": measurements}
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Salvo em {args.saida}")


if __name__ == "__main__":
    main()
