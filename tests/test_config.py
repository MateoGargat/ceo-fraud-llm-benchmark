import pytest
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

def test_run_config_validation_rejects_unknown_model():
    with pytest.raises(Exception):
        RunConfig(
            run_id="bad",
            attacker_model="unknown_model",
            roles={"comptable": "deepseek", "rh": "gpt", "dsi": "gemini", "ceo": "grok"},
        )

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
