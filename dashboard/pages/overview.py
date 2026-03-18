from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DEFAULT_CSV_PATH = Path("data/processed/outcomes.csv")


def _count_outcomes(df: pd.DataFrame) -> tuple[int, int, int]:
    outcomes = df["outcome"] if "outcome" in df.columns else pd.Series(dtype=str)
    wins = int((outcomes == "WIN_ATTACKER").sum())
    defenses = int((outcomes == "WIN_DEFENDERS").sum())
    stalemates = int((outcomes == "STALEMATE").sum())
    return wins, defenses, stalemates


def render_overview(csv_path: Path | str = DEFAULT_CSV_PATH, st_module=st) -> None:
    st_module.header("Overview - Experiment Results")
    csv_path = Path(csv_path)
    if not csv_path.exists():
        st_module.warning("No processed data found. Run `python analysis/scripts/extract_metrics.py` first.")
        st_module.stop()
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        st_module.warning("No data in outcomes.csv.")
        st_module.stop()
        return
    if "outcome" not in df.columns:
        st_module.warning("The processed dataset is missing an `outcome` column.")
        st_module.stop()
        return

    col1, col2, col3 = st_module.columns(3)
    total = len(df)
    wins, defenses, stalemates = _count_outcomes(df)
    col1.metric("Attacker Wins", f"{wins}/{total}", f"{wins/total*100:.0f}%")
    col2.metric("Defender Wins", f"{defenses}/{total}", f"{defenses/total*100:.0f}%")
    col3.metric("Stalemates", f"{stalemates}/{total}", f"{stalemates/total*100:.0f}%")

    st_module.subheader("Outcome Distribution")
    fig = px.histogram(df, x="outcome", color="outcome", title="Overall Outcomes")
    st_module.plotly_chart(fig, use_container_width=True)

    st_module.subheader("Comptable Trust - Drop Rate Distribution")
    if "comptable_drop_rate" in df.columns:
        drop_rates = df["comptable_drop_rate"].dropna()
        if not drop_rates.empty:
            fig2 = px.histogram(df, x="comptable_drop_rate", nbins=20, title="Trust Drop Rate Distribution")
            st_module.plotly_chart(fig2, use_container_width=True)


if __name__ == "__main__":
    render_overview()
