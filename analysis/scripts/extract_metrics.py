"""Extract all metrics from raw run logs into CSVs."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from src.metrics.trust_tracker import TrustTracker
from src.metrics.channel_analyzer import ChannelAnalyzer
from src.metrics.doubt_propagation import DoubtPropagation


def extract_run(log_path: Path) -> dict:
    with open(log_path, encoding="utf-8") as f:
        log = json.load(f)
    run_id = log["run_id"]
    outcome = log.get("outcome") or {}
    trust = TrustTracker(log)
    channels = ChannelAnalyzer(log)
    doubt = DoubtPropagation(log)
    return {
        "run_id": run_id,
        "log_status": "complete" if outcome else "incomplete",
        "outcome": outcome.get("outcome", "UNKNOWN"),
        "end_condition": outcome.get("end_condition", ""),
        "total_turns": outcome.get("total_turns", 0),
        "total_messages": len(log.get("messages", [])),
        "comptable_final_trust": (trust.get_trajectory("comptable") or [None])[-1],
        "comptable_inflection": trust.inflection_point("comptable"),
        "comptable_suspicion_turn": trust.suspicion_turn("comptable"),
        "comptable_max_divergence": trust.max_divergence("comptable"),
        "comptable_drop_rate": trust.drop_rate("comptable"),
        "channels_used": json.dumps(channels.channels_used()),
        "first_contact_channel": channels.first_contact_channel(),
        "channel_switches": channels.channel_switches(),
        "internal_msg_count": doubt.internal_message_count(),
        "first_doubt_origin": doubt.first_doubt_origin(),
        "propagation_delay": doubt.propagation_delay(),
    }


def main(raw_dir: Path | str | None = None, processed_dir: Path | str | None = None) -> int:
    raw_dir = Path(raw_dir) if raw_dir is not None else Path("data/raw")
    processed_dir = Path(processed_dir) if processed_dir is not None else Path("data/processed")
    if not raw_dir.exists():
        print(f"No raw data directory found: {raw_dir}")
        return 1
    rows = []
    for log_file in sorted(raw_dir.rglob("*.json")):
        try:
            rows.append(extract_run(log_file))
        except Exception as e:
            print(f"Error processing {log_file}: {e}")
    if rows:
        df = pd.DataFrame(rows)
        processed_dir.mkdir(parents=True, exist_ok=True)
        output_path = processed_dir / "outcomes.csv"
        df.to_csv(output_path, index=False)
        print(f"Extracted {len(rows)} runs -> {output_path}")
        return 0

    print("No runs found to extract")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
