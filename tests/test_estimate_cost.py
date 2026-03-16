import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.estimate_cost import estimate_run


def test_estimate_run_uses_usd_key(tmp_path):
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("""
run_id: "cost_test"
attacker_model: "gpt"
roles:
  comptable: "deepseek"
  rh: "claude"
  dsi: "gemini"
  ceo: "grok"
max_turns: 30
""")
    result = estimate_run(str(yaml_file))
    assert "estimated_cost_usd" in result
    assert "estimated_cost_eur" not in result


def test_estimate_run_ceo_called_once(tmp_path):
    """CEO profiler is called once, not per-turn. Its cost should equal exactly 1 call."""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("""
run_id: "ceo_test"
attacker_model: "gpt"
roles:
  comptable: "gpt"
  rh: "gpt"
  dsi: "gpt"
  ceo: "gpt"
max_turns: 30
""")
    result = estimate_run(str(yaml_file))
    breakdown = result["breakdown"]
    # GPT pricing: input=$5/M, output=$15/M
    # 1 call: 500 input + 300 output tokens
    expected_ceo_cost = round(500 / 1_000_000 * 5.0 + 300 / 1_000_000 * 15.0, 4)
    assert breakdown["ceo(gpt)"] == expected_ceo_cost
    # Per-turn agent uses est_turns = 30 // 2 = 15 calls
    expected_attacker_cost = round(15 * 500 / 1_000_000 * 5.0 + 15 * 300 / 1_000_000 * 15.0, 4)
    assert breakdown["attacker(gpt)"] == expected_attacker_cost
