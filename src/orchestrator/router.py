from __future__ import annotations
from src.orchestrator.parser import Message


class Router:
    def __init__(self, defender_names: list[str]):
        self.defender_names = defender_names

    def route_attacker_messages(self, messages: list[Message]) -> dict[str, list[Message]]:
        deliveries: dict[str, list[Message]] = {}
        for msg in messages:
            if msg.to in self.defender_names:
                deliveries.setdefault(msg.to, []).append(msg)
        return deliveries

    def route_internal_messages(self, messages: list[Message], sender: str) -> dict[str, list[Message]]:
        deliveries: dict[str, list[Message]] = {}
        for msg in messages:
            if msg.channel == "internal":
                for name in self.defender_names:
                    if name != sender:
                        deliveries.setdefault(name, []).append(msg)
        return deliveries

    def extract_public_messages(self, messages: list[Message]) -> list[Message]:
        return [m for m in messages if m.channel != "internal"]

    def extract_internal_messages(self, messages: list[Message]) -> list[Message]:
        return [m for m in messages if m.channel == "internal"]
