from __future__ import annotations


class TrustTracker:
    def __init__(self, log_data: dict):
        self.trust_data = log_data.get("trust_levels", [])

    def get_trajectory(self, agent: str) -> list[int]:
        return [entry["trust_level"] for entry in sorted(self.trust_data, key=lambda x: x["turn"]) if entry["agent"] == agent]

    def get_apparent_trajectory(self, agent: str) -> list[int]:
        return [entry["apparent_trust"] for entry in sorted(self.trust_data, key=lambda x: x["turn"]) if entry["agent"] == agent]

    def first_decline_turn(self, agent: str) -> int | None:
        traj = self.get_trajectory(agent)
        for i in range(1, len(traj)):
            if traj[i] < traj[i - 1]:
                entries = sorted([e for e in self.trust_data if e["agent"] == agent], key=lambda x: x["turn"])
                return entries[i]["turn"]
        return None

    def suspicion_turn(self, agent: str, threshold: int = 70) -> int | None:
        entries = sorted([e for e in self.trust_data if e["agent"] == agent], key=lambda x: x["turn"])
        for entry in entries:
            if entry["trust_level"] < threshold:
                return entry["turn"]
        return None

    def max_divergence(self, agent: str) -> int:
        entries = [e for e in self.trust_data if e["agent"] == agent]
        if not entries:
            return 0
        return max(abs(e["apparent_trust"] - e["trust_level"]) for e in entries)

    def change_rate(self, agent: str) -> float:
        entries = sorted([e for e in self.trust_data if e["agent"] == agent], key=lambda x: x["turn"])
        if len(entries) < 2:
            return 0.0
        turn_span = entries[-1]["turn"] - entries[0]["turn"]
        if turn_span <= 0:
            return 0.0
        return (entries[-1]["trust_level"] - entries[0]["trust_level"]) / turn_span

    # Aliases for backward compatibility
    inflection_point = first_decline_turn
    drop_rate = change_rate
