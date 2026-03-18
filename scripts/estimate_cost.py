"""Estimate API costs for an experiment series before running."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config
from src.utils.cost_tracker import PRICING


def collect_run_config_files(path: Path) -> list[Path]:
    if not path.exists():
        raise FileNotFoundError(f"Config path not found: {path}")
    if path.is_dir():
        return [p for p in sorted(path.glob("*.yaml")) if p.name != "base.yaml"]
    if path.name == "base.yaml":
        raise ValueError("base.yaml is a shared base config, not a runnable simulation file")
    return [path]


def estimate_run(config_path: str) -> dict:
    path = Path(config_path)
    base_candidates = [path.parent / "base.yaml", path.parent.parent / "base.yaml"]
    base_path = next((p for p in base_candidates if p.exists()), None)
    config = load_config(config_path, base_path=str(base_path) if base_path else None)
    tokens_per_agent_per_turn_in = 500
    tokens_per_agent_per_turn_out = 300
    est_turns = config.max_turns // 2
    total_cost = 0.0
    breakdown = {}

    # CEO profiler: called once, not per-turn
    ceo_model = config.roles.get("ceo", "claude")
    ceo_pricing = PRICING.get(ceo_model, {"input": 5.0, "output": 15.0})
    ceo_cost = (tokens_per_agent_per_turn_in / 1_000_000 * ceo_pricing["input"]
                + tokens_per_agent_per_turn_out / 1_000_000 * ceo_pricing["output"])
    breakdown[f"ceo({ceo_model})"] = round(ceo_cost, 4)
    total_cost += ceo_cost

    # Per-turn agents: attacker + defenders (excluding ceo)
    per_turn_agents = ["attacker"] + [r for r in config.roles if r != "ceo"]
    for agent in per_turn_agents:
        model = config.attacker_model if agent == "attacker" else config.roles.get(agent, "claude")
        pricing = PRICING.get(model, {"input": 5.0, "output": 15.0})
        cost = (est_turns * tokens_per_agent_per_turn_in / 1_000_000 * pricing["input"]
                + est_turns * tokens_per_agent_per_turn_out / 1_000_000 * pricing["output"])
        breakdown[f"{agent}({model})"] = round(cost, 4)
        total_cost += cost

    return {"run_id": config.run_id, "estimated_cost_usd": round(total_cost, 4), "breakdown": breakdown}


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/estimate_cost.py <config_or_dir>")
        sys.exit(1)
    path = Path(sys.argv[1])
    total = 0.0
    try:
        configs = collect_run_config_files(path)
        if not configs:
            raise ValueError(f"No run configs found in {path}")
        for cp in configs:
            est = estimate_run(str(cp))
            print(f"{est['run_id']}: ~{est['estimated_cost_usd']}USD  {est['breakdown']}")
            total += est["estimated_cost_usd"]
        print(f"\nTotal estimated: ~{round(total, 2)}USD")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
