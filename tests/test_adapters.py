"""
Tests for Adapters

These tests verify the adapter implementations work correctly
and maintain framework independence.
"""

import pytest
from datetime import datetime

from claw_rl.adapters import (
    BaseObserverAdapter,
    BaseDecisionMakerAdapter,
    BaseExecutorAdapter,
    BaseSignalAdapter,
    OpenClawObserverAdapter,
    OpenClawSignalAdapter,
)
from claw_rl.protocols.observer import Observation
from claw_rl.protocols.decision_maker import DecisionType
from claw_rl.protocols.executor import ExecutionStatus
from claw_rl.protocols.signal_adapter import SignalType


class TestBaseObserverAdapter:
    """Tests for BaseObserverAdapter."""
    
    def test_create_observer(self):
        """Test creating a base observer."""
        observer = BaseObserverAdapter(source_name="test")
        assert observer.source_name == "test"
    
    def test_observe(self):
        """Test collecting observation."""
        observer = BaseObserverAdapter(source_name="test")
        observer.update_metrics({"accuracy": 0.95})
        observer.update_feedback({"rating": 5})
        observer.update_context({"task": "classification"})
        
        obs = observer.observe()
        
        assert isinstance(obs, Observation)
        assert obs.metrics["accuracy"] == 0.95
        assert obs.feedback["rating"] == 5
        assert obs.context["task"] == "classification"
        assert obs.metadata["source"] == "test"
    
    def test_get_metrics(self):
        """Test getting metrics."""
        observer = BaseObserverAdapter()
        observer.update_metrics({"accuracy": 0.9, "latency_ms": 100})
        
        metrics = observer.get_metrics()
        
        assert metrics["accuracy"] == 0.9
        assert metrics["latency_ms"] == 100
    
    def test_get_feedback(self):
        """Test getting feedback."""
        observer = BaseObserverAdapter()
        observer.update_feedback({"user_rating": 4.5})
        
        feedback = observer.get_feedback()
        
        assert feedback["user_rating"] == 4.5
    
    def test_get_context(self):
        """Test getting context."""
        observer = BaseObserverAdapter()
        observer.update_context({"environment": "production"})
        
        context = observer.get_context()
        
        assert context["environment"] == "production"
    
    def test_reset(self):
        """Test resetting observer."""
        observer = BaseObserverAdapter()
        observer.update_metrics({"accuracy": 0.9})
        observer.update_feedback({"rating": 5})
        observer.update_context({"task": "test"})
        
        observer.reset()
        
        assert observer.get_metrics() == {}
        assert observer.get_feedback() == {}
        assert observer.get_context() == {}


class TestBaseDecisionMakerAdapter:
    """Tests for BaseDecisionMakerAdapter."""
    
    def test_create_decision_maker(self):
        """Test creating a base decision maker."""
        dm = BaseDecisionMakerAdapter(source_name="test")
        assert dm.source_name == "test"
    
    def test_decide(self):
        """Test making a decision."""
        dm = BaseDecisionMakerAdapter()
        
        decision = dm.decide({"accuracy": 0.8})
        
        assert decision.decision_type == DecisionType.NO_ACTION
        assert decision.action == "none"
        assert decision.confidence == 1.0
    
    def test_get_confidence(self):
        """Test getting confidence."""
        dm = BaseDecisionMakerAdapter()
        
        confidence = dm.get_confidence({"accuracy": 0.9})
        
        assert confidence == 1.0
    
    def test_explain(self):
        """Test explaining decision."""
        dm = BaseDecisionMakerAdapter()
        decision = dm.decide({})
        
        explanation = dm.explain(decision)
        
        assert "Decision" in explanation
    
    def test_reset(self):
        """Test resetting decision maker."""
        dm = BaseDecisionMakerAdapter()
        dm.decide({})
        dm.decide({})
        
        dm.reset()
        
        assert dm._decision_count == 0


class TestBaseExecutorAdapter:
    """Tests for BaseExecutorAdapter."""
    
    def test_create_executor(self):
        """Test creating a base executor."""
        executor = BaseExecutorAdapter(source_name="test")
        assert executor.source_name == "test"
    
    def test_execute(self):
        """Test executing a decision."""
        executor = BaseExecutorAdapter()
        
        result = executor.execute({"decision_id": "dec_001"})
        
        assert result.success
        assert result.status == ExecutionStatus.SUCCESS
    
    def test_rollback(self):
        """Test rolling back a decision."""
        executor = BaseExecutorAdapter()
        executor.execute({"decision_id": "dec_001"})
        
        result = executor.rollback("dec_001")
        
        assert result.success
        assert result.status == ExecutionStatus.ROLLED_BACK
    
    def test_rollback_not_found(self):
        """Test rolling back non-existent decision."""
        executor = BaseExecutorAdapter()
        
        result = executor.rollback("nonexistent")
        
        assert not result.success
        assert result.status == ExecutionStatus.FAILED
    
    def test_get_status(self):
        """Test getting execution status."""
        executor = BaseExecutorAdapter()
        executor.execute({"decision_id": "dec_001"})
        
        status = executor.get_status("dec_001")
        
        assert status == ExecutionStatus.SUCCESS
    
    def test_get_status_not_found(self):
        """Test getting status of non-existent decision."""
        executor = BaseExecutorAdapter()
        
        status = executor.get_status("nonexistent")
        
        assert status is None
    
    def test_get_metrics(self):
        """Test getting executor metrics."""
        executor = BaseExecutorAdapter()
        executor.execute({"decision_id": "dec_001"})
        
        metrics = executor.get_metrics()
        
        assert metrics["total_executions"] == 1
        assert metrics["success_count"] == 1
        assert metrics["success_rate"] == 1.0
    
    def test_reset(self):
        """Test resetting executor."""
        executor = BaseExecutorAdapter()
        executor.execute({"decision_id": "dec_001"})
        
        executor.reset()
        
        metrics = executor.get_metrics()
        assert metrics["total_executions"] == 0


class TestBaseSignalAdapter:
    """Tests for BaseSignalAdapter."""
    
    def test_create_signal_adapter(self):
        """Test creating a base signal adapter."""
        adapter = BaseSignalAdapter(source_name="test")
        assert adapter.source_name == "test"
    
    def test_adapt(self):
        """Test adapting a signal."""
        adapter = BaseSignalAdapter()
        
        signal = adapter.adapt({"test": "data"})
        
        assert signal.source == "base"
        assert signal.signal_type in [SignalType.FEEDBACK, SignalType.REWARD]
    
    def test_adapt_batch(self):
        """Test adapting multiple signals."""
        adapter = BaseSignalAdapter()
        
        signals = adapter.adapt_batch([{"a": 1}, {"b": 2}])
        
        assert len(signals) == 2
    
    def test_detect_type_reward(self):
        """Test detecting reward type."""
        adapter = BaseSignalAdapter()
        
        signal_type = adapter.detect_type({"reward": 1.0})
        
        assert signal_type == SignalType.REWARD
    
    def test_detect_type_hint(self):
        """Test detecting hint type."""
        adapter = BaseSignalAdapter()
        
        signal_type = adapter.detect_type({"hint": "try again"})
        
        assert signal_type == SignalType.HINT
    
    def test_detect_type_error(self):
        """Test detecting error type."""
        adapter = BaseSignalAdapter()
        
        signal_type = adapter.detect_type({"error": "something went wrong"})
        
        assert signal_type == SignalType.ERROR
    
    def test_detect_type_metric(self):
        """Test detecting metric type."""
        adapter = BaseSignalAdapter()
        
        signal_type = adapter.detect_type({"metric": 0.95})
        
        assert signal_type == SignalType.METRIC
    
    def test_detect_type_feedback(self):
        """Test detecting feedback type (default)."""
        adapter = BaseSignalAdapter()
        
        signal_type = adapter.detect_type({"unknown": "data"})
        
        assert signal_type == SignalType.FEEDBACK
    
    def test_validate(self):
        """Test validating signals."""
        adapter = BaseSignalAdapter()
        
        assert adapter.validate({"test": "data"}) is True
        assert adapter.validate(None) is False
    
    def test_get_source_name(self):
        """Test getting source name."""
        adapter = BaseSignalAdapter(source_name="custom")
        
        assert adapter.get_source_name() == "custom"


class TestOpenClawObserverAdapter:
    """Tests for OpenClawObserverAdapter."""
    
    def test_create_observer(self):
        """Test creating OpenClaw observer."""
        observer = OpenClawObserverAdapter()
        assert observer.source_name == "openclaw"
    
    def test_observe(self):
        """Test collecting observation."""
        observer = OpenClawObserverAdapter()
        
        obs = observer.observe()
        
        assert obs.metadata["source"] == "openclaw"
    
    def test_update_from_session_start(self):
        """Test updating from session start event."""
        observer = OpenClawObserverAdapter()
        
        observer.update_from_event({
            "type": "session_start",
            "session_id": "sess_001",
            "model": "gpt-4",
            "channel": "telegram",
        })
        
        obs = observer.observe()
        
        assert obs.metadata["session_id"] == "sess_001"
        assert obs.context["model"] == "gpt-4"
        assert obs.context["channel"] == "telegram"
    
    def test_update_from_tool_call(self):
        """Test updating from tool call event."""
        observer = OpenClawObserverAdapter()
        
        # Successful tool call
        observer.update_from_event({
            "type": "tool_call",
            "success": True,
        })
        
        # Failed tool call
        observer.update_from_event({
            "type": "tool_call",
            "success": False,
        })
        
        obs = observer.observe()
        
        assert obs.metrics["tool_calls"] == 2
        assert obs.metrics["success_rate"] == 0.5
        assert obs.feedback["error_count"] == 1
    
    def test_update_from_feedback(self):
        """Test updating from feedback event."""
        observer = OpenClawObserverAdapter()
        
        observer.update_from_event({
            "type": "feedback",
            "rating": 5,
            "feedback": "Great response!",
        })
        
        obs = observer.observe()
        
        assert obs.feedback["user_rating"] == 5
        assert obs.feedback["explicit_feedback"] == "Great response!"
    
    def test_reset(self):
        """Test resetting observer."""
        observer = OpenClawObserverAdapter()
        observer.update_from_event({
            "type": "session_start",
            "session_id": "sess_001",
        })
        
        observer.reset()
        
        assert observer._session_data == {}


class TestOpenClawSignalAdapter:
    """Tests for OpenClawSignalAdapter."""
    
    def test_create_adapter(self):
        """Test creating OpenClaw adapter."""
        adapter = OpenClawSignalAdapter()
        assert adapter.source_name == "openclaw"
    
    def test_adapt_feedback_event(self):
        """Test adapting feedback event."""
        adapter = OpenClawSignalAdapter()
        
        signal = adapter.adapt({
            "type": "feedback",
            "id": "fb_001",
            "rating": 5,
            "feedback": "Excellent!",
        })
        
        assert signal.signal_type == SignalType.FEEDBACK
        assert signal.source == "openclaw"
        assert signal.payload["rating"] == 5
    
    def test_adapt_tool_result_success(self):
        """Test adapting successful tool result."""
        adapter = OpenClawSignalAdapter()
        
        signal = adapter.adapt({
            "type": "tool_result",
            "id": "tr_001",
            "success": True,
            "tool_name": "read_file",
        })
        
        assert signal.signal_type == SignalType.REWARD
        assert signal.payload["value"] == 1.0
    
    def test_adapt_tool_result_failure(self):
        """Test adapting failed tool result."""
        adapter = OpenClawSignalAdapter()
        
        signal = adapter.adapt({
            "type": "tool_result",
            "id": "tr_002",
            "success": False,
            "tool_name": "read_file",
        })
        
        assert signal.signal_type == SignalType.ERROR
        assert signal.payload["value"] == -1.0
    
    def test_adapt_error_event(self):
        """Test adapting error event."""
        adapter = OpenClawSignalAdapter()
        
        signal = adapter.adapt({
            "type": "error",
            "id": "err_001",
            "error_code": "TIMEOUT",
            "error_message": "Request timed out",
        })
        
        assert signal.signal_type == SignalType.ERROR
        assert signal.payload["error_code"] == "TIMEOUT"
    
    def test_adapt_metric_event(self):
        """Test adapting metric event."""
        adapter = OpenClawSignalAdapter()
        
        signal = adapter.adapt({
            "type": "metric",
            "id": "m_001",
            "metric_name": "latency",
            "metric_value": 150,
            "unit": "ms",
        })
        
        assert signal.signal_type == SignalType.METRIC
        assert signal.payload["metric_name"] == "latency"
    
    def test_adapt_unknown_event(self):
        """Test adapting unknown event type."""
        adapter = OpenClawSignalAdapter()
        
        signal = adapter.adapt({
            "type": "unknown",
            "data": "test",
        })
        
        assert signal.signal_type == SignalType.FEEDBACK
        assert signal.source == "openclaw"
    
    def test_adapt_non_dict(self):
        """Test adapting non-dict signal."""
        adapter = OpenClawSignalAdapter()
        
        signal = adapter.adapt("raw string")
        
        assert signal.signal_type == SignalType.FEEDBACK
        assert "raw" in signal.payload
    
    def test_validate_valid_event(self):
        """Test validating valid event."""
        adapter = OpenClawSignalAdapter()
        
        assert adapter.validate({"type": "feedback"}) is True
    
    def test_validate_invalid_event(self):
        """Test validating invalid event."""
        adapter = OpenClawSignalAdapter()
        
        assert adapter.validate({"no_type": "here"}) is False
        assert adapter.validate("not a dict") is False
        assert adapter.validate(None) is False
    
    def test_get_source_name(self):
        """Test getting source name."""
        adapter = OpenClawSignalAdapter()
        
        assert adapter.get_source_name() == "openclaw"
