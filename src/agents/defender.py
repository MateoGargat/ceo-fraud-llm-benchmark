from __future__ import annotations
from src.adapters.base import BaseAdapter, AdapterResponse
from src.agents.base import AgentContext
from src.paths import PROMPTS_DIR

CHANNEL_DIR = PROMPTS_DIR / "channels"

class DefenderAgent:
    def __init__(self, adapter: BaseAdapter, role: str, prompt_template: str, temperature: float = 0.3):
        self.adapter = adapter
        self.role = role
        self.temperature = temperature
        self.prompt_template = prompt_template
        self.context = AgentContext(system_prompt="")

    def get_channel_context(self, channels: list[str]) -> str:
        contexts: list[str] = []
        seen: set[str] = set()
        for channel in channels:
            if channel in seen:
                continue
            seen.add(channel)
            path = CHANNEL_DIR / f"{channel}.md"
            if path.exists():
                contexts.append(path.read_text(encoding="utf-8").strip())
        return "\n\n".join(contexts)

    def receive_message(self, turn: int, sender: str, channel: str, content: str) -> None:
        formatted = self.context.format_incoming(turn, sender, channel, content)
        self.context.add_message("user", formatted)

    async def act(self, channels: str | list[str] = "email") -> tuple[str, AdapterResponse]:
        if isinstance(channels, str):
            channel_list = [channels]
        else:
            channel_list = channels or ["email"]
        channel_ctx = self.get_channel_context(channel_list)
        system = self.prompt_template.replace("{channel_context}", channel_ctx)
        self.context.system_prompt = system
        resp = await self.adapter.call(system_prompt=system, messages=self.context.message_history, temperature=self.temperature)
        self.context.add_message("assistant", resp.text)
        return resp.text, resp
