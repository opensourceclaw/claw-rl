"""
Tests for Implicit Feedback Inference

Tests for:
- ImplicitFeedbackInference
- UserAction tracking
- Signal inference from behavior
"""

import pytest
from datetime import datetime, timedelta

from claw_rl.feedback.implicit import (
    ImplicitSignalType,
    UserAction,
    ImplicitSignal,
    ImplicitFeedbackInference,
)


class TestUserAction:
    """Test UserAction dataclass."""
    
    def test_user_action_creation(self):
        """Test creating a UserAction."""
        action = UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:00",
            session_id="session-123",
            content="Hello",
        )
        
        assert action.action_type == "user_message"
        assert action.session_id == "session-123"
        assert action.content == "Hello"
    
    def test_user_action_to_dict(self):
        """Test converting UserAction to dict."""
        action = UserAction(
            action_type="ai_response",
            timestamp="2026-04-03T07:00:01",
            metadata={"model": "gpt-4"},
        )
        
        d = action.to_dict()
        
        assert d["action_type"] == "ai_response"
        assert d["metadata"]["model"] == "gpt-4"


class TestImplicitSignal:
    """Test ImplicitSignal dataclass."""
    
    def test_implicit_signal_creation(self):
        """Test creating an ImplicitSignal."""
        signal = ImplicitSignal(
            signal_type=ImplicitSignalType.RESPONSE_TIME.value,
            signal="positive",
            confidence=0.6,
            timestamp="2026-04-03T07:00:05",
            reason="Fast response time",
        )
        
        assert signal.signal_type == "response_time"
        assert signal.signal == "positive"
        assert signal.confidence == 0.6
    
    def test_implicit_signal_to_dict(self):
        """Test converting ImplicitSignal to dict."""
        signal = ImplicitSignal(
            signal_type=ImplicitSignalType.RETRY_ACTION.value,
            signal="negative",
            confidence=0.7,
            timestamp="2026-04-03T07:00:10",
            reason="Repeated action",
            actions_analyzed=3,
        )
        
        d = signal.to_dict()
        
        assert d["signal_type"] == "retry_action"
        assert d["actions_analyzed"] == 3


class TestImplicitFeedbackInference:
    """Test ImplicitFeedbackInference."""
    
    @pytest.fixture
    def inference(self):
        """Create a fresh inference instance."""
        return ImplicitFeedbackInference()
    
    def test_track_action(self, inference):
        """Test tracking a user action."""
        action = UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:00",
            session_id="session-123",
            content="Hello",
        )
        
        inference.track_action(action)
        
        actions = inference.get_actions()
        assert len(actions) == 1
        assert actions[0].content == "Hello"
    
    def test_track_actions_batch(self, inference):
        """Test tracking multiple actions."""
        actions = [
            UserAction(action_type="user_message", timestamp="2026-04-03T07:00:00"),
            UserAction(action_type="ai_response", timestamp="2026-04-03T07:00:01"),
        ]
        
        inference.track_actions(actions)
        
        assert len(inference.get_actions()) == 2
    
    def test_track_by_session(self, inference):
        """Test tracking actions by session."""
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:00",
            session_id="session-1",
        ))
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:01",
            session_id="session-2",
        ))
        
        assert len(inference.get_actions(session_id="session-1")) == 1
        assert len(inference.get_actions(session_id="session-2")) == 1
    
    def test_infer_fast_response_time_positive(self, inference):
        """Test fast response time yields positive signal."""
        # AI responds at 07:00:00
        inference.track_action(UserAction(
            action_type="ai_response",
            timestamp="2026-04-03T07:00:00",
            session_id="session-1",
        ))
        # User responds quickly at 07:00:05 (5 seconds)
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:05",
            session_id="session-1",
            content="继续",
        ))
        
        signals = inference.infer_signals(session_id="session-1")
        
        # Should have a positive response time signal
        response_signals = [s for s in signals if s.signal_type == "response_time"]
        assert len(response_signals) >= 1
        assert response_signals[0].signal == "positive"
    
    def test_infer_slow_response_time_negative(self, inference):
        """Test very slow response time yields negative signal."""
        # AI responds at 07:00:00
        inference.track_action(UserAction(
            action_type="ai_response",
            timestamp="2026-04-03T07:00:00",
            session_id="session-1",
        ))
        # User responds slowly at 07:05:00 (300 seconds = 5 minutes)
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:05:00",
            session_id="session-1",
            content="让我想想...",
        ))
        
        signals = inference.infer_signals(session_id="session-1")
        
        # Should have a negative response time signal
        response_signals = [s for s in signals if s.signal_type == "response_time"]
        assert len(response_signals) >= 1
        assert response_signals[0].signal == "negative"
    
    def test_infer_retry_negative(self, inference):
        """Test retry pattern yields negative signal."""
        # User sends similar message twice
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:00",
            session_id="session-1",
            content="帮我写一个函数",
        ))
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:30",
            session_id="session-1",
            content="帮我写一个函数",  # Same content
        ))
        
        signals = inference.infer_signals(session_id="session-1")
        
        # Should have a retry signal
        retry_signals = [s for s in signals if s.signal_type == "retry_action"]
        assert len(retry_signals) >= 1
        assert retry_signals[0].signal == "negative"
    
    def test_infer_continuation_positive(self, inference):
        """Test continuation yields positive signal."""
        inference.track_action(UserAction(
            action_type="ai_response",
            timestamp="2026-04-03T07:00:00",
            session_id="session-1",
        ))
        # User continues with new task (no correction words)
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:10",
            session_id="session-1",
            content="好的,下一个问题",
        ))
        
        signals = inference.infer_signals(session_id="session-1")
        
        # Should have a continuation signal
        continuation_signals = [s for s in signals if s.signal_type == "continuation"]
        assert len(continuation_signals) >= 1
        assert continuation_signals[0].signal == "positive"
    
    def test_no_signals_for_empty_actions(self, inference):
        """Test no signals for empty actions."""
        signals = inference.infer_signals(session_id="nonexistent")
        
        assert len(signals) == 0
    
    def test_get_session_summary(self, inference):
        """Test session summary generation."""
        # Add some actions
        inference.track_action(UserAction(
            action_type="ai_response",
            timestamp="2026-04-03T07:00:00",
            session_id="session-1",
        ))
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:05",
            session_id="session-1",
            content="好的",
        ))
        
        summary = inference.get_session_summary("session-1")
        
        assert summary["session_id"] == "session-1"
        assert summary["total_signals"] >= 1
        assert "positive_count" in summary
        assert "negative_count" in summary
        assert "overall_sentiment" in summary
    
    def test_clear_actions(self, inference):
        """Test clearing actions."""
        inference.track_action(UserAction(
            action_type="user_message",
            timestamp="2026-04-03T07:00:00",
        ))
        
        assert len(inference.get_actions()) == 1
        
        inference.clear_actions()
        
        assert len(inference.get_actions()) == 0


class TestSimilarityCalculation:
    """Test text similarity calculation."""
    
    @pytest.fixture
    def inference(self):
        """Create inference instance."""
        return ImplicitFeedbackInference()
    
    def test_identical_texts(self, inference):
        """Test identical texts have similarity 1.0."""
        similarity = inference._calculate_similarity("hello world", "hello world")
        
        assert similarity == 1.0
    
    def test_no_overlap(self, inference):
        """Test texts with no overlap have similarity 0.0."""
        similarity = inference._calculate_similarity("hello world", "foo bar")
        
        assert similarity == 0.0
    
    def test_partial_overlap(self, inference):
        """Test partial overlap."""
        similarity = inference._calculate_similarity("hello world", "hello there")
        
        assert 0 < similarity < 1
    
    def test_empty_texts(self, inference):
        """Test empty texts."""
        assert inference._calculate_similarity("", "hello") == 0.0
        assert inference._calculate_similarity("hello", "") == 0.0
        assert inference._calculate_similarity("", "") == 0.0
