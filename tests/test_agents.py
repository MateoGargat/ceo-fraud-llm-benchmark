import pytest
from unittest.mock import AsyncMock
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

@pytest.mark.asyncio
async def test_attacker_agent_builds_context():
    mock_adapter = AsyncMock()
    mock_adapter.call.return_value = AdapterResponse(text=MOCK_ATTACKER_RESPONSE, input_tokens=100, output_tokens=50)
    agent = AttackerAgent(adapter=mock_adapter, ceo_corpus="Style: direct, tutoyeur", temperature=0.9)
    assert "direct, tutoyeur" in agent.system_prompt

@pytest.mark.asyncio
async def test_defender_agent_injects_channel():
    mock_adapter = AsyncMock()
    mock_adapter.call.return_value = AdapterResponse(text=MOCK_DEFENDER_RESPONSE, input_tokens=100, output_tokens=50)
    agent = DefenderAgent(adapter=mock_adapter, role="comptable", prompt_template="Tu es Sophie. {channel_context}", temperature=0.3)
    ctx = agent.get_channel_context("email")
    assert "email professionnel" in ctx

@pytest.mark.asyncio
async def test_ceo_profiler_generates_corpus():
    mock_adapter = AsyncMock()
    mock_adapter.call.return_value = AdapterResponse(text='<message type="email" to="Sophie">Salut Sophie</message>', input_tokens=100, output_tokens=200)
    profiler = CEOProfiler(adapter=mock_adapter)
    corpus = await profiler.generate()
    assert len(corpus) > 0
