"""Compara duas rodadas feitas com o mesmo conjunto e modo."""
from collections import Counter
import argparse
import json
from pathlib import Path


def read(path):
    return json.loads((path / "resumo.json").read_text(encoding="utf-8"))


def pct(x):
    return x["aprovados"] / x["total"] * 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("anterior", type=Path)
    parser.add_argument("nova", type=Path)
    args = parser.parse_args()
    a, b = read(args.anterior), read(args.nova)
    if (a["dataset_sha256"], a["modo"]) != (b["dataset_sha256"], b["modo"]):
        parser.error("Conjuntos ou modos diferentes. Comparação inválida.")
    if a["sistema_sha256"] == b["sistema_sha256"]:
        parser.error("As duas rodadas usam o mesmo código e corpus.")
    origens = Counter(json.loads(line)["origem"] for line in
                      (args.anterior / "casos.jsonl").read_text(encoding="utf-8").splitlines())
    composition = " · ".join(f"{k} {origens[k]}" for k in ("producao", "desenvolvimento", "sintetico"))
    print(f"DATASET v{a['dataset']}   {a['total']} casos   ({composition})")
    judge_path = Path(__file__).resolve().parent / "resultados/juiz-v1.0.0/resultado-bruto.json"
    if b["juiz"] is None and judge_path.is_file():
        judge = json.loads(judge_path.read_text(encoding="utf-8"))
        print(f"JUIZ rubrica v{judge['rubrica']}  concordância {judge['concordancia']:.1%}"
              f"  limiar {judge['limiar']:.0%}  (validação separada, não adotado)")
    elif b["juiz"] is not None:
        print(b["juiz"])
    else:
        print("JUIZ sem resultado publicado")
    print(f"{'classe':20s} {'versão A':>9s} {'versão B':>9s} {'delta':>9s}")
    for label, left, right in [(c, a["classes"][c], b["classes"][c]) for c in a["classes"]] + [("MÉDIA", a, b)]:
        x, y = pct(left), pct(right)
        print(f"{label:20s} {x:8.1f}% {y:8.1f}% {y-x:+8.1f} pp")


if __name__ == "__main__":
    main()
