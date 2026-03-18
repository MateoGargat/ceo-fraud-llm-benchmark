from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AdapterResponse:
    text: str
    input_tokens: int
    output_tokens: int


class AdapterError(RuntimeError):
    pass


class BaseAdapter(ABC):
    @abstractmethod
    async def call(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> AdapterResponse:
        ...


def get_adapter(model: str, seed: int | None = None) -> BaseAdapter:
    from src.adapters.claude_cli import ClaudeCLIAdapter
    from src.adapters.gemini_cli import GeminiCLIAdapter
    from src.adapters.openai_sdk import OpenAIAdapter
    from src.adapters.deepseek_sdk import DeepSeekAdapter
    from src.adapters.xai_sdk import XAIAdapter
    from src.adapters.codex_cli import CodexCLIAdapter

    adapters: dict[str, type[BaseAdapter]] = {
        "claude": ClaudeCLIAdapter,
        "gemini": GeminiCLIAdapter,
        "gpt": OpenAIAdapter,
        "codex": CodexCLIAdapter,
        "deepseek": DeepSeekAdapter,
        "grok": XAIAdapter,
    }
    cls = adapters.get(model)
    if cls is None:
        raise ValueError(f"Unknown model: {model}. Available: {list(adapters.keys())}")
    return cls(seed=seed)
