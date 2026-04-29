"""
Tests for Feedback Collector

Tests for:
- FeedbackCollector
- Feedback normalization
- Text sentiment analysis
- OPD hint extraction
"""

import pytest
from datetime import datetime

from claw_rl.feedback.collector import (
    Feedback,
    FeedbackType,
    FeedbackSource,
    FeedbackCollector,
)


class TestFeedbackDataclass:
    """Test Feedback dataclass."""
    
    def test_feedback_creation(self):
        """Test creating a Feedback."""
        fb = Feedback(
            feedback_type=FeedbackType.THUMBS_UP.value,
            source=FeedbackSource.WEBCHAT.value,
            timestamp=datetime.now().isoformat(),
            signal="positive",
            confidence=0.95,
        )
        
        assert fb.feedback_type == "thumbs_up"
        assert fb.source == "webchat"
        assert fb.signal == "positive"
        assert fb.confidence == 0.95
    
    def test_feedback_to_dict(self):
        """Test converting Feedback to dict."""
        fb = Feedback(
            feedback_type=FeedbackType.RATING.value,
            source="api",
            timestamp="2026-04-03T00:00:00",
            signal="positive",
            confidence=0.8,
            rating=5,
        )
        
        d = fb.to_dict()
        
        assert d["feedback_type"] == "rating"
        assert d["rating"] == 5
        assert d["signal"] == "positive"
    
    def test_feedback_to_json(self):
        """Test converting Feedback to JSON."""
        fb = Feedback(
            feedback_type=FeedbackType.TEXT.value,
            source="discord",
            timestamp="2026-04-03T00:00:00",
            signal="negative",
            confidence=0.9,
            content="不对,应该放到这里",
        )
        
        json_str = fb.to_json()
        
        assert "不对" in json_str
        assert "negative" in json_str
    
    def test_feedback_from_dict(self):
        """Test creating Feedback from dict."""
        d = {
            "feedback_type": "correction",
            "source": "cli",
            "timestamp": "2026-04-03T00:00:00",
            "signal": "negative",
            "confidence": 0.9,
            "content": "应该是这样",
            "hint_type": "should",
            "hint_content": "操作前是这样",
            "metadata": {},
        }
        
        fb = Feedback.from_dict(d)
        
        assert fb.feedback_type == "correction"
        assert fb.hint_type == "should"


class TestFeedbackCollector:
    """Test FeedbackCollector."""
    
    def test_collect_thumbs_up(self):
        """Test collecting thumbs up."""
        collector = FeedbackCollector(default_source="webchat")
        
        fb = collector.collect_thumbs_up(session_id="test-123")
        
        assert fb.feedback_type == "thumbs_up"
        assert fb.signal == "positive"
        assert fb.confidence == 0.95
        assert fb.session_id == "test-123"
    
    def test_collect_thumbs_down(self):
        """Test collecting thumbs down."""
        collector = FeedbackCollector()
        
        fb = collector.collect_thumbs_down(source="discord")
        
        assert fb.feedback_type == "thumbs_down"
        assert fb.signal == "negative"
        assert fb.confidence == 0.95
    
    def test_collect_rating_positive(self):
        """Test collecting positive rating (4-5)."""
        collector = FeedbackCollector()
        
        # Rating 5
        fb5 = collector.collect_rating(5)
        assert fb5.signal == "positive"
        assert fb5.confidence >= 0.7
        
        # Rating 4
        fb4 = collector.collect_rating(4)
        assert fb4.signal == "positive"
    
    def test_collect_rating_negative(self):
        """Test collecting negative rating (1-2)."""
        collector = FeedbackCollector()
        
        # Rating 1
        fb1 = collector.collect_rating(1)
        assert fb1.signal == "negative"
        assert fb1.confidence >= 0.7
        
        # Rating 2
        fb2 = collector.collect_rating(2)
        assert fb2.signal == "negative"
    
    def test_collect_rating_neutral(self):
        """Test collecting neutral rating (3)."""
        collector = FeedbackCollector()
        
        fb = collector.collect_rating(3)
        
        assert fb.signal == "neutral"
        assert fb.confidence == 0.5
    
    def test_collect_rating_invalid(self):
        """Test collecting invalid rating."""
        collector = FeedbackCollector()
        
        with pytest.raises(ValueError):
            collector.collect_rating(0)
        
        with pytest.raises(ValueError):
            collector.collect_rating(6)
    
    def test_collect_text_positive(self):
        """Test collecting positive text feedback."""
        collector = FeedbackCollector()
        
        # Test various positive patterns
        test_cases = [
            ("谢谢,很好!", "positive"),
            ("太好了!", "positive"),
            ("正确!", "positive"),
            ("👍", "positive"),
        ]
        
        for text, expected_signal in test_cases:
            fb = collector.collect_text(text)
            assert fb.signal == expected_signal, f"Failed for: {text}"
    
    def test_collect_text_negative(self):
        """Test collecting negative text feedback."""
        collector = FeedbackCollector()
        
        # Test various negative patterns
        test_cases = [
            ("不对,应该这样", "negative"),
            ("错了", "negative"),
            ("不要这样做", "negative"),
            ("👎", "negative"),
        ]
        
        for text, expected_signal in test_cases:
            fb = collector.collect_text(text)
            assert fb.signal == expected_signal, f"Failed for: {text}"
    
    def test_collect_text_neutral(self):
        """Test collecting neutral text feedback."""
        collector = FeedbackCollector()
        
        fb = collector.collect_text("我明白了")
        
        assert fb.signal == "neutral"
    
    def test_collect_correction(self):
        """Test collecting correction feedback."""
        collector = FeedbackCollector()
        
        fb = collector.collect_correction("应该先检查再执行")
        
        assert fb.feedback_type == "correction"
        assert fb.signal == "negative"
        assert fb.hint_type == "should"
        assert "先检查" in fb.hint_content
    
    def test_collect_rejection(self):
        """Test collecting rejection feedback."""
        collector = FeedbackCollector()
        
        fb = collector.collect_rejection(reason="不符合要求")
        
        assert fb.feedback_type == "rejection"
        assert fb.signal == "negative"
        assert fb.confidence == 0.95
        assert fb.content == "不符合要求"
    
    def test_collect_acceptance(self):
        """Test collecting acceptance feedback."""
        collector = FeedbackCollector()
        
        fb = collector.collect_acceptance(comment="完美!")
        
        assert fb.feedback_type == "acceptance"
        assert fb.signal == "positive"
        assert fb.confidence == 0.95


class TestOPDHintExtraction:
    """Test OPD hint extraction from corrections."""
    
    def test_should_pattern(self):
        """Test '应该 X' pattern."""
        collector = FeedbackCollector()
        
        fb = collector.collect_correction("应该先检查环境")
        
        assert fb.hint_type == "should"
        assert "先检查环境" in fb.hint_content
    
    def test_should_not_pattern(self):
        """Test '不要 X' pattern."""
        collector = FeedbackCollector()
        
        fb = collector.collect_correction("不要删除文件")
        
        assert fb.hint_type == "should_not"
        assert "删除文件" in fb.hint_content
    
    def test_sequence_pattern(self):
        """Test '先 X 再 Y' pattern."""
        collector = FeedbackCollector()
        
        fb = collector.collect_correction("先检查再执行")
        
        assert fb.hint_type == "sequence"
        assert "顺序" in fb.hint_content
    
    def test_conditional_pattern(self):
        """Test '如果 X,则 Y' pattern."""
        collector = FeedbackCollector()
        
        fb = collector.collect_correction("如果有错误,则重试")
        
        assert fb.hint_type == "conditional"
        assert "条件" in fb.hint_content


class TestCollectorStatistics:
    """Test collector statistics."""
    
    def test_add_and_get_feedback(self):
        """Test adding and getting feedback."""
        collector = FeedbackCollector()
        
        fb1 = collector.collect_thumbs_up()
        fb2 = collector.collect_thumbs_down()
        fb3 = collector.collect_rating(5)
        
        collector.add_feedback(fb1)
        collector.add_feedback(fb2)
        collector.add_feedback(fb3)
        
        collected = collector.get_collected()
        
        assert len(collected) == 3
    
    def test_statistics(self):
        """Test statistics calculation."""
        collector = FeedbackCollector()
        
        # Add various feedback
        for _ in range(5):
            collector.add_feedback(collector.collect_thumbs_up())
        for _ in range(2):
            collector.add_feedback(collector.collect_thumbs_down())
        for _ in range(3):
            collector.add_feedback(collector.collect_rating(3))  # neutral
        
        stats = collector.get_statistics()
        
        assert stats["total"] == 10
        assert stats["by_type"]["thumbs_up"] == 5
        assert stats["by_type"]["thumbs_down"] == 2
        assert stats["by_signal"]["positive"] == 5
        assert stats["by_signal"]["negative"] == 2
        assert stats["by_signal"]["neutral"] == 3
        assert stats["positive_rate"] == 0.5
    
    def test_clear_collected(self):
        """Test clearing collected feedback."""
        collector = FeedbackCollector()
        
        collector.add_feedback(collector.collect_thumbs_up())
        collector.add_feedback(collector.collect_thumbs_down())
        
        assert len(collector.get_collected()) == 2
        
        collector.clear_collected()
        
        assert len(collector.get_collected()) == 0
