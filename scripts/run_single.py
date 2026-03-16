"""Run a single simulation from a YAML config file."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config
from src.orchestrator.engine import SimulationEngine


async def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_single.py <config.yaml>")
        sys.exit(1)
    config_path = sys.argv[1]
    config = load_config(config_path)
    output_dir = f"data/raw/{config.run_id}"
    print(f"Starting run: {config.run_id}")
    print(f"Attacker: {config.attacker_model}")
    print(f"Roles: {config.roles}")
    engine = SimulationEngine(config=config, output_dir=output_dir)
    result = await engine.run()
    print(f"\nResult: {result.outcome} ({result.end_condition}) at turn {result.turn}")


if __name__ == "__main__":
    asyncio.run(main())
