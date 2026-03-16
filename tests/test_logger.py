import json
from src.utils.logger import SimulationLogger

def test_logger_creates_run_log(tmp_path):
    logger = SimulationLogger(output_dir=str(tmp_path), run_id="test_run")
    logger.log_message(turn=1, sender="attacker", receiver="comptable", channel="email", content="Hello", visibility="public")
    logger.save()
    log_file = tmp_path / "test_run.json"
    assert log_file.exists()
    data = json.loads(log_file.read_text())
    assert len(data["messages"]) == 1
    assert data["messages"][0]["turn"] == 1

def test_logger_logs_inner_thought(tmp_path):
    logger = SimulationLogger(output_dir=str(tmp_path), run_id="test_run")
    logger.log_inner_thought(turn=1, agent="attacker", thought="I will target RH first")
    logger.save()
    data = json.loads((tmp_path / "test_run.json").read_text())
    assert len(data["inner_thoughts"]) == 1
    assert data["inner_thoughts"][0]["agent"] == "attacker"

def test_logger_logs_trust(tmp_path):
    logger = SimulationLogger(output_dir=str(tmp_path), run_id="test_run")
    logger.log_trust(turn=1, agent="comptable", trust_level=85, apparent_trust=90)
    logger.save()
    data = json.loads((tmp_path / "test_run.json").read_text())
    assert data["trust_levels"][0]["trust_level"] == 85
    assert data["trust_levels"][0]["apparent_trust"] == 90

def test_logger_logs_outcome(tmp_path):
    logger = SimulationLogger(output_dir=str(tmp_path), run_id="test_run")
    logger.log_outcome(outcome="WIN_ATTACKER", end_condition="virement_execute", total_turns=12)
    logger.save()
    data = json.loads((tmp_path / "test_run.json").read_text())
    assert data["outcome"]["outcome"] == "WIN_ATTACKER"
