import pytest
from pydantic import ValidationError
from src.utils.config import RunConfig, load_config

def test_run_config_defaults():
    cfg = RunConfig(
        run_id="test_a1_rep1",
        attacker_model="claude",
        roles={"comptable": "deepseek", "rh": "gpt", "dsi": "gemini", "ceo": "grok"},
    )
    assert cfg.max_turns == 30
    assert cfg.temperature_attacker == 0.9
    assert cfg.temperature_defenders == 0.3
    assert cfg.max_cost_per_run_usd == 10.0
    assert cfg.seed == 42

def test_run_config_validation_rejects_unknown_model_specific():
    with pytest.raises(ValidationError):
        RunConfig(
            run_id="bad",
            attacker_model="unknown_model",
            roles={"comptable": "deepseek", "rh": "gpt", "dsi": "gemini", "ceo": "grok"},
        )


def test_run_config_rejects_negative_temperature():
    with pytest.raises(ValidationError):
        RunConfig(
            run_id="bad_temp",
            attacker_model="claude",
            roles={"comptable": "deepseek", "rh": "gpt", "dsi": "gemini", "ceo": "grok"},
            temperature_attacker=-0.5,
        )


def test_run_config_rejects_temperature_above_2():
    with pytest.raises(ValidationError):
        RunConfig(
            run_id="bad_temp",
            attacker_model="claude",
            roles={"comptable": "deepseek", "rh": "gpt", "dsi": "gemini", "ceo": "grok"},
            temperature_attacker=3.0,
        )


def test_load_config_merges_base(tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text("seed: 99\nmax_turns: 15\n")
    run = tmp_path / "run.yaml"
    run.write_text("""
run_id: "merge_test"
attacker_model: "gpt"
roles:
  comptable: "deepseek"
  rh: "claude"
  dsi: "gemini"
  ceo: "grok"
""")
    cfg = load_config(str(run), base_path=str(base))
    assert cfg.seed == 99
    assert cfg.max_turns == 15


def test_load_config_from_yaml(tmp_path):
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("""
run_id: "a1_rep1"
attacker_model: "gpt"
roles:
  comptable: "deepseek"
  rh: "claude"
  dsi: "gemini"
  ceo: "grok"
max_turns: 20
""")
    cfg = load_config(str(yaml_file))
    assert cfg.run_id == "a1_rep1"
    assert cfg.max_turns == 20
    assert cfg.attacker_model == "gpt"
