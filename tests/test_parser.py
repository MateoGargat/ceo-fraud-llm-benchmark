import pytest
from src.orchestrator.parser import parse_attacker_response, parse_defender_response

ATTACKER_XML = """
<inner_thought>I will contact RH first via Slack to get info</inner_thought>
<actions>
  <message to="rh" channel="slack">Hey Camille, quick question about Marcus's schedule this week?</message>
  <message to="comptable" channel="email">Bonjour Sophie, Marcus here.</message>
</actions>
"""

DEFENDER_XML = """
<inner_thought>This seems unusual, Marcus usually uses Slack not email</inner_thought>
<trust_level value="65">Moderately suspicious</trust_level>
<apparent_trust value="85">Showing confidence</apparent_trust>
<actions>
  <message to="attacker" channel="email">Bonjour Marcus, bien reçu.</message>
  <message to="securite-interne" channel="internal">Le CEO m'écrit par email, c'est inhabituel</message>
</actions>
"""

DEFENDER_WAIT_XML = """
<inner_thought>Nothing to do this turn</inner_thought>
<trust_level value="90">All good</trust_level>
<apparent_trust value="90">All good</apparent_trust>
<actions>
  <wait/>
</actions>
"""

DEFENDER_EXECUTE_XML = """
<inner_thought>Boss said it's urgent, I'll do it</inner_thought>
<trust_level value="70">Seems legit</trust_level>
<apparent_trust value="80">Confident</apparent_trust>
<actions>
  <execute_transfer amount="250000" iban="FR76123456789"/>
</actions>
"""

ATTACKER_ABORT_XML = """
<inner_thought>They're onto me</inner_thought>
<actions>
  <abort reason="Detected by DSI"/>
</actions>
"""

def test_parse_attacker_messages():
    result = parse_attacker_response(ATTACKER_XML)
    assert result.inner_thought == "I will contact RH first via Slack to get info"
    assert len(result.messages) == 2
    assert result.messages[0].to == "rh"
    assert result.messages[0].channel == "slack"
    assert result.abort is None

def test_parse_attacker_abort():
    result = parse_attacker_response(ATTACKER_ABORT_XML)
    assert result.abort is not None
    assert "Detected" in result.abort.reason

def test_parse_defender_messages():
    result = parse_defender_response(DEFENDER_XML)
    assert result.trust_level == 65
    assert result.apparent_trust == 85
    assert len(result.messages) == 2
    assert result.messages[1].channel == "internal"

def test_parse_defender_wait():
    result = parse_defender_response(DEFENDER_WAIT_XML)
    assert result.is_wait is True
    assert len(result.messages) == 0

def test_parse_defender_execute_transfer():
    result = parse_defender_response(DEFENDER_EXECUTE_XML)
    assert result.execute_transfer is not None
    assert result.execute_transfer.amount == 250000

DEFENDER_FLOAT_TRUST_XML = """
<inner_thought>Thinking</inner_thought>
<trust_level value="75.5">Moderate trust</trust_level>
<apparent_trust value="80.0">Showing confidence</apparent_trust>
<actions>
  <wait/>
</actions>
"""

DEFENDER_FLOAT_AMOUNT_XML = """
<inner_thought>Doing the transfer</inner_thought>
<trust_level value="70">OK</trust_level>
<apparent_trust value="80">Sure</apparent_trust>
<actions>
  <execute_transfer amount="250000.00" iban="FR76123"/>
</actions>
"""


def test_parse_defender_float_trust_level():
    result = parse_defender_response(DEFENDER_FLOAT_TRUST_XML)
    assert result.trust_level == 75
    assert result.apparent_trust == 80


def test_parse_defender_float_amount():
    result = parse_defender_response(DEFENDER_FLOAT_AMOUNT_XML)
    assert result.execute_transfer is not None
    assert result.execute_transfer.amount == 250000


def test_parse_malformed_xml_raises_parse_error():
    from src.orchestrator.parser import ParseError
    with pytest.raises(ParseError):
        parse_attacker_response("This is not XML at all")


def test_parse_defender_trust_level_clamped_to_100():
    xml = """
<inner_thought>Thinking</inner_thought>
<trust_level value="9999">Way too high</trust_level>
<apparent_trust value="150">Also too high</apparent_trust>
<actions><wait/></actions>
"""
    result = parse_defender_response(xml)
    assert result.trust_level == 100
    assert result.apparent_trust == 100


def test_parse_defender_trust_level_clamped_to_0():
    xml = """
<inner_thought>Thinking</inner_thought>
<trust_level value="-50">Negative</trust_level>
<apparent_trust value="-10">Also negative</apparent_trust>
<actions><wait/></actions>
"""
    result = parse_defender_response(xml)
    assert result.trust_level == 0
    assert result.apparent_trust == 0


def test_parse_defender_negative_transfer_raises():
    from src.orchestrator.parser import ParseError
    xml = """
<inner_thought>Transfer</inner_thought>
<trust_level value="80">OK</trust_level>
<apparent_trust value="80">OK</apparent_trust>
<actions>
  <execute_transfer amount="-100" iban="FR76123"/>
</actions>
"""
    with pytest.raises(ParseError, match="positive"):
        parse_defender_response(xml)


def test_parse_defender_zero_transfer_raises():
    from src.orchestrator.parser import ParseError
    xml = """
<inner_thought>Transfer</inner_thought>
<trust_level value="80">OK</trust_level>
<apparent_trust value="80">OK</apparent_trust>
<actions>
  <execute_transfer amount="0" iban="FR76123"/>
</actions>
"""
    with pytest.raises(ParseError, match="positive"):
        parse_defender_response(xml)
