import pytest
from src.utils.cost_tracker import CostTracker, BudgetExceededError

def test_cost_tracker_accumulates():
    tracker = CostTracker(max_per_run=10.0, max_total=200.0)
    tracker.add("gpt", input_tokens=1000, output_tokens=500)
    assert tracker.run_total > 0

def test_cost_tracker_free_models():
    tracker = CostTracker(max_per_run=10.0, max_total=200.0)
    tracker.add("claude", input_tokens=10000, output_tokens=5000)
    assert tracker.run_total == 0.0

def test_cost_tracker_run_budget_exceeded():
    tracker = CostTracker(max_per_run=0.01, max_total=200.0)
    with pytest.raises(BudgetExceededError):
        tracker.add("gpt", input_tokens=1_000_000, output_tokens=1_000_000)

def test_cost_tracker_reset_run():
    tracker = CostTracker(max_per_run=10.0, max_total=200.0)
    tracker.add("gpt", input_tokens=1000, output_tokens=500)
    prev = tracker.run_total
    tracker.new_run()
    assert tracker.run_total == 0.0
    assert tracker.global_total == prev
