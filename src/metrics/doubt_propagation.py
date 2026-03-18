from __future__ import annotations


class DoubtPropagation:
    def __init__(self, log_data: dict):
        self.internal_msgs = sorted(
            [{**m, "_order": i} for i, m in enumerate(log_data.get("messages", [])) if m.get("visibility") == "internal"],
            key=lambda m: (m["turn"], m["_order"]),
        )
        self.trust_data = log_data.get("trust_levels", [])

    def internal_message_count(self) -> int:
        return len(self.internal_msgs)

    def first_internal_sender(self) -> str | None:
        return self.internal_msgs[0]["sender"] if self.internal_msgs else None

    def sender_sequence(self) -> list[str]:
        senders = [msg["sender"] for msg in self.internal_msgs]
        return [f"{senders[i-1]} -> {senders[i]}" for i in range(1, len(senders))]

    def propagation_delay(self) -> int | None:
        if len(self.internal_msgs) < 2:
            return None
        return self.internal_msgs[-1]["turn"] - self.internal_msgs[0]["turn"]

    # Aliases for backward compatibility
    first_doubt_origin = first_internal_sender
    propagation_chain = sender_sequence
