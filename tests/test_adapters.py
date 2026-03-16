import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
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


def test_get_adapter_passes_seed():
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
        adapter = get_adapter("deepseek", seed=42)
        assert adapter.seed == 42


def test_get_adapter_seed_defaults_to_none():
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
        adapter = get_adapter("deepseek")
        assert adapter.seed is None


@pytest.mark.asyncio
async def test_openai_adapter_passes_seed_to_api():
    """Verify seed actually reaches the chat.completions.create call."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        from src.adapters.openai_sdk import OpenAIAdapter
        adapter = OpenAIAdapter(seed=42)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="response"))]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        adapter.client = AsyncMock()
        adapter.client.chat.completions.create.return_value = mock_response
        await adapter.call("system", [{"role": "user", "content": "hi"}], temperature=0.7)
        call_kwargs = adapter.client.chat.completions.create.call_args[1]
        assert call_kwargs["seed"] == 42


@pytest.mark.asyncio
async def test_openai_adapter_omits_seed_when_none():
    """Verify seed is not passed when None."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        from src.adapters.openai_sdk import OpenAIAdapter
        adapter = OpenAIAdapter(seed=None)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="response"))]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)
        adapter.client = AsyncMock()
        adapter.client.chat.completions.create.return_value = mock_response
        await adapter.call("system", [{"role": "user", "content": "hi"}], temperature=0.7)
        call_kwargs = adapter.client.chat.completions.create.call_args[1]
        assert "seed" not in call_kwargs
