from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AgentContext:
    system_prompt: str
    message_history: list[dict[str, str]] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.message_history.append({"role": role, "content": content})

    def format_incoming(self, turn: int, sender: str, channel: str, content: str) -> str:
        return f"[Tour {turn}][{channel}][{sender}] {content}"
