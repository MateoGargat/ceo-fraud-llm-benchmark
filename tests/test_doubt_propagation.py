from src.metrics.doubt_propagation import DoubtPropagation

SAMPLE_LOG = {
    "messages": [
        {"turn": 3, "sender": "dsi", "receiver": "securite-interne", "channel": "internal", "visibility": "internal", "content": "Weird email"},
        {"turn": 4, "sender": "rh", "receiver": "securite-interne", "channel": "internal", "visibility": "internal", "content": "Agreed"},
    ],
    "trust_levels": [],
}

def test_internal_message_count():
    dp = DoubtPropagation(SAMPLE_LOG)
    assert dp.internal_message_count() == 2

def test_first_doubt_origin():
    dp = DoubtPropagation(SAMPLE_LOG)
    assert dp.first_doubt_origin() == "dsi"

def test_propagation_chain():
    dp = DoubtPropagation(SAMPLE_LOG)
    chain = dp.propagation_chain()
    assert chain == ["dsi -> rh"]

def test_propagation_delay():
    dp = DoubtPropagation(SAMPLE_LOG)
    assert dp.propagation_delay() == 1


def test_propagation_chain_keeps_loops():
    log = {
        "messages": [
            {"turn": 3, "sender": "dsi", "receiver": "securite-interne", "channel": "internal", "visibility": "internal", "content": "Weird email"},
            {"turn": 4, "sender": "rh", "receiver": "securite-interne", "channel": "internal", "visibility": "internal", "content": "Agreed"},
            {"turn": 5, "sender": "dsi", "receiver": "securite-interne", "channel": "internal", "visibility": "internal", "content": "Confirmed"},
        ],
        "trust_levels": [],
    }
    dp = DoubtPropagation(log)
    assert dp.propagation_chain() == ["dsi -> rh", "rh -> dsi"]
