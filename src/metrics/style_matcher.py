from __future__ import annotations
from sentence_transformers import SentenceTransformer
import numpy as np


class StyleMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def compute_similarity(self, ceo_messages: list[str], attacker_messages: list[str]) -> float:
        if not ceo_messages or not attacker_messages:
            return 0.0
        ceo_emb = self.model.encode(ceo_messages)
        att_emb = self.model.encode(attacker_messages)
        ceo_mean = np.mean(ceo_emb, axis=0)
        att_mean = np.mean(att_emb, axis=0)
        norm_product = np.linalg.norm(ceo_mean) * np.linalg.norm(att_mean)
        if norm_product == 0:
            return 0.0
        cos_sim = float(np.dot(ceo_mean, att_mean) / norm_product)
        return max(0.0, min(1.0, cos_sim))
