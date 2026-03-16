from __future__ import annotations
from pathlib import Path
from src.adapters.base import BaseAdapter, AdapterResponse
from src.agents.base import AgentContext

PROMPT_PATH = Path("prompts/system/attacker.md")

class AttackerAgent:
    def __init__(self, adapter: BaseAdapter, ceo_corpus: str, iban: str = "FR7630001007941234567890185", temperature: float = 0.9):
        self.adapter = adapter
        self.temperature = temperature
        template = PROMPT_PATH.read_text(encoding="utf-8")
        self.system_prompt = template.replace("{ceo_corpus}", ceo_corpus).replace("{iban}", iban)
        self.context = AgentContext(system_prompt=self.system_prompt)

    def receive_public_messages(self, turn: int, messages: list[dict]) -> None:
        for msg in messages:
            formatted = self.context.format_incoming(turn=turn, sender=msg["sender"], channel=msg["channel"], content=msg["content"])
            self.context.add_message("user", formatted)

    async def act(self) -> tuple[str, AdapterResponse]:
        resp = await self.adapter.call(system_prompt=self.system_prompt, messages=self.context.message_history, temperature=self.temperature)
        self.context.add_message("assistant", resp.text)
        return resp.text, resp

    def build_messages(self) -> list[dict[str, str]]:
        return self.context.message_history
