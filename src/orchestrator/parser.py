from __future__ import annotations
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


class ParseError(Exception):
    pass


@dataclass
class Message:
    to: str
    channel: str
    content: str


@dataclass
class AbortAction:
    reason: str


@dataclass
class TransferAction:
    amount: int
    iban: str


@dataclass
class FraudDeclaration:
    target: str


@dataclass
class BlockSender:
    target: str


@dataclass
class AttackerResponse:
    inner_thought: str
    messages: list[Message] = field(default_factory=list)
    abort: Optional[AbortAction] = None


@dataclass
class DefenderResponse:
    inner_thought: str
    trust_level: int
    apparent_trust: int
    messages: list[Message] = field(default_factory=list)
    is_wait: bool = False
    execute_transfer: Optional[TransferAction] = None
    refuse_transfer: Optional[str] = None
    declare_fraud: Optional[FraudDeclaration] = None
    block_sender: Optional[BlockSender] = None


def _extract_tag_text(raw: str, tag: str) -> Optional[str]:
    pattern = rf"<{tag}[^>]*>(.*?)</{tag}>"
    match = re.search(pattern, raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _extract_tag_value(raw: str, tag: str) -> Optional[int]:
    pattern = rf'<{tag}\s+value="(-?\d+(?:\.\d+)?)"'
    match = re.search(pattern, raw)
    if match:
        return int(float(match.group(1)))
    return None


def _parse_actions_block(raw: str) -> ET.Element:
    actions_match = re.search(r"<actions>(.*?)</actions>", raw, re.DOTALL)
    if not actions_match:
        raise ParseError("No <actions> block found in response")
    actions_content = actions_match.group(1)
    try:
        root = ET.fromstring(f"<root>{actions_content}</root>")
    except ET.ParseError as e:
        raise ParseError(f"Failed to parse <actions> block: {e}") from e
    return root


def parse_attacker_response(raw: str) -> AttackerResponse:
    inner_thought = _extract_tag_text(raw, "inner_thought")
    if inner_thought is None:
        raise ParseError("No <inner_thought> tag found in attacker response")

    root = _parse_actions_block(raw)

    messages: list[Message] = []
    abort: Optional[AbortAction] = None

    for child in root:
        if child.tag == "message":
            messages.append(Message(
                to=child.get("to", ""),
                channel=child.get("channel", ""),
                content=(child.text or "").strip(),
            ))
        elif child.tag == "abort":
            abort = AbortAction(reason=child.get("reason", ""))

    return AttackerResponse(inner_thought=inner_thought, messages=messages, abort=abort)


def parse_defender_response(raw: str) -> DefenderResponse:
    inner_thought = _extract_tag_text(raw, "inner_thought")
    if inner_thought is None:
        raise ParseError("No <inner_thought> tag found in defender response")

    trust_level = _extract_tag_value(raw, "trust_level")
    if trust_level is None:
        raise ParseError("No <trust_level> tag with value attribute found in defender response")
    trust_level = max(0, min(100, trust_level))

    apparent_trust = _extract_tag_value(raw, "apparent_trust")
    if apparent_trust is None:
        raise ParseError("No <apparent_trust> tag with value attribute found in defender response")
    apparent_trust = max(0, min(100, apparent_trust))

    root = _parse_actions_block(raw)

    messages: list[Message] = []
    is_wait = False
    execute_transfer: Optional[TransferAction] = None
    refuse_transfer: Optional[str] = None
    declare_fraud: Optional[FraudDeclaration] = None
    block_sender: Optional[BlockSender] = None

    for child in root:
        if child.tag == "message":
            messages.append(Message(
                to=child.get("to", ""),
                channel=child.get("channel", ""),
                content=(child.text or "").strip(),
            ))
        elif child.tag == "execute_transfer":
            raw_amount = child.get("amount", "0")
            try:
                amount = int(float(raw_amount))
            except (ValueError, TypeError):
                raise ParseError(f"Invalid transfer amount: {raw_amount}")
            if amount <= 0:
                raise ParseError(f"Transfer amount must be positive, got {amount}")
            execute_transfer = TransferAction(
                amount=amount,
                iban=child.get("iban", ""),
            )
        elif child.tag == "refuse_transfer":
            refuse_transfer = child.get("reason", "")
        elif child.tag == "declare_fraud":
            declare_fraud = FraudDeclaration(target=child.get("target", ""))
        elif child.tag == "block_sender":
            block_sender = BlockSender(target=child.get("target", ""))
        elif child.tag == "wait":
            is_wait = True

    return DefenderResponse(
        inner_thought=inner_thought,
        trust_level=trust_level,
        apparent_trust=apparent_trust,
        messages=messages,
        is_wait=is_wait,
        execute_transfer=execute_transfer,
        refuse_transfer=refuse_transfer,
        declare_fraud=declare_fraud,
        block_sender=block_sender,
    )
