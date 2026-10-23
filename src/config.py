"""Configuração explícita do LuxCar."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MODEL = os.getenv("LUXCAR_MODEL", "openai/gpt-oss-20b")
USE_LLM = os.getenv("LUXCAR_USE_LLM", "1").lower() not in {"0", "false", "nao", "não"}
if os.getenv("GROQ_API_KEY"):
    API_KEY = os.environ["GROQ_API_KEY"]
    BASE_URL = os.getenv("LUXCAR_BASE_URL", "https://api.groq.com/openai/v1")
    PROVIDER = "groq"
elif os.getenv("XAI_API_KEY"):
    API_KEY = os.environ["XAI_API_KEY"]
    BASE_URL = os.getenv("LUXCAR_BASE_URL", "https://api.x.ai/v1")
    PROVIDER = "xai"
elif os.getenv("OPENAI_API_KEY"):
    API_KEY = os.environ["OPENAI_API_KEY"]
    BASE_URL = os.getenv("LUXCAR_BASE_URL") or None
    PROVIDER = "openai"
else:
    API_KEY = None
    BASE_URL = os.getenv("LUXCAR_BASE_URL") or None
    PROVIDER = "none"
MAX_STEPS = 12
TIME_BUDGET_SECONDS = 30.0
RECURSION_LIMIT = 20
RAG_TOP_K = 3
MAX_CONTEXT_CHARS = 8_000
HITL_TIMEOUT_HOURS = int(os.getenv("LUXCAR_HITL_TIMEOUT_HOURS", "24"))
CHECKPOINT_DB = Path(os.getenv("LUXCAR_CHECKPOINT_DB", str(ROOT / ".runtime" / "checkpoints.sqlite")))
MEMORY_DB = Path(os.getenv("LUXCAR_MEMORY_DB", str(ROOT / ".runtime" / "memory.sqlite")))
CORPUS_DIR = ROOT / "dados" / "corpus"
VEHICLES_FILE = ROOT / "dados" / "veiculos.json"
PROMPTS_DIR = ROOT / "src" / "prompts"
LOGS_DIR = ROOT / "logs"

