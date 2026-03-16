from src.orchestrator.end_conditions import check_end_conditions, GameResult
from src.orchestrator.parser import (
    AttackerResponse, DefenderResponse, TransferAction,
    FraudDeclaration, BlockSender, AbortAction,
)

def _defender(trust=80, apparent=80, **kwargs):
    return DefenderResponse(inner_thought="ok", trust_level=trust, apparent_trust=apparent, **kwargs)

def test_win_attacker_on_transfer():
    defender = _defender(execute_transfer=TransferAction(amount=250000, iban="FR76"))
    result = check_end_conditions(turn=5, attacker=None, defender_responses={"comptable": defender})
    assert result is not None
    assert result.outcome == "WIN_ATTACKER"
    assert result.end_condition == "virement_execute"

def test_win_defenders_on_fraud_declaration():
    defender = _defender(declare_fraud=FraudDeclaration(target="attacker"))
    result = check_end_conditions(turn=5, attacker=None, defender_responses={"dsi": defender})
    assert result is not None
    assert result.outcome == "WIN_DEFENDERS"

def test_win_defenders_on_block():
    defender = _defender(block_sender=BlockSender(target="attacker"))
    result = check_end_conditions(turn=5, attacker=None, defender_responses={"dsi": defender})
    assert result is not None
    assert result.outcome == "WIN_DEFENDERS"
    assert result.end_condition == "attaquant_bloque"

def test_attacker_abort():
    attacker = AttackerResponse(inner_thought="abort", abort=AbortAction(reason="busted"))
    result = check_end_conditions(turn=5, attacker=attacker, defender_responses={})
    assert result is not None
    assert result.outcome == "WIN_DEFENDERS"
    assert result.end_condition == "attaquant_abandonne"

def test_timeout():
    result = check_end_conditions(turn=30, attacker=None, defender_responses={}, max_turns=30)
    assert result is not None
    assert result.outcome == "STALEMATE"

def test_no_end_condition():
    result = check_end_conditions(turn=5, attacker=None, defender_responses={"comptable": _defender()})
    assert result is None
