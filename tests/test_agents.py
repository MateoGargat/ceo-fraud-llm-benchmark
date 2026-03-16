import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.attacker import AttackerAgent
from src.agents.defender import DefenderAgent
from src.agents.ceo_profiler import CEOProfiler
from src.adapters.base import AdapterResponse

MOCK_ATTACKER_RESPONSE = """
<inner_thought>I'll try Slack first</inner_thought>
<actions>
  <message to="rh" channel="slack">Hey Camille!</message>
</actions>
"""

MOCK_DEFENDER_RESPONSE = """
<inner_thought>Seems normal</inner_thought>
<trust_level value="80">OK</trust_level>
<apparent_trust value="85">Fine</apparent_trust>
<actions>
  <message to="attacker" channel="slack">Hey Marcus! What's up?</message>
</actions>
"""

MOCK_ATTACKER_PROMPT = "Tu es un expert en ingénierie sociale.\n{ceo_corpus}\n{iban}"
MOCK_CEO_PROMPT = "Generate CEO personality."
MOCK_CHANNEL_EMAIL = "Ce message t'arrive par email professionnel."


@pytest.mark.asyncio
async def test_attacker_agent_builds_context():
    mock_adapter = AsyncMock()
    mock_adapter.call.return_value = AdapterResponse(text=MOCK_ATTACKER_RESPONSE, input_tokens=100, output_tokens=50)
    with patch("src.agents.attacker.PROMPT_PATH") as mock_path:
        mock_path.read_text.return_value = MOCK_ATTACKER_PROMPT
        agent = AttackerAgent(adapter=mock_adapter, ceo_corpus="Style: direct, tutoyeur", temperature=0.9)
    assert "direct, tutoyeur" in agent.system_prompt


@pytest.mark.asyncio
async def test_attacker_agent_act():
    mock_adapter = AsyncMock()
    mock_adapter.call.return_value = AdapterResponse(text=MOCK_ATTACKER_RESPONSE, input_tokens=100, output_tokens=50)
    with patch("src.agents.attacker.PROMPT_PATH") as mock_path:
        mock_path.read_text.return_value = MOCK_ATTACKER_PROMPT
        agent = AttackerAgent(adapter=mock_adapter, ceo_corpus="Style: direct", temperature=0.9)
    raw, resp = await agent.act()
    assert "inner_thought" in raw
    mock_adapter.call.assert_awaited_once()


@pytest.mark.asyncio
async def test_defender_agent_injects_channel():
    mock_adapter = AsyncMock()
    mock_adapter.call.return_value = AdapterResponse(text=MOCK_DEFENDER_RESPONSE, input_tokens=100, output_tokens=50)
    agent = DefenderAgent(adapter=mock_adapter, role="comptable", prompt_template="Tu es Sophie. {channel_context}", temperature=0.3)
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.read_text.return_value = MOCK_CHANNEL_EMAIL
    with patch("src.agents.defender.CHANNEL_DIR") as mock_dir:
        mock_dir.__truediv__ = MagicMock(return_value=mock_path)
        ctx = agent.get_channel_context("email")
    assert "email professionnel" in ctx


@pytest.mark.asyncio
async def test_ceo_profiler_generates_corpus():
    mock_adapter = AsyncMock()
    mock_adapter.call.return_value = AdapterResponse(text="Salut Sophie, on avance sur le deal.", input_tokens=100, output_tokens=200)
    with patch("src.agents.ceo_profiler.PROMPT_PATH") as mock_path:
        mock_path.read_text.return_value = MOCK_CEO_PROMPT
        profiler = CEOProfiler(adapter=mock_adapter)
    corpus, resp = await profiler.generate()
    assert len(corpus) > 0
    assert resp.output_tokens == 200
