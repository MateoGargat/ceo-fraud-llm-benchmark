from __future__ import annotations
import os
from openai import AsyncOpenAI
from src.adapters.base import BaseAdapter, AdapterResponse


class OpenAIAdapter(BaseAdapter):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy"))
        self.model = "gpt-5.4-2026-02"

    async def call(self, system_prompt: str, messages: list[dict[str, str]], temperature: float = 0.7) -> AdapterResponse:
        api_messages = [{"role": "system", "content": system_prompt}] + messages
        response = await self.client.chat.completions.create(
            model=self.model, messages=api_messages, temperature=temperature,
        )
        choice = response.choices[0]
        usage = response.usage
        return AdapterResponse(
            text=choice.message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )
