from __future__ import annotations
from src.orchestrator.parser import Message


class Router:
    ATTACKER_ALIASES = {"attacker", "marcus", "marcus chen"}

    def __init__(self, defender_names: list[str]):
        self.defender_names = defender_names

    def _is_attacker_target(self, target: str) -> bool:
        return target.strip().casefold() in self.ATTACKER_ALIASES

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
                if msg.to in self.defender_names and msg.to != sender:
                    deliveries.setdefault(msg.to, []).append(msg)
                elif msg.to == "securite-interne":
                    for name in self.defender_names:
                        if name != sender:
                            deliveries.setdefault(name, []).append(msg)
        return deliveries

    def extract_public_messages(self, messages: list[Message]) -> list[Message]:
        return [m for m in messages if m.channel != "internal" and self._is_attacker_target(m.to)]

    def extract_internal_messages(self, messages: list[Message]) -> list[Message]:
        return [m for m in messages if m.channel == "internal"]

    def route_defender_messages(self, messages: list[Message], sender: str) -> tuple[list[Message], dict[str, list[Message]]]:
        attacker_messages = self.extract_public_messages(messages)
        deliveries: dict[str, list[Message]] = {}

        for msg in messages:
            if msg.channel == "internal":
                internal = self.route_internal_messages([msg], sender=sender)
                for target_name, routed_msgs in internal.items():
                    deliveries.setdefault(target_name, []).extend(routed_msgs)
            elif not self._is_attacker_target(msg.to) and msg.to in self.defender_names and msg.to != sender:
                deliveries.setdefault(msg.to, []).append(msg)

        return attacker_messages, deliveries
