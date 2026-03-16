"""Estimate API costs for an experiment series before running."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config
from src.utils.cost_tracker import PRICING


def estimate_run(config_path: str) -> dict:
    config = load_config(config_path)
    tokens_per_agent_per_turn_in = 500
    tokens_per_agent_per_turn_out = 300
    agents = ["attacker"] + list(config.roles.keys())
    total_cost = 0.0
    breakdown = {}
    for agent in agents:
        model = config.attacker_model if agent == "attacker" else config.roles.get(agent, "claude")
        pricing = PRICING.get(model, {"input": 5.0, "output": 15.0})
        est_turns = config.max_turns // 2
        cost = (est_turns * tokens_per_agent_per_turn_in / 1_000_000 * pricing["input"]
                + est_turns * tokens_per_agent_per_turn_out / 1_000_000 * pricing["output"])
        breakdown[f"{agent}({model})"] = round(cost, 4)
        total_cost += cost
    return {"run_id": config.run_id, "estimated_cost_eur": round(total_cost, 4), "breakdown": breakdown}


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/estimate_cost.py <config_or_dir>")
        sys.exit(1)
    path = Path(sys.argv[1])
    configs = sorted(path.glob("*.yaml")) if path.is_dir() else [path]
    total = 0.0
    for cp in configs:
        est = estimate_run(str(cp))
        print(f"{est['run_id']}: ~{est['estimated_cost_eur']}EUR  {est['breakdown']}")
        total += est["estimated_cost_eur"]
    print(f"\nTotal estimated: ~{round(total, 2)}EUR")


if __name__ == "__main__":
    main()
