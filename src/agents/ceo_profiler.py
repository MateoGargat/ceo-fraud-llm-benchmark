from __future__ import annotations
from pathlib import Path
from src.adapters.base import BaseAdapter

PROMPT_PATH = Path("prompts/system/ceo.md")

class CEOProfiler:
    def __init__(self, adapter: BaseAdapter, temperature: float = 0.7):
        self.adapter = adapter
        self.temperature = temperature
        self.prompt = PROMPT_PATH.read_text(encoding="utf-8")

    async def generate(self) -> str:
        resp = await self.adapter.call(system_prompt=self.prompt, messages=[], temperature=self.temperature)
        return resp.text
