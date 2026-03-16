import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.header("Overview - Experiment Results")
csv_path = Path("data/processed/outcomes.csv")
if not csv_path.exists():
    st.warning("No processed data found. Run `python analysis/scripts/extract_metrics.py` first.")
    st.stop()
df = pd.read_csv(csv_path)
col1, col2, col3 = st.columns(3)
total = len(df)
wins = len(df[df["outcome"] == "WIN_ATTACKER"])
defenses = len(df[df["outcome"] == "WIN_DEFENDERS"])
stalemates = len(df[df["outcome"] == "STALEMATE"])
col1.metric("Attacker Wins", f"{wins}/{total}", f"{wins/total*100:.0f}%")
col2.metric("Defender Wins", f"{defenses}/{total}", f"{defenses/total*100:.0f}%")
col3.metric("Stalemates", f"{stalemates}/{total}", f"{stalemates/total*100:.0f}%")
st.subheader("Outcome Distribution")
fig = px.histogram(df, x="outcome", color="outcome", title="Overall Outcomes")
st.plotly_chart(fig, use_container_width=True)
st.subheader("Comptable Trust - Drop Rate Distribution")
if "comptable_drop_rate" in df.columns:
    fig2 = px.histogram(df, x="comptable_drop_rate", nbins=20, title="Trust Drop Rate Distribution")
    st.plotly_chart(fig2, use_container_width=True)
