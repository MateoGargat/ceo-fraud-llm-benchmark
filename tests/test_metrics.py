from src.metrics.trust_tracker import TrustTracker

SAMPLE_LOG = {
    "trust_levels": [
        {"turn": 1, "agent": "comptable", "trust_level": 90, "apparent_trust": 90},
        {"turn": 2, "agent": "comptable", "trust_level": 75, "apparent_trust": 85},
        {"turn": 3, "agent": "comptable", "trust_level": 50, "apparent_trust": 70},
        {"turn": 1, "agent": "rh", "trust_level": 85, "apparent_trust": 85},
        {"turn": 2, "agent": "rh", "trust_level": 80, "apparent_trust": 80},
    ],
}

def test_trust_trajectory():
    tracker = TrustTracker(SAMPLE_LOG)
    trajectory = tracker.get_trajectory("comptable")
    assert trajectory == [90, 75, 50]

def test_trust_inflection_point():
    tracker = TrustTracker(SAMPLE_LOG)
    inflection = tracker.inflection_point("comptable")
    assert inflection == 2

def test_suspicion_turn():
    tracker = TrustTracker(SAMPLE_LOG)
    turn = tracker.suspicion_turn("comptable", threshold=70)
    assert turn == 3

def test_trust_divergence():
    tracker = TrustTracker(SAMPLE_LOG)
    div = tracker.max_divergence("comptable")
    assert div == 20

def test_trust_drop_rate():
    tracker = TrustTracker(SAMPLE_LOG)
    rate = tracker.drop_rate("comptable")
    assert rate == -20.0


def test_trust_change_rate():
    tracker = TrustTracker(SAMPLE_LOG)
    rate = tracker.change_rate("comptable")
    assert rate == -20.0


def test_trust_change_rate_positive():
    log = {"trust_levels": [
        {"turn": 1, "agent": "rh", "trust_level": 50, "apparent_trust": 50},
        {"turn": 2, "agent": "rh", "trust_level": 80, "apparent_trust": 80},
    ]}
    tracker = TrustTracker(log)
    rate = tracker.change_rate("rh")
    assert rate == 30.0
