from __future__ import annotations
from typing import Literal
import yaml
from pydantic import BaseModel, field_validator, model_validator

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
    max_cost_per_run_usd: float = 10.0
    max_total_budget_usd: float = 200.0

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


def load_config(path: str, base_path: str | None = None) -> RunConfig:
    data: dict = {}
    if base_path:
        with open(base_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    with open(path, "r", encoding="utf-8") as f:
        run_data = yaml.safe_load(f)
    data.update(run_data)
    return RunConfig(**data)
