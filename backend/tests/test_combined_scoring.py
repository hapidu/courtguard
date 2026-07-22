"""
Unit tests for the combined multi-modal risk scoring logic.

Run with (from the backend folder, venv activated):
    pytest tests/ -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.routers.combined import _risk_contribution, ModuleScore, WEIGHTS


def test_fake_verdict_contributes_its_own_confidence_as_risk():
    module = ModuleScore(verdict="fake", confidence_score=90)
    contribution = _risk_contribution(module, weight=1.0)
    assert contribution == 90


def test_real_verdict_contributes_inverse_of_confidence_as_risk():
    module = ModuleScore(verdict="real", confidence_score=90)
    contribution = _risk_contribution(module, weight=1.0)
    # High confidence in "real" should mean LOW risk
    assert contribution == 10


def test_missing_module_contributes_zero_risk():
    contribution = _risk_contribution(None, weight=0.5)
    assert contribution == 0


def test_weight_is_applied_correctly():
    module = ModuleScore(verdict="fake", confidence_score=100)
    contribution = _risk_contribution(module, weight=0.4)
    assert contribution == 40


def test_weights_sum_to_one():
    total = sum(WEIGHTS.values())
    assert abs(total - 1.0) < 0.001


def test_video_has_highest_weight():
    # Matches your survey finding: video was rated the most vulnerable
    # evidence type (46.3%), so it should carry the most weight.
    assert WEIGHTS["video"] == max(WEIGHTS.values())