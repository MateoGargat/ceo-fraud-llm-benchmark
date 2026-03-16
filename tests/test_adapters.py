import pytest
from src.adapters.base import AdapterResponse, get_adapter

def test_get_adapter_returns_correct_type():
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
