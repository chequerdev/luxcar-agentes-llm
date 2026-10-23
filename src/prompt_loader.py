from __future__ import annotations

import hashlib

from .config import PROMPTS_DIR


def load_prompt(name: str) -> tuple[str, str]:
    path = PROMPTS_DIR / name
    content = path.read_text(encoding="utf-8")
    version = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    return content, version


def prompt_versions() -> dict[str, str]:
    return {path.name: load_prompt(path.name)[1] for path in sorted(PROMPTS_DIR.glob("*.md"))}

