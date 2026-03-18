"""Run a single simulation from a YAML config file."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config, load_env_file
from src.orchestrator.engine import SimulationEngine


def resolve_base_path(config_path: Path) -> Path | None:
    base_candidates = [config_path.parent / "base.yaml", config_path.parent.parent / "base.yaml"]
    return next((p for p in base_candidates if p.exists()), None)


def load_run_config(config_path: Path):
    if config_path.name == "base.yaml":
        raise ValueError("base.yaml is a shared base config, not a runnable simulation file")
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    base_path = resolve_base_path(config_path)
    return load_config(str(config_path), base_path=str(base_path) if base_path else None)


async def run_single(config_path: Path):
    load_env_file()
    config = load_run_config(config_path)
    output_dir = f"data/raw/{config.run_id}"
    print(f"Starting run: {config.run_id}")
    print(f"Attacker: {config.attacker_model}")
    print(f"Roles: {config.roles}")
    engine = SimulationEngine(config=config, output_dir=output_dir)
    return await engine.run()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_single.py <config.yaml>")
        sys.exit(1)
    try:
        result = await run_single(Path(sys.argv[1]))
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    print(f"\nResult: {result.outcome} ({result.end_condition}) at turn {result.turn}")


if __name__ == "__main__":
    asyncio.run(main())
