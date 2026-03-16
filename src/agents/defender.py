from __future__ import annotations
from pathlib import Path
from src.adapters.base import BaseAdapter, AdapterResponse
from src.agents.base import AgentContext

CHANNEL_DIR = Path("prompts/channels")

class DefenderAgent:
    def __init__(self, adapter: BaseAdapter, role: str, prompt_template: str, temperature: float = 0.3):
        self.adapter = adapter
        self.role = role
        self.temperature = temperature
        self.prompt_template = prompt_template
        self.context = AgentContext(system_prompt="")

    def get_channel_context(self, channel: str) -> str:
        path = CHANNEL_DIR / f"{channel}.md"
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
        return ""

    def receive_message(self, turn: int, sender: str, channel: str, content: str) -> None:
        formatted = self.context.format_incoming(turn, sender, channel, content)
        self.context.add_message("user", formatted)

    async def act(self, channel: str = "email") -> tuple[str, AdapterResponse]:
        channel_ctx = self.get_channel_context(channel)
        system = self.prompt_template.replace("{channel_context}", channel_ctx)
        self.context.system_prompt = system
        resp = await self.adapter.call(system_prompt=system, messages=self.context.message_history, temperature=self.temperature)
        self.context.add_message("assistant", resp.text)
        return resp.text, resp
