import json

import pandas as pd

from analysis.scripts.extract_metrics import extract_run, main


def test_extract_run_handles_missing_outcome(tmp_path):
    log_file = tmp_path / "run.json"
    log_file.write_text(
        json.dumps({
            "run_id": "r1",
            "outcome": None,
            "messages": [],
            "trust_levels": [],
        }),
        encoding="utf-8",
    )

    result = extract_run(log_file)

    assert result["run_id"] == "r1"
    assert result["outcome"] == "UNKNOWN"
    assert result["total_turns"] == 0


def test_extract_metrics_main_writes_processed_csv(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    (raw_dir / "good.json").write_text(
        json.dumps({
            "run_id": "good",
            "outcome": {"outcome": "WIN_ATTACKER", "end_condition": "virement_execute", "total_turns": 4},
            "messages": [],
            "trust_levels": [],
        }),
        encoding="utf-8",
    )
    (raw_dir / "bad.json").write_text("not json", encoding="utf-8")

    exit_code = main(raw_dir=raw_dir, processed_dir=processed_dir)

    assert exit_code == 0
    csv_path = processed_dir / "outcomes.csv"
    assert csv_path.exists()
    df = pd.read_csv(csv_path)
    assert list(df["run_id"]) == ["good"]
    assert list(df["log_status"]) == ["complete"]
