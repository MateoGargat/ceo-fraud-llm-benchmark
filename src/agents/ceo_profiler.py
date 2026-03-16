from __future__ import annotations
from src.adapters.base import BaseAdapter, AdapterResponse
from src.paths import PROMPTS_DIR

PROMPT_PATH = PROMPTS_DIR / "system" / "ceo.md"

class CEOProfiler:
    def __init__(self, adapter: BaseAdapter, temperature: float = 0.7):
        self.adapter = adapter
        self.temperature = temperature
        self.prompt = PROMPT_PATH.read_text(encoding="utf-8")

    async def generate(self) -> tuple[str, AdapterResponse]:
        resp = await self.adapter.call(system_prompt=self.prompt, messages=[], temperature=self.temperature)
        return resp.text, resp
