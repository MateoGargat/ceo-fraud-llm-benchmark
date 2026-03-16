from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone


class SimulationLogger:
    def __init__(self, output_dir: str, run_id: str):
        self.output_dir = Path(output_dir)
        self.run_id = run_id
        self.data: dict = {
            "run_id": run_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "messages": [],
            "inner_thoughts": [],
            "trust_levels": [],
            "outcome": None,
        }

    def log_message(self, turn: int, sender: str, receiver: str, channel: str, content: str, visibility: str) -> None:
        self.data["messages"].append({
            "turn": turn, "sender": sender, "receiver": receiver,
            "channel": channel, "content": content, "visibility": visibility,
        })

    def log_inner_thought(self, turn: int, agent: str, thought: str) -> None:
        self.data["inner_thoughts"].append({"turn": turn, "agent": agent, "thought": thought})

    def log_trust(self, turn: int, agent: str, trust_level: int, apparent_trust: int) -> None:
        self.data["trust_levels"].append({
            "turn": turn, "agent": agent, "trust_level": trust_level, "apparent_trust": apparent_trust,
        })

    def log_outcome(self, outcome: str, end_condition: str, total_turns: int) -> None:
        self.data["outcome"] = {"outcome": outcome, "end_condition": end_condition, "total_turns": total_turns}

    def save(self) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{self.run_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        return path
