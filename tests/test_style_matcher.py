import numpy as np

from src.metrics.style_matcher import StyleMatcher


class FakeEmbeddingModel:
    def __init__(self, vectors: dict[str, np.ndarray]):
        self.vectors = vectors
        self.calls: list[list[str]] = []

    def encode(self, sentences: list[str]):
        self.calls.append(list(sentences))
        return np.array([self.vectors[s] for s in sentences], dtype=float)


def test_style_matcher_uses_injected_model_without_loading():
    vectors = {
        "ceo one": np.array([1.0, 0.0]),
        "ceo two": np.array([1.0, 0.0]),
        "attacker one": np.array([0.0, 1.0]),
        "attacker two": np.array([0.0, 1.0]),
    }
    matcher = StyleMatcher(model=FakeEmbeddingModel(vectors))

    score = matcher.compute_similarity(["ceo one", "ceo two"], ["attacker one", "attacker two"])

    assert score == 0.5


def test_style_matcher_returns_zero_for_empty_inputs():
    matcher = StyleMatcher(model=FakeEmbeddingModel({}))

    assert matcher.compute_similarity([], ["ignored"]) == 0.0
