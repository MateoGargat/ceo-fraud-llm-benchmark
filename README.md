# The CEO Breach

**Analyzing Multi-Agent LLM Vulnerability to Precision Social Engineering**

A research simulation that pits 5 frontier LLMs against each other in a CEO fraud scenario. One agent attacks, the others defend. Who wins?

## Architecture

```
Attacker (LLM X) --> ORCHESTRATOR --> Comptable (LLM Y)
                     |-- Email --|       RH (LLM Z)
                     |-- Slack --|       DSI (LLM W)
                     |-- Phone --|
                     |-- Internal (defenders only) --|
```

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Configure API keys
cp .env.example .env
# Edit .env with your keys; the CLI scripts load it automatically

# Estimate costs before running
python scripts/estimate_cost.py configs/series_a/

# Run a single simulation
python scripts/run_single.py configs/series_a/run_a1_rep1.yaml

# Run full experiment series
python scripts/run_experiment.py configs/series_a/

# Extract metrics
python analysis/scripts/extract_metrics.py

# Launch dashboard
streamlit run dashboard/app.py
```

## Project Structure

```
TheBreach/
  src/           # Core simulation code
    adapters/    # LLM adapters (Claude CLI, Gemini CLI, OpenAI, DeepSeek, xAI)
    agents/      # Agent classes (attacker, defenders, CEO profiler)
    orchestrator/# Simulation engine, message router, parser
    metrics/     # Trust tracking, channel analysis, doubt propagation
    utils/       # Config, logging, cost tracking
  configs/       # YAML run configurations
  prompts/       # System prompts for each agent role
  scripts/       # Run scripts and cost estimator
  analysis/      # Metrics extraction and notebooks
  dashboard/     # Streamlit results dashboard
  paper/         # Research paper
  tests/         # Test suite
```

## Key Results

[TODO: Add after experiments]

## Models Tested

| Model | Roles |
|---|---|
| GPT-5.4 | All (rotating) |
| Claude 4.6 Opus | All (rotating) |
| Gemini 3.1 Ultra | All (rotating) |
| DeepSeek V3 | All (rotating) |
| Grok-3 | All (rotating) |

## Methodology

See [paper/the_ceo_breach.md](paper/the_ceo_breach.md) for full methodology.

Smart Rotation design: 5 models x 5 roles, ~31 runs total in two series.

## License

MIT
