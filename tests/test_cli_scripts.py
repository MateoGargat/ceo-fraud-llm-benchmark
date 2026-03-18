import os
import sys

import pytest

from scripts.estimate_cost import collect_run_config_files as collect_cost_files
from scripts.run_experiment import build_shared_tracker, collect_run_config_files
from scripts.run_single import load_run_config, main as run_single_main
from src.utils.config import RunConfig, load_env_file


def _write_run_config(path, run_id="run_a", max_total=200.0):
    path.write_text(
        f"""
run_id: "{run_id}"
attacker_model: "gpt"
roles:
  comptable: "deepseek"
  rh: "claude"
  dsi: "gemini"
  ceo: "grok"
max_total_budget_usd: {max_total}
""",
        encoding="utf-8",
    )


def test_load_env_file_reads_dotenv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text(
        """
OPENAI_API_KEY=test-openai
XAI_API_KEY="test-xai"
""",
        encoding="utf-8",
    )

    for key in ("OPENAI_API_KEY", "XAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    loaded = load_env_file()

    assert loaded == [env_file]
    assert os.environ["OPENAI_API_KEY"] == "test-openai"
    assert os.environ["XAI_API_KEY"] == "test-xai"


def test_load_env_file_does_not_override_existing_values(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=from-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "already-set")

    load_env_file()

    assert os.environ["OPENAI_API_KEY"] == "already-set"


def test_collect_run_config_files_skips_base_yaml(tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text("seed: 1\n", encoding="utf-8")
    run_a = tmp_path / "a.yaml"
    _write_run_config(run_a, "a")
    run_b = tmp_path / "b.yaml"
    _write_run_config(run_b, "b")

    files = collect_run_config_files(tmp_path)

    assert files == [run_a, run_b]


def test_collect_cost_files_skips_base_yaml(tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text("seed: 1\n", encoding="utf-8")
    run_a = tmp_path / "a.yaml"
    _write_run_config(run_a, "a")

    files = collect_cost_files(tmp_path)

    assert files == [run_a]


def test_build_shared_tracker_rejects_inconsistent_total_budget():
    configs = [
        RunConfig(
            run_id="a",
            attacker_model="gpt",
            roles={"comptable": "deepseek", "rh": "claude", "dsi": "gemini", "ceo": "grok"},
            max_total_budget_usd=100.0,
        ),
        RunConfig(
            run_id="b",
            attacker_model="gpt",
            roles={"comptable": "deepseek", "rh": "claude", "dsi": "gemini", "ceo": "grok"},
            max_total_budget_usd=200.0,
        ),
    ]

    with pytest.raises(ValueError, match="same max_total_budget_usd"):
        build_shared_tracker(configs)


@pytest.mark.asyncio
async def test_run_single_main_reports_user_friendly_error_for_base_yaml(tmp_path, monkeypatch, capsys):
    base = tmp_path / "base.yaml"
    base.write_text("seed: 1\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["run_single.py", str(base)])

    with pytest.raises(SystemExit) as exc:
        await run_single_main()

    assert exc.value.code == 1
    assert "ERROR:" in capsys.readouterr().out
