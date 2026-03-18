from __future__ import annotations
import os
from typing import Literal
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

ModelName = Literal["gpt", "claude", "gemini", "deepseek", "grok", "codex"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

class RunConfig(BaseModel):
    run_id: str
    attacker_model: ModelName
    roles: dict[str, ModelName]  # comptable, rh, dsi, ceo -> model
    seed: int = Field(default=42, ge=0)
    temperature_attacker: float = 0.9
    temperature_defenders: float = 0.3
    temperature_ceo: float = 0.7
    max_turns: int = Field(default=30, ge=1)
    max_retries_format: int = Field(default=2, ge=0)
    max_cost_per_run_usd: float = Field(default=10.0, ge=0.0)
    max_total_budget_usd: float = Field(default=200.0, ge=0.0)

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, v: dict) -> dict:
        required = {"comptable", "rh", "dsi", "ceo"}
        if set(v.keys()) != required:
            raise ValueError(f"Roles must be exactly {required}, got {set(v.keys())}")
        return v

    @field_validator("temperature_attacker", "temperature_defenders", "temperature_ceo")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 2.0:
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got {v}")
        return v

    @model_validator(mode="after")
    def validate_budget_coherence(self):
        if self.max_cost_per_run_usd > self.max_total_budget_usd:
            raise ValueError("Per-run budget cannot exceed total budget")
        return self


def load_env_file(path: str | Path | None = None) -> list[Path]:
    candidates = [Path(path)] if path is not None else [Path.cwd() / ".env", PROJECT_ROOT / ".env"]
    loaded: list[Path] = []
    seen: set[Path] = set()

    for candidate in candidates:
        resolved = candidate.resolve(strict=False)
        if resolved in seen or not candidate.exists():
            continue
        seen.add(resolved)

        with open(candidate, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if stripped.startswith("export "):
                    stripped = stripped[len("export ") :].strip()
                if "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                key = key.strip()
                if not key or key in os.environ:
                    continue
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                    value = value[1:-1]
                os.environ[key] = value
        loaded.append(candidate)

    return loaded


def load_config(path: str, base_path: str | None = None) -> RunConfig:
    data: dict = {}
    if base_path:
        with open(base_path, "r", encoding="utf-8") as f:
            base_data = yaml.safe_load(f)
        if base_data is None:
            data = {}
        elif isinstance(base_data, dict):
            data = base_data
        else:
            raise ValueError("Base config YAML must contain a mapping")
    with open(path, "r", encoding="utf-8") as f:
        run_data = yaml.safe_load(f)
    if run_data is None or not isinstance(run_data, dict):
        raise ValueError("Run config YAML must contain a mapping")
    data.update(run_data)
    return RunConfig(**data)
