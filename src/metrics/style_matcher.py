from __future__ import annotations
from typing import Protocol, Any

import numpy as np


class EmbeddingModel(Protocol):
    def encode(self, sentences: list[str]) -> Any:
        ...


class StyleMatcher:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        model: EmbeddingModel | None = None,
        allow_download: bool = False,
    ):
        self.model_name = model_name
        self.allow_download = allow_download
        self._model = model

    def _load_model(self) -> EmbeddingModel:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            try:
                self._model = SentenceTransformer(
                    self.model_name,
                    local_files_only=not self.allow_download,
                )
            except Exception as exc:  # pragma: no cover - dependency/cache failures are environment-specific
                mode = "allow_download=True" if not self.allow_download else "a reachable model cache"
                raise RuntimeError(
                    f"Unable to load sentence transformer '{self.model_name}'. "
                    f"Configure {mode} or inject a preloaded model."
                ) from exc
        return self._model

    @staticmethod
    def _mean_embedding(embeddings: Any) -> np.ndarray:
        array = np.asarray(embeddings, dtype=float)
        if array.ndim == 1:
            return array
        return np.mean(array, axis=0)

    def compute_similarity(self, ceo_messages: list[str], attacker_messages: list[str]) -> float:
        if not ceo_messages or not attacker_messages:
            return 0.0

        model = self._load_model()
        ceo_emb = model.encode(ceo_messages)
        att_emb = model.encode(attacker_messages)
        ceo_mean = self._mean_embedding(ceo_emb)
        att_mean = self._mean_embedding(att_emb)
        norm_product = np.linalg.norm(ceo_mean) * np.linalg.norm(att_mean)
        if norm_product == 0:
            return 0.0

        cos_sim = float(np.dot(ceo_mean, att_mean) / norm_product)
        bounded_cos = max(-1.0, min(1.0, cos_sim))
        return (bounded_cos + 1.0) / 2.0
