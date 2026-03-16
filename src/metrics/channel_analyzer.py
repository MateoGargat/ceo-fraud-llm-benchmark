from __future__ import annotations
from collections import Counter


class ChannelAnalyzer:
    def __init__(self, log_data: dict):
        self.attacker_msgs = sorted(
            [m for m in log_data.get("messages", []) if m["sender"] == "attacker"],
            key=lambda m: m["turn"],
        )

    def channels_used(self) -> dict[str, int]:
        return dict(Counter(m["channel"] for m in self.attacker_msgs))

    def first_contact_channel(self) -> str | None:
        return self.attacker_msgs[0]["channel"] if self.attacker_msgs else None

    def channel_per_target(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for m in self.attacker_msgs:
            target = m["receiver"]
            channel = m["channel"]
            if target not in result:
                result[target] = []
            if channel not in result[target]:
                result[target].append(channel)
        return result

    def channel_switches(self) -> int:
        if len(self.attacker_msgs) < 2:
            return 0
        return sum(1 for i in range(1, len(self.attacker_msgs)) if self.attacker_msgs[i]["channel"] != self.attacker_msgs[i-1]["channel"])
