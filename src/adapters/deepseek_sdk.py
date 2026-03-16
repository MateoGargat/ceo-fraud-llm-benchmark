from __future__ import annotations
import os
from openai import AsyncOpenAI
from src.adapters.base import BaseAdapter, AdapterResponse


class DeepSeekAdapter(BaseAdapter):
    def __init__(self, seed: int | None = None):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is required")
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        self.model = "deepseek-chat"
        self.seed = seed

    async def call(self, system_prompt: str, messages: list[dict[str, str]], temperature: float = 0.7) -> AdapterResponse:
        api_messages = [{"role": "system", "content": system_prompt}] + messages
        kwargs = {"model": self.model, "messages": api_messages, "temperature": temperature}
        if self.seed is not None:
            kwargs["seed"] = self.seed
        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        usage = response.usage
        return AdapterResponse(
            text=choice.message.content or "",
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )
