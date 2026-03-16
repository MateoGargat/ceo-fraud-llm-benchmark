from __future__ import annotations
from typing import Literal
import yaml
from pydantic import BaseModel, field_validator

ModelName = Literal["gpt", "claude", "gemini", "deepseek", "grok", "codex"]

class RunConfig(BaseModel):
    run_id: str
    attacker_model: ModelName
    roles: dict[str, ModelName]  # comptable, rh, dsi, ceo -> model
    seed: int = 42
    temperature_attacker: float = 0.9
    temperature_defenders: float = 0.3
    temperature_ceo: float = 0.7
    max_turns: int = 30
    max_retries_format: int = 2
    max_cost_per_run_eur: float = 10.0
    max_total_budget_eur: float = 200.0

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, v: dict) -> dict:
        required = {"comptable", "rh", "dsi", "ceo"}
        if set(v.keys()) != required:
            raise ValueError(f"Roles must be exactly {required}, got {set(v.keys())}")
        return v

def load_config(path: str) -> RunConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return RunConfig(**data)
