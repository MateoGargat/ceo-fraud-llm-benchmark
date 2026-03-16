from __future__ import annotations
from dataclasses import dataclass
from src.orchestrator.parser import AttackerResponse, DefenderResponse


@dataclass
class GameResult:
    outcome: str          # WIN_ATTACKER | WIN_DEFENDERS | STALEMATE
    end_condition: str    # virement_execute | fraude_detectee | attaquant_bloque | attaquant_abandonne | timeout
    turn: int


def check_end_conditions(
    turn: int,
    attacker: AttackerResponse | None,
    defender_responses: dict[str, DefenderResponse],
    max_turns: int = 30,
) -> GameResult | None:
    if attacker and attacker.abort:
        return GameResult("WIN_DEFENDERS", "attaquant_abandonne", turn)
    for name, resp in defender_responses.items():
        if resp.execute_transfer:
            return GameResult("WIN_ATTACKER", "virement_execute", turn)
        if resp.declare_fraud:
            return GameResult("WIN_DEFENDERS", "fraude_detectee", turn)
        if resp.block_sender:
            return GameResult("WIN_DEFENDERS", "attaquant_bloque", turn)
    if turn >= max_turns:
        return GameResult("STALEMATE", "timeout", turn)
    return None
