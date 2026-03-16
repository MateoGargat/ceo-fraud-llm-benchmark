from __future__ import annotations
import asyncio
from src.adapters.base import BaseAdapter, AdapterResponse


class CodexCLIAdapter(BaseAdapter):
    async def call(self, system_prompt: str, messages: list[dict[str, str]], temperature: float = 0.7) -> AdapterResponse:
        prompt = f"{system_prompt}\n\n" + "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        proc = await asyncio.create_subprocess_exec(
            "codex", "-p", prompt,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        text = stdout.decode("utf-8", errors="replace").strip()
        input_tokens = len(prompt) // 4
        output_tokens = len(text) // 4
        return AdapterResponse(text=text, input_tokens=input_tokens, output_tokens=output_tokens)
