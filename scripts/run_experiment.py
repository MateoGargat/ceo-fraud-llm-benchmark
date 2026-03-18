"""Run a full experiment series from a directory of YAML configs."""
import asyncio
from math import isclose
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config, load_env_file
from src.utils.cost_tracker import CostTracker
from src.orchestrator.engine import SimulationEngine


def collect_run_config_files(configs_dir: Path) -> list[Path]:
    if not configs_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {configs_dir}")
    if not configs_dir.is_dir():
        raise ValueError(f"Expected a directory, got: {configs_dir}")
    return [p for p in sorted(configs_dir.glob("*.yaml")) if p.name != "base.yaml"]


def load_series_configs(config_files: list[Path], base_path: Path | None) -> list:
    configs = []
    for config_path in config_files:
        configs.append(load_config(str(config_path), base_path=str(base_path) if base_path else None))
    return configs


def build_shared_tracker(configs) -> CostTracker:
    if not configs:
        raise ValueError("No run configs found")
    max_total = configs[0].max_total_budget_usd
    for config in configs[1:]:
        if not isclose(config.max_total_budget_usd, max_total, rel_tol=0.0, abs_tol=1e-9):
            raise ValueError(
                "All configs in a series must share the same max_total_budget_usd"
            )
    return CostTracker(
        max_per_run=configs[0].max_cost_per_run_usd,
        max_total=max_total,
    )


async def run_experiment(configs_dir: Path):
    load_env_file()
    config_files = collect_run_config_files(configs_dir)
    if not config_files:
        raise ValueError(f"No run configs found in {configs_dir}")
    print(f"Found {len(config_files)} configs")
    base_path = configs_dir.parent / "base.yaml"
    base_config_path = base_path if base_path.exists() else None
    configs = load_series_configs(config_files, base_config_path)
    shared_tracker = build_shared_tracker(configs)

    results = []
    for config in configs:
        output_dir = f"data/raw/{config.run_id}"
        print(f"\n{'='*60}")
        print(f"Run: {config.run_id} | Attacker: {config.attacker_model}")
        try:
            shared_tracker.new_run()
            shared_tracker.max_per_run = config.max_cost_per_run_usd
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
    return results


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_experiment.py <configs_dir>")
        sys.exit(1)
    try:
        await run_experiment(Path(sys.argv[1]))
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
