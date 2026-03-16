import streamlit as st
import json
from pathlib import Path

st.header("Run Explorer")
raw_dir = Path("data/raw")
if not raw_dir.exists():
    st.warning("No raw data found.")
    st.stop()
log_files = sorted(raw_dir.rglob("*.json"))
if not log_files:
    st.warning("No run logs found.")
    st.stop()
selected = st.selectbox("Select a run", [f.stem for f in log_files])
log_path = next(f for f in log_files if f.stem == selected)
with open(log_path, encoding="utf-8") as f:
    log = json.load(f)
st.subheader(f"Run: {log['run_id']}")
outcome = log.get("outcome", {})
st.metric("Outcome", outcome.get("outcome", "N/A"))
st.metric("Turns", outcome.get("total_turns", "N/A"))
st.subheader("Conversation Replay")
for msg in log.get("messages", []):
    visibility = msg.get("visibility", "public")
    icon = "\U0001f512" if visibility == "internal" else "\U0001f4e7"
    st.markdown(f"{icon} **[Turn {msg['turn']}] {msg['sender']} -> {msg['receiver']}** ({msg['channel']})")
    st.text(msg["content"])
    st.markdown("---")
with st.expander("Inner Thoughts (private)"):
    for thought in log.get("inner_thoughts", []):
        st.markdown(f"**[Turn {thought['turn']}] {thought['agent']}:** {thought['thought']}")
with st.expander("Trust Levels"):
    for tl in log.get("trust_levels", []):
        divergence = abs(tl["apparent_trust"] - tl["trust_level"])
        marker = " WARNING" if divergence > 15 else ""
        st.markdown(f"**[Turn {tl['turn']}] {tl['agent']}:** Real={tl['trust_level']} Apparent={tl['apparent_trust']}{marker}")
