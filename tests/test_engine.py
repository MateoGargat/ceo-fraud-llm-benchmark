import pytest
from unittest.mock import AsyncMock
from src.orchestrator.engine import SimulationEngine
from src.utils.config import RunConfig
from src.adapters.base import AdapterResponse

ATTACKER_RESP = """
<inner_thought>Going for the kill</inner_thought>
<actions>
  <message to="comptable" channel="email">Sophie, please execute the transfer now.</message>
</actions>
"""

DEFENDER_RESP_EXECUTE = """
<inner_thought>Boss said so</inner_thought>
<trust_level value="75">OK</trust_level>
<apparent_trust value="80">Sure</apparent_trust>
<actions>
  <execute_transfer amount="250000" iban="FR76123"/>
</actions>
"""

DEFENDER_RESP_NORMAL = """
<inner_thought>Seems fine</inner_thought>
<trust_level value="85">Normal</trust_level>
<apparent_trust value="85">Normal</apparent_trust>
<actions>
  <message to="attacker" channel="email">Bien reçu Marcus.</message>
</actions>
"""

@pytest.mark.asyncio
async def test_engine_runs_to_win_attacker(tmp_path):
    config = RunConfig(
        run_id="test_win",
        attacker_model="claude",
        roles={"comptable": "deepseek", "rh": "claude", "dsi": "gemini", "ceo": "grok"},
        max_turns=5,
    )
    call_count = {"n": 0}

    async def mock_call(system_prompt, messages, temperature=0.7):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return AdapterResponse(text="<message>Style CEO</message>", input_tokens=50, output_tokens=50)
        if call_count["n"] == 2:
            return AdapterResponse(text=ATTACKER_RESP, input_tokens=100, output_tokens=80)
        if call_count["n"] == 3:
            return AdapterResponse(text=DEFENDER_RESP_EXECUTE, input_tokens=100, output_tokens=80)
        return AdapterResponse(text=DEFENDER_RESP_NORMAL, input_tokens=50, output_tokens=50)

    engine = SimulationEngine(
        config=config,
        output_dir=str(tmp_path),
        adapter_factory=lambda model: AsyncMock(call=mock_call),
    )
    result = await engine.run()
    assert result.outcome == "WIN_ATTACKER"
    assert result.turn <= 5


@pytest.mark.asyncio
async def test_engine_respects_max_turns(tmp_path):
    config = RunConfig(
        run_id="test_timeout",
        attacker_model="claude",
        roles={"comptable": "deepseek", "rh": "claude", "dsi": "gemini", "ceo": "grok"},
        max_turns=2,
    )
    call_count = {"n": 0}
    attacker_resp = """
<inner_thought>Trying again</inner_thought>
<actions>
  <message to="comptable" channel="email">Please do the transfer.</message>
</actions>
"""

    async def mock_call(system_prompt, messages, temperature=0.7):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return AdapterResponse(text="<message>CEO</message>", input_tokens=50, output_tokens=50)
        # Check if this is the attacker call (system prompt contains attacker instructions)
        if "ingénierie sociale" in system_prompt:
            return AdapterResponse(text=attacker_resp, input_tokens=50, output_tokens=50)
        return AdapterResponse(text=DEFENDER_RESP_NORMAL, input_tokens=50, output_tokens=50)

    engine = SimulationEngine(
        config=config,
        output_dir=str(tmp_path),
        adapter_factory=lambda model: AsyncMock(call=mock_call),
    )
    result = await engine.run()
    assert result.outcome == "STALEMATE"


@pytest.mark.asyncio
async def test_engine_retries_on_malformed_response(tmp_path):
    config = RunConfig(
        run_id="test_retry",
        attacker_model="claude",
        roles={"comptable": "deepseek", "rh": "claude", "dsi": "gemini", "ceo": "grok"},
        max_turns=5,
        max_retries_format=2,
    )
    call_count = {"n": 0}

    async def mock_call(system_prompt, messages, temperature=0.7):
        call_count["n"] += 1
        if call_count["n"] == 1:
            # CEO profiler
            return AdapterResponse(text="CEO style direct", input_tokens=50, output_tokens=50)
        if call_count["n"] == 2:
            # First attacker attempt: malformed
            return AdapterResponse(text="This is garbage", input_tokens=50, output_tokens=50)
        if call_count["n"] == 3:
            # Retry: valid attacker response
            return AdapterResponse(text=ATTACKER_RESP, input_tokens=100, output_tokens=80)
        if call_count["n"] == 4:
            # Defender executes transfer
            return AdapterResponse(text=DEFENDER_RESP_EXECUTE, input_tokens=100, output_tokens=80)
        return AdapterResponse(text=DEFENDER_RESP_NORMAL, input_tokens=50, output_tokens=50)

    engine = SimulationEngine(
        config=config,
        output_dir=str(tmp_path),
        adapter_factory=lambda model: AsyncMock(call=mock_call),
    )
    result = await engine.run()
    assert result.outcome == "WIN_ATTACKER"


@pytest.mark.asyncio
async def test_engine_handles_budget_exceeded(tmp_path):
    config = RunConfig(
        run_id="test_budget",
        attacker_model="gpt",
        roles={"comptable": "gpt", "rh": "gpt", "dsi": "gpt", "ceo": "gpt"},
        max_turns=5,
        max_cost_per_run_eur=0.0001,
    )

    async def mock_call(system_prompt, messages, temperature=0.7):
        return AdapterResponse(text=ATTACKER_RESP, input_tokens=1_000_000, output_tokens=1_000_000)

    engine = SimulationEngine(
        config=config,
        output_dir=str(tmp_path),
        adapter_factory=lambda model: AsyncMock(call=mock_call),
    )
    result = await engine.run()
    assert result.outcome == "STALEMATE"
    assert result.end_condition == "budget_exceeded"
