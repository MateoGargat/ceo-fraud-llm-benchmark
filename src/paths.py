from __future__ import annotations
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent


def resolve_prompts_dir() -> Path:
    packaged = PACKAGE_DIR / "prompts"
    if packaged.exists():
        return packaged

    repo_prompts = PROJECT_ROOT / "prompts"
    if repo_prompts.exists():
        return repo_prompts

    raise FileNotFoundError("Could not locate prompts directory in package or repository")


PROMPTS_DIR = resolve_prompts_dir()
