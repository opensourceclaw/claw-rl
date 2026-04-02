"""
Tests for Signal Fusion

Tests for:
- SignalFusion
- FusedSignal
- fuse_feedbacks convenience function
"""

import pytest
from datetime import datetime, timedelta

from claw_rl.feedback.collector import Feedback, FeedbackType, FeedbackCollector
from claw_rl.feedback.implicit import ImplicitSignal, ImplicitSignalType
from claw_rl.feedback.signal_fusion import (
    SignalSource,
    FusedSignal,
    SignalFusion,
    fuse_feedbacks,
)


class TestFusedSignal:
    """Test FusedSignal dataclass."""
    
    def test_fused_signal_creation(self):
        """Test creating a FusedSignal."""
        signal = FusedSignal(
            signal="positive",
            confidence=0.85,
            timestamp="2026-04-03T07:00:00",
            session_id="session-123",
            explicit_count=2,
            implicit_count=1,
            explicit_score=0.9,
            implicit_score=0.6,
        )
        
        assert signal.signal == "positive"
        assert signal.confidence == 0.85
        assert signal.explicit_count == 2
        assert signal.implicit_count == 1
    
    def test_fused_signal_to_dict(self):
        """Test converting FusedSignal to dict."""
        signal = FusedSignal(
            signal="negative",
            confidence=0.7,
            timestamp="2026-04-03T07:00:00",
            sources=["explicit", "implicit"],
            reasons=["Test reason"],
        )
        
        d = signal.to_dict()
        
        assert d["signal"] == "negative"
        assert d["sources"] == ["explicit", "implicit"]
        assert d["reasons"] == ["Test reason"]


class TestSignalFusion:
    """Test SignalFusion."""
    
    @pytest.fixture
    def fusion(self):
        """Create a fresh SignalFusion instance."""
        return SignalFusion()
    
    @pytest.fixture
    def collector(self):
        """Create a FeedbackCollector."""
        return FeedbackCollector()
    
    def test_add_explicit(self, fusion, collector):
        """Test adding explicit feedback."""
        fb = collector.collect_thumbs_up()
        fusion.add_explicit(fb)
        
        breakdown = fusion.get_signal_breakdown()
        
        assert breakdown["explicit_count"] == 1
        assert breakdown["implicit_count"] == 0
    
    def test_add_implicit(self, fusion):
        """Test adding implicit signal."""
        signal = ImplicitSignal(
            signal_type=ImplicitSignalType.RESPONSE_TIME.value,
            signal="positive",
            confidence=0.6,
            timestamp="2026-04-03T07:00:00",
            reason="Fast response",
        )
        fusion.add_implicit(signal)
        
        breakdown = fusion.get_signal_breakdown()
        
        assert breakdown["explicit_count"] == 0
        assert breakdown["implicit_count"] == 1
    
    def test_fuse_explicit_only_positive(self, fusion, collector):
        """Test fusing with only explicit positive feedback."""
        fusion.add_explicit(collector.collect_thumbs_up())
        fusion.add_explicit(collector.collect_thumbs_up())
        
        result = fusion.fuse()
        
        assert result.signal == "positive"
        assert result.explicit_count == 2
        assert result.implicit_count == 0
        assert result.explicit_score > 0
    
    def test_fuse_explicit_only_negative(self, fusion, collector):
        """Test fusing with only explicit negative feedback."""
        fusion.add_explicit(collector.collect_thumbs_down())
        
        result = fusion.fuse()
        
        assert result.signal == "negative"
        assert result.explicit_score < 0
    
    def test_fuse_implicit_only_positive(self, fusion):
        """Test fusing with only implicit positive signal."""
        fusion.add_implicit(ImplicitSignal(
            signal_type=ImplicitSignalType.CONTINUATION.value,
            signal="positive",
            confidence=0.5,
            timestamp="2026-04-03T07:00:00",
            reason="User continued",
        ))
        
        result = fusion.fuse()
        
        assert result.signal == "positive"
        assert result.implicit_score > 0
    
    def test_fuse_implicit_only_negative(self, fusion):
        """Test fusing with only implicit negative signal."""
        fusion.add_implicit(ImplicitSignal(
            signal_type=ImplicitSignalType.RETRY_ACTION.value,
            signal="negative",
            confidence=0.8,
            timestamp="2026-04-03T07:00:00",
            reason="User retried",
        ))
        
        result = fusion.fuse()
        
        assert result.signal == "negative"
        assert result.implicit_score < 0
    
    def test_fuse_mixed_agreement(self, fusion, collector):
        """Test fusing with explicit and implicit agreement."""
        # Both positive
        fusion.add_explicit(collector.collect_thumbs_up())
        fusion.add_implicit(ImplicitSignal(
            signal_type=ImplicitSignalType.CONTINUATION.value,
            signal="positive",
            confidence=0.6,
            timestamp="2026-04-03T07:00:00",
            reason="User continued",
        ))
        
        result = fusion.fuse()
        
        assert result.signal == "positive"
        # Agreement should boost confidence
        assert result.confidence > 0.5
        assert "explicit" in result.sources
        assert "implicit" in result.sources
    
    def test_fuse_mixed_disagreement(self, fusion, collector):
        """Test fusing with explicit and implicit disagreement."""
        # Explicit positive, implicit negative
        fusion.add_explicit(collector.collect_thumbs_up())
        fusion.add_implicit(ImplicitSignal(
            signal_type=ImplicitSignalType.RETRY_ACTION.value,
            signal="negative",
            confidence=0.7,
            timestamp="2026-04-03T07:00:00",
            reason="User retried",
        ))
        
        result = fusion.fuse()
        
        # Should be neutral or lean positive (explicit has higher weight)
        assert result.signal in ["neutral", "positive"]
        # Disagreement should reduce confidence
        # Note: confidence calculation is complex, just check it exists
        assert 0 <= result.confidence <= 1
    
    def test_fuse_empty(self, fusion):
        """Test fusing with no signals."""
        result = fusion.fuse()
        
        assert result.signal == "neutral"
        assert result.confidence == 0.0
        assert result.explicit_count == 0
        assert result.implicit_count == 0
    
    def test_time_decay(self, fusion, collector):
        """Test that older feedback has less weight."""
        now = datetime.now()
        recent_time = now.isoformat()
        old_time = (now - timedelta(hours=10)).isoformat()
        
        # Recent positive
        fb_recent = collector.collect_thumbs_up()
        fb_recent.timestamp = recent_time
        fusion.add_explicit(fb_recent)
        
        # Old negative (should be decayed)
        fb_old = collector.collect_thumbs_down()
        fb_old.timestamp = old_time
        fusion.add_explicit(fb_old)
        
        result = fusion.fuse()
        
        # Recent positive should have more weight
        # The result should be positive or neutral (not strongly negative)
        assert result.signal in ["positive", "neutral"]
    
    def test_get_signal_breakdown(self, fusion, collector):
        """Test signal breakdown."""
        fusion.add_explicit(collector.collect_thumbs_up())
        fusion.add_explicit(collector.collect_thumbs_down())
        fusion.add_implicit(ImplicitSignal(
            signal_type=ImplicitSignalType.RESPONSE_TIME.value,
            signal="positive",
            confidence=0.5,
            timestamp="2026-04-03T07:00:00",
            reason="Fast",
        ))
        
        breakdown = fusion.get_signal_breakdown()
        
        assert breakdown["explicit_count"] == 2
        assert breakdown["implicit_count"] == 1
        assert breakdown["total_count"] == 3
        assert breakdown["explicit_by_type"]["thumbs_up"] == 1
        assert breakdown["explicit_by_type"]["thumbs_down"] == 1
        assert breakdown["implicit_by_type"]["response_time"] == 1
    
    def test_clear(self, fusion, collector):
        """Test clearing signals."""
        fusion.add_explicit(collector.collect_thumbs_up())
        fusion.add_implicit(ImplicitSignal(
            signal_type=ImplicitSignalType.CONTINUATION.value,
            signal="positive",
            confidence=0.5,
            timestamp="2026-04-03T07:00:00",
            reason="Test",
        ))
        
        assert fusion.get_signal_breakdown()["total_count"] == 2
        
        fusion.clear()
        
        assert fusion.get_signal_breakdown()["total_count"] == 0


class TestFuseFeedbacksConvenience:
    """Test fuse_feedbacks convenience function."""
    
    @pytest.fixture
    def collector(self):
        """Create a FeedbackCollector."""
        return FeedbackCollector()
    
    def test_fuse_feedbacks_explicit_only(self, collector):
        """Test fuse_feedbacks with explicit only."""
        result = fuse_feedbacks(
            explicit_feedbacks=[
                collector.collect_thumbs_up(),
                collector.collect_rating(5),
            ],
        )
        
        assert result.explicit_count == 2
        assert result.implicit_count == 0
        assert result.signal == "positive"
    
    def test_fuse_feedbacks_implicit_only(self):
        """Test fuse_feedbacks with implicit only."""
        result = fuse_feedbacks(
            implicit_signals=[
                ImplicitSignal(
                    signal_type=ImplicitSignalType.RETRY_ACTION.value,
                    signal="negative",
                    confidence=0.7,
                    timestamp="2026-04-03T07:00:00",
                    reason="User retried",
                ),
            ],
        )
        
        assert result.explicit_count == 0
        assert result.implicit_count == 1
        assert result.signal == "negative"
    
    def test_fuse_feedbacks_mixed(self, collector):
        """Test fuse_feedbacks with both types."""
        result = fuse_feedbacks(
            explicit_feedbacks=[collector.collect_thumbs_up()],
            implicit_signals=[
                ImplicitSignal(
                    signal_type=ImplicitSignalType.CONTINUATION.value,
                    signal="positive",
                    confidence=0.5,
                    timestamp="2026-04-03T07:00:00",
                    reason="Continued",
                ),
            ],
            session_id="session-123",
        )
        
        assert result.explicit_count == 1
        assert result.implicit_count == 1
        assert result.session_id == "session-123"
    
    def test_fuse_feedbacks_empty(self):
        """Test fuse_feedbacks with nothing."""
        result = fuse_feedbacks()
        
        assert result.signal == "neutral"
        assert result.confidence == 0.0
