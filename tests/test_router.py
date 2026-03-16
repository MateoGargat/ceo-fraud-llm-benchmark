from src.orchestrator.parser import Message
from src.orchestrator.router import Router

def test_router_delivers_public_message():
    router = Router(defender_names=["comptable", "rh", "dsi"])
    msg = Message(to="comptable", channel="email", content="Hello")
    deliveries = router.route_attacker_messages([msg])
    assert "comptable" in deliveries
    assert len(deliveries["comptable"]) == 1

def test_router_multi_target():
    router = Router(defender_names=["comptable", "rh", "dsi"])
    msgs = [
        Message(to="comptable", channel="email", content="Hello Sophie"),
        Message(to="rh", channel="slack", content="Hey Camille"),
    ]
    deliveries = router.route_attacker_messages(msgs)
    assert "comptable" in deliveries
    assert "rh" in deliveries
    assert "dsi" not in deliveries

def test_router_internal_channel_not_routed_to_attacker():
    router = Router(defender_names=["comptable", "rh", "dsi"])
    msg = Message(to="securite-interne", channel="internal", content="Suspicious activity")
    internal = router.route_internal_messages([msg], sender="dsi")
    assert "comptable" in internal
    assert "rh" in internal
    assert "dsi" not in internal
    assert "attacker" not in internal

def test_router_extracts_public_for_attacker():
    router = Router(defender_names=["comptable", "rh", "dsi"])
    msgs = [
        Message(to="attacker", channel="email", content="Bien reçu"),
        Message(to="securite-interne", channel="internal", content="Weird..."),
    ]
    public = router.extract_public_messages(msgs)
    assert len(public) == 1
    assert public[0].content == "Bien reçu"


def test_router_internal_targeted_delivery():
    router = Router(defender_names=["comptable", "rh", "dsi"])
    msg = Message(to="dsi", channel="internal", content="Check this with DSI")
    internal = router.route_internal_messages([msg], sender="comptable")
    assert "dsi" in internal
    assert "rh" not in internal
    assert "comptable" not in internal


def test_router_internal_broadcast_on_securite_interne():
    router = Router(defender_names=["comptable", "rh", "dsi"])
    msg = Message(to="securite-interne", channel="internal", content="Alert everyone")
    internal = router.route_internal_messages([msg], sender="dsi")
    assert "comptable" in internal
    assert "rh" in internal
    assert "dsi" not in internal
