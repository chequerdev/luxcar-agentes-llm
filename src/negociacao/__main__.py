"""Interface textual local. Confirmação é um comando separado da entrada do modelo."""
import argparse
import json
from pathlib import Path

from .agent import ROOT, build_agent


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    parser = argparse.ArgumentParser(description="LuxCar — decisão comercial e registro de propostas")
    parser.add_argument("--modo", choices=("local", "llm"), default="llm")
    parser.add_argument("--db", type=Path, default=ROOT / ".runtime/negociacao.sqlite")
    parser.add_argument("--log", type=Path, default=ROOT / ".runtime/negociacao.jsonl")
    parser.add_argument("--vendedor", required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--mensagem")
    action.add_argument("--confirmar", metavar="REVISAO_ID")
    action.add_argument("--rejeitar", metavar="REVISAO_ID")
    args = parser.parse_args()
    try:
        agent = build_agent(args.db, args.log, mode=args.modo if args.mensagem else "local")
    except (ValueError, ImportError) as err:
        parser.error(str(err))
    out = agent.execute(args.vendedor, text=args.mensagem, review=args.confirmar or args.rejeitar,
                        approval=args.confirmar is not None)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
