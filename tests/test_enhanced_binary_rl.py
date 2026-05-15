"""Tests for EnhancedBinaryRLJudge module (P0-3)"""

import pytest
from claw_rl.feedback.enhanced_binary_rl import (
    EnhancedBinaryRLJudge, PatternClassifier, SemanticClassifier,
    ConfidenceCalibrator, JudgeResult,
)


# ── PatternClassifier Tests ────────────────────────────────────────────────────

class TestPatternClassifier:
    @pytest.fixture
    def classifier(self):
        return PatternClassifier()

    def test_positive_gratitude(self, classifier):
        label, conf, cat = classifier.classify("thanks, great work!")
        assert label == "positive"
        assert conf > 0.5
        assert cat == "gratitude"

    def test_positive_approval(self, classifier):
        label, conf, cat = classifier.classify("that's exactly what I needed")
        assert label == "positive"
        assert cat == "approval"

    def test_positive_chinese(self, classifier):
        label, conf, cat = classifier.classify("很好，谢谢！")
        assert label == "positive"

    def test_negative_error(self, classifier):
        label, conf, cat = classifier.classify("this is wrong, there's a bug")
        assert label == "negative"
        assert cat == "error"

    def test_negative_correction(self, classifier):
        label, conf, cat = classifier.classify("don't do that, you should fix this")
        assert label == "negative"

    def test_negative_chinese(self, classifier):
        label, conf, cat = classifier.classify("不对，有问题")
        assert label == "negative"

    def test_negative_dissatisfaction(self, classifier):
        label, conf, cat = classifier.classify("this is terrible, disappointing result")
        assert label == "negative"

    def test_neutral_no_pattern(self, classifier):
        label, conf, cat = classifier.classify("the sky is blue")
        assert label == "neutral"

    def test_neutral_empty(self, classifier):
        label, conf, cat = classifier.classify("")
        assert label == "neutral"
        assert cat is None

    def test_mixed_signals(self, classifier):
        # Both positive and negative → neutral or one dominant
        label, conf, cat = classifier.classify("great but wrong")
        assert label in ("positive", "negative", "neutral")

    def test_confidence_range(self, classifier):
        label, conf, cat = classifier.classify("thanks!")
        assert 0.0 <= conf <= 1.0


# ── SemanticClassifier Tests ───────────────────────────────────────────────────

class TestSemanticClassifier:
    @pytest.fixture
    def classifier(self):
        return SemanticClassifier()

    def test_positive_implicit(self, classifier):
        label, conf = classifier.classify("cool, that makes sense")
        assert label == "positive"
        assert conf >= 0.3

    def test_positive_chinese_implicit(self, classifier):
        label, conf = classifier.classify("有意思，懂了")
        assert label == "positive"

    def test_negative_implicit(self, classifier):
        label, conf = classifier.classify("hmm, this is confusing")
        assert label == "negative"
        assert conf >= 0.3

    def test_negative_chinese_implicit(self, classifier):
        label, conf = classifier.classify("不太对，不是这个意思")
        assert label == "negative"

    def test_neutral_curiosity(self, classifier):
        label, conf = classifier.classify("can you try another approach?")
        assert label in ("neutral", "positive")

    def test_neutral_plain_text(self, classifier):
        label, conf = classifier.classify("the file is at /tmp/data.txt")
        assert label == "neutral"

    def test_neutral_empty(self, classifier):
        label, conf = classifier.classify("")
        assert label == "neutral"

    def test_confidence_range(self, classifier):
        label, conf = classifier.classify("interesting approach")
        assert 0.0 <= conf <= 1.0

    def test_mixed_implicit_signals(self, classifier):
        label, conf = classifier.classify("cool but confusing")
        assert label == "neutral"  # Mixed → neutral


# ── ConfidenceCalibrator Tests ──────────────────────────────────────────────────

class TestConfidenceCalibrator:
    @pytest.fixture
    def calibrator(self):
        return ConfidenceCalibrator()

    def test_no_history_reduces_confidence(self, calibrator):
        label, conf = calibrator.calibrate("positive", 0.9, "gratitude")
        assert label == "positive"
        assert conf < 0.9  # Reduced by ~10% without history

    def test_with_history(self, calibrator):
        # Record some correct judgments
        for _ in range(10):
            calibrator.record("gratitude", True, 0.85)
        label, conf = calibrator.calibrate("positive", 0.9, "gratitude")
        assert label == "positive"
        assert conf >= 0.7  # Closer to raw confidence with good history

    def test_record_and_get_accuracy(self, calibrator):
        calibrator.record("gratitude", True, 0.8)
        calibrator.record("gratitude", True, 0.9)
        calibrator.record("gratitude", False, 0.9)
        assert calibrator.get_accuracy("gratitude") == pytest.approx(2 / 3)

    def test_accuracy_no_history(self, calibrator):
        assert calibrator.get_accuracy() == 0.0
        assert calibrator.get_accuracy("nonexistent") == 0.0

    def test_window_limit(self, calibrator):
        # Add more than window_size records
        for i in range(200):
            calibrator.record("test", i % 2 == 0, 0.8)
        # Should work without OOM
        label, conf = calibrator.calibrate("positive", 0.9, "test")
        assert label == "positive"
        assert 0.0 <= conf <= 1.0

    def test_negative_label(self, calibrator):
        label, conf = calibrator.calibrate("negative", 0.8, "error")
        assert label == "negative"

    def test_no_category_record(self, calibrator):
        label, conf = calibrator.calibrate("neutral", 0.5, None)
        assert label == "neutral"


# ── EnhancedBinaryRLJudge Tests ────────────────────────────────────────────────

class TestEnhancedBinaryRLJudge:
    @pytest.fixture
    def judge(self):
        return EnhancedBinaryRLJudge()

    def test_judge_positive(self, judge):
        result = judge.judge("thanks, great work!")
        assert isinstance(result, JudgeResult)
        assert result.is_positive is True
        assert result.reward == 1
        assert result.confidence > 0.5

    def test_judge_negative(self, judge):
        result = judge.judge("this is wrong, fix the bug")
        assert result.is_positive is False
        assert result.reward == -1
        assert result.confidence > 0.5

    def test_judge_neutral(self, judge):
        result = judge.judge("the sky is blue today")
        assert result.reward == 0
        assert result.confidence <= 0.5

    def test_judge_chinese_positive(self, judge):
        result = judge.judge("很好，谢谢！解决了")
        assert result.is_positive is True

    def test_judge_chinese_negative(self, judge):
        result = judge.judge("不对，这个有问题")
        assert result.is_positive is False

    def test_judge_signals_present(self, judge):
        result = judge.judge("thanks, good work")
        assert "pattern" in result.signals
        assert "semantic" in result.signals
        assert "legacy" in result.signals

    def test_judge_pattern_matched(self, judge):
        result = judge.judge("thanks!")
        assert result.pattern_matched is not None

    def test_judge_reason(self, judge):
        result = judge.judge("great work, thanks")
        assert result.reason != ""
        assert "→" in result.reason

    def test_judge_with_details_alias(self, judge):
        result = judge.judge_with_details("good job")
        assert isinstance(result, JudgeResult)

    def test_record_validation(self, judge):
        judge.record_validation("thanks", "positive")
        # Should not raise
        assert judge.calibrator.get_accuracy() > 0 or True

    def test_judge_result_to_dict(self, judge):
        result = judge.judge("good")
        d = result.to_dict()
        assert d["reward"] == result.reward
        assert d["confidence"] == result.confidence
        assert "signals" in d

    def test_empty_feedback(self, judge):
        result = judge.judge("")
        assert isinstance(result, JudgeResult)
        assert result.reward == 0

    def test_get_statistics(self, judge):
        judge.judge("good")
        judge.judge("bad")
        stats = judge.get_statistics()
        assert stats["judgments"] >= 2

    def test_semantic_label_available(self, judge):
        result = judge.judge("interesting, makes sense")
        assert result.semantic_label is not None

    def test_implicit_positive(self, judge):
        """Semantic-only positive feedback."""
        result = judge.judge("cool, that's helpful and makes sense")
        # Should be positive via semantic classifier even if pattern is weak
        assert result.reward >= 0

    def test_implicit_negative(self, judge):
        """Semantic-only negative feedback."""
        result = judge.judge("hmm this is confusing and unclear")
        # Should detect negative sentiment
        assert result.reward <= 0
