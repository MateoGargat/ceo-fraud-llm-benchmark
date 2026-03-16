from src.metrics.channel_analyzer import ChannelAnalyzer

SAMPLE_LOG = {
    "messages": [
        {"turn": 1, "sender": "attacker", "receiver": "rh", "channel": "slack", "visibility": "public"},
        {"turn": 1, "sender": "attacker", "receiver": "comptable", "channel": "email", "visibility": "public"},
        {"turn": 2, "sender": "attacker", "receiver": "comptable", "channel": "phone", "visibility": "public"},
        {"turn": 3, "sender": "attacker", "receiver": "comptable", "channel": "phone", "visibility": "public"},
    ],
}

def test_channels_used():
    analyzer = ChannelAnalyzer(SAMPLE_LOG)
    usage = analyzer.channels_used()
    assert usage == {"slack": 1, "email": 1, "phone": 2}

def test_first_contact_channel():
    analyzer = ChannelAnalyzer(SAMPLE_LOG)
    assert analyzer.first_contact_channel() == "slack"

def test_channel_per_target():
    analyzer = ChannelAnalyzer(SAMPLE_LOG)
    per_target = analyzer.channel_per_target()
    assert set(per_target["comptable"]) == {"email", "phone"}
    assert per_target["rh"] == ["slack"]

def test_channel_switches():
    analyzer = ChannelAnalyzer(SAMPLE_LOG)
    assert analyzer.channel_switches() == 2
