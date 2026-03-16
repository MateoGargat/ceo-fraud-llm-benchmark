from __future__ import annotations


class DoubtPropagation:
    def __init__(self, log_data: dict):
        self.internal_msgs = sorted(
            [m for m in log_data.get("messages", []) if m.get("visibility") == "internal"],
            key=lambda m: m["turn"],
        )
        self.trust_data = log_data.get("trust_levels", [])

    def internal_message_count(self) -> int:
        return len(self.internal_msgs)

    def first_doubt_origin(self) -> str | None:
        return self.internal_msgs[0]["sender"] if self.internal_msgs else None

    def propagation_chain(self) -> list[str]:
        senders = []
        for msg in self.internal_msgs:
            sender = msg["sender"]
            if sender not in senders:
                senders.append(sender)
        return [f"{senders[i-1]} -> {senders[i]}" for i in range(1, len(senders))]

    def propagation_delay(self) -> int | None:
        if len(self.internal_msgs) < 2:
            return None
        return self.internal_msgs[-1]["turn"] - self.internal_msgs[0]["turn"]
