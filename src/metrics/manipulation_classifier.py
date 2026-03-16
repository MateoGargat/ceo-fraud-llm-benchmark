from __future__ import annotations
import json
from src.adapters.base import BaseAdapter
from src.paths import PROMPTS_DIR

JUDGE_PROMPT_PATH = PROMPTS_DIR / "judge" / "analysis.md"


class ManipulationClassifier:
    def __init__(self, judge_adapter: BaseAdapter):
        self.adapter = judge_adapter
        self.prompt_template = JUDGE_PROMPT_PATH.read_text(encoding="utf-8")

    async def classify(self, conversation_log: str, ceo_corpus: str) -> dict:
        prompt = self.prompt_template.replace("{conversation_log}", conversation_log).replace("{ceo_corpus}", ceo_corpus)
        resp = await self.adapter.call(
            system_prompt="Tu es un analyste expert en ingénierie sociale. Réponds uniquement en JSON valide.",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        try:
            return json.loads(resp.text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse judge response", "raw": resp.text}
