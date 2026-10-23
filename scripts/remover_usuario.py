"""Remove um titular das memórias, checkpoints e logs locais."""
from __future__ import annotations

import argparse
import json

from src.memory import MemoryStore

parser = argparse.ArgumentParser(description="Esquecimento completo de um usuário LuxCar")
parser.add_argument("--user-id", required=True)
args = parser.parse_args()
print(json.dumps(MemoryStore().forget_user_everywhere(args.user_id), ensure_ascii=False, indent=2))
