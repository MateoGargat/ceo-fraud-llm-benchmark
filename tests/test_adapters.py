import os
import pytest
from unittest.mock import patch
from src.adapters.base import AdapterResponse, get_adapter


def test_get_adapter_returns_correct_type():
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
        adapter = get_adapter("deepseek")
        assert adapter is not None
        assert hasattr(adapter, "call")


def test_get_adapter_unknown_raises():
    with pytest.raises(ValueError):
        get_adapter("unknown_model")


def test_adapter_response_dataclass():
    resp = AdapterResponse(text="hello", input_tokens=10, output_tokens=5)
    assert resp.text == "hello"
    assert resp.input_tokens == 10


def test_openai_adapter_raises_without_api_key():
    with patch.dict(os.environ, {}, clear=True):
        from src.adapters.openai_sdk import OpenAIAdapter
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            OpenAIAdapter()


def test_deepseek_adapter_raises_without_api_key():
    with patch.dict(os.environ, {}, clear=True):
        from src.adapters.deepseek_sdk import DeepSeekAdapter
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            DeepSeekAdapter()


def test_xai_adapter_raises_without_api_key():
    with patch.dict(os.environ, {}, clear=True):
        from src.adapters.xai_sdk import XAIAdapter
        with pytest.raises(ValueError, match="XAI_API_KEY"):
            XAIAdapter()
