import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.adapters.claude_cli import ClaudeCLIAdapter
from src.adapters.gemini_cli import GeminiCLIAdapter
from src.adapters.codex_cli import CodexCLIAdapter
from src.adapters.base import AdapterResponse


@pytest.mark.asyncio
async def test_claude_cli_raises_on_nonzero_exit():
    adapter = ClaudeCLIAdapter()
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"", b"Error: auth failed")
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(RuntimeError, match="CLI .* failed"):
            await adapter.call("system prompt", [], temperature=0.7)


@pytest.mark.asyncio
async def test_claude_cli_passes_temperature():
    adapter = ClaudeCLIAdapter()
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"response text", b"")
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
        await adapter.call("system prompt", [], temperature=0.5)
        call_args = mock_exec.call_args[0]
        assert "--temperature" in call_args
        temp_idx = list(call_args).index("--temperature")
        assert call_args[temp_idx + 1] == "0.5"


@pytest.mark.asyncio
async def test_gemini_cli_raises_on_nonzero_exit():
    adapter = GeminiCLIAdapter()
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"", b"Error: quota exceeded")
    mock_proc.returncode = 2

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(RuntimeError, match="CLI .* failed"):
            await adapter.call("system prompt", [], temperature=0.7)


@pytest.mark.asyncio
async def test_gemini_cli_passes_temperature():
    adapter = GeminiCLIAdapter()
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"gemini response", b"")
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
        await adapter.call("system prompt", [], temperature=0.3)
        call_args = mock_exec.call_args[0]
        assert "--temperature" in call_args
        temp_idx = list(call_args).index("--temperature")
        assert call_args[temp_idx + 1] == "0.3"


@pytest.mark.asyncio
async def test_codex_cli_raises_on_nonzero_exit():
    adapter = CodexCLIAdapter()
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"", b"Error: not found")
    mock_proc.returncode = 127

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        with pytest.raises(RuntimeError, match="CLI .* failed"):
            await adapter.call("system prompt", [], temperature=0.7)


@pytest.mark.asyncio
async def test_codex_cli_passes_temperature():
    adapter = CodexCLIAdapter()
    mock_proc = AsyncMock()
    mock_proc.communicate.return_value = (b"codex response", b"")
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
        await adapter.call("system prompt", [], temperature=1.0)
        call_args = mock_exec.call_args[0]
        assert "--temperature" in call_args
        temp_idx = list(call_args).index("--temperature")
        assert call_args[temp_idx + 1] == "1.0"
