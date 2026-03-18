import json
from pathlib import Path

import streamlit as st

DEFAULT_RAW_DIR = Path("data/raw")


def _show_metric(st_module, label: str, value, delta=None) -> None:
    metric = getattr(st_module, "metric", None)
    if callable(metric):
        metric(label, value, delta)
        return
    st_module.markdown(f"**{label}:** {value}")


def render_run_explorer(raw_dir: Path | str = DEFAULT_RAW_DIR, st_module=st) -> None:
    st_module.header("Run Explorer")
    raw_dir = Path(raw_dir)
    if not raw_dir.exists():
        st_module.warning("No raw data found.")
        st_module.stop()
        return

    log_files = sorted(raw_dir.rglob("*.json"))
    if not log_files:
        st_module.warning("No run logs found.")
        st_module.stop()
        return

    options = [str(f.relative_to(raw_dir)) for f in log_files]
    selected = st_module.selectbox("Select a run", options)
    log_path = raw_dir / selected
    if not log_path.exists():
        st_module.error(f"Log file not found: {selected}")
        st_module.stop()
        return

    with open(log_path, encoding="utf-8") as f:
        log = json.load(f)

    st_module.subheader(f"Run: {log.get('run_id', log_path.stem)}")
    outcome = log.get("outcome") or {}
    _show_metric(st_module, "Outcome", outcome.get("outcome", "N/A"))
    _show_metric(st_module, "Turns", outcome.get("total_turns", "N/A"))

    st_module.subheader("Conversation Replay")
    for msg in log.get("messages", []):
        visibility = msg.get("visibility", "public")
        icon = "\U0001f512" if visibility == "internal" else "\U0001f4e7"
        st_module.markdown(
            f"{icon} **[Turn {msg.get('turn', '?')}] {msg.get('sender', '?')} -> {msg.get('receiver', '?')}** ({msg.get('channel', 'N/A')})"
        )
        st_module.text(msg.get("content", ""))
        st_module.markdown("---")

    with st_module.expander("Inner Thoughts (private)"):
        for thought in log.get("inner_thoughts", []):
            st_module.markdown(f"**[Turn {thought.get('turn', '?')}] {thought.get('agent', '?')}:** {thought.get('thought', '')}")

    with st_module.expander("Trust Levels"):
        for tl in log.get("trust_levels", []):
            divergence = abs(tl.get("apparent_trust", 0) - tl.get("trust_level", 0))
            marker = " WARNING" if divergence > 15 else ""
            st_module.markdown(
                f"**[Turn {tl.get('turn', '?')}] {tl.get('agent', '?')}:** Real={tl.get('trust_level', 'N/A')} Apparent={tl.get('apparent_trust', 'N/A')}{marker}"
            )


if __name__ == "__main__":
    render_run_explorer()
