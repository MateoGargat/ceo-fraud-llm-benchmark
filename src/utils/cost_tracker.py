from __future__ import annotations


class BudgetExceededError(Exception):
    pass


# Pricing in USD per million tokens
PRICING: dict[str, dict[str, float]] = {
    "gpt":      {"input": 5.0,  "output": 15.0},
    "grok":     {"input": 2.0,  "output": 6.0},
    "deepseek": {"input": 0.14, "output": 0.28},
    "claude":   {"input": 0.0,  "output": 0.0},
    "gemini":   {"input": 0.0,  "output": 0.0},
    "codex":    {"input": 0.0,  "output": 0.0},
}


class CostTracker:
    def __init__(self, max_per_run: float, max_total: float):
        self.max_per_run = max_per_run
        self.max_total = max_total
        self.run_total: float = 0.0
        self.global_total: float = 0.0
        self.history: list[dict] = []

    def add(self, model: str, input_tokens: int, output_tokens: int) -> float:
        if model not in PRICING:
            raise ValueError(f"Unknown model: {model}. Available: {list(PRICING.keys())}")
        pricing = PRICING[model]
        cost = (input_tokens / 1_000_000 * pricing["input"] + output_tokens / 1_000_000 * pricing["output"])

        # Check BEFORE mutating
        if self.run_total + cost > self.max_per_run:
            raise BudgetExceededError(f"Run budget exceeded: {self.run_total + cost:.4f} > {self.max_per_run}")
        if self.global_total + cost > self.max_total:
            raise BudgetExceededError(f"Total budget exceeded: {self.global_total + cost:.4f} > {self.max_total}")

        self.run_total += cost
        self.global_total += cost
        self.history.append({"model": model, "input": input_tokens, "output": output_tokens, "cost": cost})
        return cost

    def new_run(self) -> None:
        self.run_total = 0.0
