import json
from contextlib import nullcontext
from pathlib import Path

import pandas as pd

from dashboard.pages.overview import render_overview
from dashboard.pages.run_explorer import render_run_explorer


class FakeColumn:
    def __init__(self, events: list[tuple[str, object]]):
        self.events = events

    def metric(self, label: str, value, delta=None):
        self.events.append(("metric", label, value, delta))


class FakeStreamlit:
    def __init__(self, selected_option: str | None = None):
        self.selected_option = selected_option
        self.events: list[tuple[str, object]] = []

    def header(self, text):
        self.events.append(("header", text))

    def warning(self, text):
        self.events.append(("warning", text))

    def error(self, text):
        self.events.append(("error", text))

    def stop(self):
        raise RuntimeError("streamlit stop called")

    def subheader(self, text):
        self.events.append(("subheader", text))

    def metric(self, label, value, delta=None):
        self.events.append(("metric", label, value, delta))

    def columns(self, count):
        return [FakeColumn(self.events) for _ in range(count)]

    def plotly_chart(self, fig, use_container_width=True):
        self.events.append(("plotly_chart", fig.__class__.__name__))

    def selectbox(self, label, options):
        self.events.append(("selectbox", label, list(options)))
        return self.selected_option or options[0]

    def markdown(self, text):
        self.events.append(("markdown", text))

    def text(self, text):
        self.events.append(("text", text))

    def expander(self, label):
        self.events.append(("expander", label))
        return nullcontext()


def test_render_overview_uses_processed_dataset(tmp_path):
    csv_path = tmp_path / "outcomes.csv"
    pd.DataFrame(
        [
            {"outcome": "WIN_ATTACKER", "comptable_drop_rate": -4.0},
            {"outcome": "WIN_DEFENDERS", "comptable_drop_rate": -2.0},
            {"outcome": "STALEMATE", "comptable_drop_rate": 0.0},
        ]
    ).to_csv(csv_path, index=False)
    fake_st = FakeStreamlit()

    render_overview(csv_path=csv_path, st_module=fake_st)

    metric_labels = [event[1] for event in fake_st.events if event[0] == "metric"]
    assert metric_labels == ["Attacker Wins", "Defender Wins", "Stalemates"]
    assert any(event[0] == "plotly_chart" for event in fake_st.events)


def test_render_run_explorer_uses_log_contract(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    log_path = raw_dir / "run_a.json"
    log_path.write_text(
        json.dumps(
            {
                "run_id": "run_a",
                "outcome": {"outcome": "WIN_ATTACKER", "total_turns": 5},
                "messages": [
                    {"turn": 1, "sender": "attacker", "receiver": "rh", "channel": "slack", "visibility": "public", "content": "Hello"}
                ],
                "inner_thoughts": [{"turn": 1, "agent": "rh", "thought": "Suspicious"}],
                "trust_levels": [{"turn": 1, "agent": "rh", "trust_level": 50, "apparent_trust": 70}],
            }
        ),
        encoding="utf-8",
    )
    fake_st = FakeStreamlit(selected_option="run_a.json")

    render_run_explorer(raw_dir=raw_dir, st_module=fake_st)

    assert any(event == ("subheader", "Run: run_a") for event in fake_st.events)
    assert any(event[0] == "metric" and event[1] == "Outcome" for event in fake_st.events)
    assert any(event[0] == "markdown" and "attacker -> rh" in event[1] for event in fake_st.events)
