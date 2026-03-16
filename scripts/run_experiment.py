"""Run a full experiment series from a directory of YAML configs."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config
from src.utils.cost_tracker import CostTracker
from src.orchestrator.engine import SimulationEngine


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_experiment.py <configs_dir>")
        sys.exit(1)
    configs_dir = Path(sys.argv[1])
    config_files = sorted(configs_dir.glob("*.yaml"))
    if not config_files:
        print(f"No YAML configs found in {configs_dir}")
        sys.exit(1)
    print(f"Found {len(config_files)} configs")

    # Shared cost tracker across all runs
    base_path = configs_dir.parent / "base.yaml"
    first_config = load_config(
        str(config_files[0]),
        base_path=str(base_path) if base_path.exists() else None,
    )
    shared_tracker = CostTracker(
        max_per_run=first_config.max_cost_per_run_usd,
        max_total=first_config.max_total_budget_usd,
    )

    results = []
    for config_path in config_files:
        config = load_config(
            str(config_path),
            base_path=str(base_path) if base_path.exists() else None,
        )
        output_dir = f"data/raw/{config.run_id}"
        print(f"\n{'='*60}")
        print(f"Run: {config.run_id} | Attacker: {config.attacker_model}")
        try:
            shared_tracker.new_run()
            engine = SimulationEngine(config=config, output_dir=output_dir)
            engine.cost_tracker = shared_tracker
            result = await engine.run()
            results.append({"run_id": config.run_id, "outcome": result.outcome, "turn": result.turn})
            print(f"Result: {result.outcome} at turn {result.turn}")
            if result.end_condition == "budget_exceeded":
                print("Budget exceeded, stopping experiment.")
                break
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"run_id": config.run_id, "outcome": "ERROR", "error": str(e)})
    print(f"\n{'='*60}")
    print("Summary:")
    for r in results:
        print(f"  {r['run_id']}: {r.get('outcome', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
