"""
Tests for Protocol Layer

These tests verify the protocol interfaces and data classes.
Since protocols are interfaces, tests focus on:
1. Data class functionality
2. Protocol compliance checking
3. Type safety
"""

import pytest
from datetime import datetime

from claw_rl.protocols import (
    ObserverProtocol,
    DecisionMakerProtocol,
    ExecutorProtocol,
    SignalAdapterProtocol,
)
from claw_rl.protocols.observer import Observation
from claw_rl.protocols.decision_maker import Decision, DecisionType
from claw_rl.protocols.executor import ExecutionResult, ExecutionStatus
from claw_rl.protocols.signal_adapter import AdaptedSignal, SignalType


class TestObservation:
    """Tests for Observation data class."""
    
    def test_create_observation(self):
        """Test creating an observation."""
        obs = Observation(
            timestamp="2026-04-06T10:00:00",
            metrics={"accuracy": 0.95},
            feedback={"rating": 5},
            context={"task": "test"},
            metadata={"source": "unit_test"},
        )
        
        assert obs.timestamp == "2026-04-06T10:00:00"
        assert obs.metrics["accuracy"] == 0.95
        assert obs.feedback["rating"] == 5
        assert obs.context["task"] == "test"
    
    def test_observation_to_dict(self):
        """Test converting observation to dict."""
        obs = Observation(
            timestamp="2026-04-06T10:00:00",
            metrics={"accuracy": 0.95},
            feedback={"rating": 5},
            context={"task": "test"},
            metadata={},
        )
        
        result = obs.to_dict()
        
        assert result["timestamp"] == "2026-04-06T10:00:00"
        assert result["metrics"]["accuracy"] == 0.95
        assert result["feedback"]["rating"] == 5
    
    def test_observation_from_dict(self):
        """Test creating observation from dict."""
        data = {
            "timestamp": "2026-04-06T10:00:00",
            "metrics": {"latency": 100},
            "feedback": {"user_satisfied": True},
            "context": {"environment": "production"},
            "metadata": {"version": "1.0"},
        }
        
        obs = Observation.from_dict(data)
        
        assert obs.timestamp == "2026-04-06T10:00:00"
        assert obs.metrics["latency"] == 100
        assert obs.feedback["user_satisfied"] is True


class TestDecision:
    """Tests for Decision data class."""
    
    def test_create_decision(self):
        """Test creating a decision."""
        decision = Decision(
            decision_id="dec_001",
            decision_type=DecisionType.PARAMETER_ADJUST,
            action="increase_learning_rate",
            parameters={"learning_rate": 0.01},
            confidence=0.9,
        )
        
        assert decision.decision_id == "dec_001"
        assert decision.decision_type == DecisionType.PARAMETER_ADJUST
        assert decision.action == "increase_learning_rate"
        assert decision.confidence == 0.9
    
    def test_decision_auto_timestamp(self):
        """Test that decision gets auto timestamp."""
        decision = Decision(
            decision_id="dec_002",
            decision_type=DecisionType.NO_ACTION,
            action="none",
            parameters={},
            confidence=1.0,
        )
        
        assert decision.timestamp != ""
    
    def test_decision_to_dict(self):
        """Test converting decision to dict."""
        decision = Decision(
            decision_id="dec_003",
            decision_type=DecisionType.STRATEGY_CHANGE,
            action="switch_strategy",
            parameters={"new_strategy": "exploration"},
            confidence=0.8,
            reasoning="Current strategy underperforming",
        )
        
        result = decision.to_dict()
        
        assert result["decision_id"] == "dec_003"
        assert result["decision_type"] == "strategy_change"
        assert result["reasoning"] == "Current strategy underperforming"
    
    def test_decision_from_dict(self):
        """Test creating decision from dict."""
        data = {
            "decision_id": "dec_004",
            "decision_type": "config_update",
            "action": "update_config",
            "parameters": {"batch_size": 32},
            "confidence": 0.95,
            "reasoning": "Test",
        }
        
        decision = Decision.from_dict(data)
        
        assert decision.decision_id == "dec_004"
        assert decision.decision_type == DecisionType.CONFIG_UPDATE
        assert decision.parameters["batch_size"] == 32


class TestExecutionResult:
    """Tests for ExecutionResult data class."""
    
    def test_create_success_result(self):
        """Test creating a success result."""
        result = ExecutionResult(
            decision_id="dec_001",
            status=ExecutionStatus.SUCCESS,
            success=True,
            result={"applied": True},
        )
        
        assert result.decision_id == "dec_001"
        assert result.status == ExecutionStatus.SUCCESS
        assert result.success is True
        assert result.error is None
    
    def test_create_failed_result(self):
        """Test creating a failed result."""
        result = ExecutionResult(
            decision_id="dec_002",
            status=ExecutionStatus.FAILED,
            success=False,
            result={},
            error="Configuration not found",
        )
        
        assert result.status == ExecutionStatus.FAILED
        assert result.success is False
        assert result.error == "Configuration not found"
    
    def test_result_to_dict(self):
        """Test converting result to dict."""
        result = ExecutionResult(
            decision_id="dec_003",
            status=ExecutionStatus.SUCCESS,
            success=True,
            result={"time_ms": 10},
            metrics={"memory_mb": 50},
        )
        
        data = result.to_dict()
        
        assert data["decision_id"] == "dec_003"
        assert data["status"] == "success"
        assert data["result"]["time_ms"] == 10
    
    def test_result_from_dict(self):
        """Test creating result from dict."""
        data = {
            "decision_id": "dec_004",
            "status": "rolled_back",
            "success": False,
            "result": {"rolled_back": True},
            "error": "Failed validation",
        }
        
        result = ExecutionResult.from_dict(data)
        
        assert result.decision_id == "dec_004"
        assert result.status == ExecutionStatus.ROLLED_BACK
        assert result.error == "Failed validation"


class TestAdaptedSignal:
    """Tests for AdaptedSignal data class."""
    
    def test_create_signal(self):
        """Test creating an adapted signal."""
        signal = AdaptedSignal(
            signal_id="sig_001",
            signal_type=SignalType.REWARD,
            source="neoclaw",
            payload={"value": 1.0},
        )
        
        assert signal.signal_id == "sig_001"
        assert signal.signal_type == SignalType.REWARD
        assert signal.source == "neoclaw"
    
    def test_signal_to_reward(self):
        """Test converting signal to reward."""
        signal = AdaptedSignal(
            signal_id="sig_002",
            signal_type=SignalType.REWARD,
            source="test",
            payload={"value": 0.5},
        )
        
        reward = signal.to_reward()
        
        assert reward == 0.5
    
    def test_signal_to_reward_wrong_type(self):
        """Test converting non-reward signal to reward."""
        signal = AdaptedSignal(
            signal_id="sig_003",
            signal_type=SignalType.HINT,
            source="test",
            payload={"text": "try again"},
        )
        
        reward = signal.to_reward()
        
        assert reward is None
    
    def test_signal_to_hint(self):
        """Test converting signal to hint."""
        signal = AdaptedSignal(
            signal_id="sig_004",
            signal_type=SignalType.HINT,
            source="test",
            payload={"text": "increase learning rate"},
        )
        
        hint = signal.to_hint()
        
        assert hint == "increase learning rate"
    
    def test_signal_to_dict(self):
        """Test converting signal to dict."""
        signal = AdaptedSignal(
            signal_id="sig_005",
            signal_type=SignalType.FEEDBACK,
            source="user",
            payload={"rating": 5},
        )
        
        data = signal.to_dict()
        
        assert data["signal_id"] == "sig_005"
        assert data["signal_type"] == "feedback"
        assert data["source"] == "user"
    
    def test_signal_from_dict(self):
        """Test creating signal from dict."""
        data = {
            "signal_id": "sig_006",
            "signal_type": "error",
            "source": "system",
            "payload": {"error_code": 500},
        }
        
        signal = AdaptedSignal.from_dict(data)
        
        assert signal.signal_id == "sig_006"
        assert signal.signal_type == SignalType.ERROR
        assert signal.source == "system"


class TestProtocolCompliance:
    """Tests for protocol compliance."""
    
    def test_observer_protocol_has_methods(self):
        """Test ObserverProtocol has required methods."""
        # Protocol defines interface, check methods exist
        assert hasattr(ObserverProtocol, 'observe')
        assert hasattr(ObserverProtocol, 'get_metrics')
        assert hasattr(ObserverProtocol, 'get_feedback')
        assert hasattr(ObserverProtocol, 'get_context')
        assert hasattr(ObserverProtocol, 'reset')
    
    def test_decision_maker_protocol_has_methods(self):
        """Test DecisionMakerProtocol has required methods."""
        assert hasattr(DecisionMakerProtocol, 'decide')
        assert hasattr(DecisionMakerProtocol, 'get_confidence')
        assert hasattr(DecisionMakerProtocol, 'explain')
        assert hasattr(DecisionMakerProtocol, 'reset')
    
    def test_executor_protocol_has_methods(self):
        """Test ExecutorProtocol has required methods."""
        assert hasattr(ExecutorProtocol, 'execute')
        assert hasattr(ExecutorProtocol, 'rollback')
        assert hasattr(ExecutorProtocol, 'get_status')
        assert hasattr(ExecutorProtocol, 'get_metrics')
        assert hasattr(ExecutorProtocol, 'reset')
    
    def test_signal_adapter_protocol_has_methods(self):
        """Test SignalAdapterProtocol has required methods."""
        assert hasattr(SignalAdapterProtocol, 'adapt')
        assert hasattr(SignalAdapterProtocol, 'adapt_batch')
        assert hasattr(SignalAdapterProtocol, 'detect_type')
        assert hasattr(SignalAdapterProtocol, 'validate')
        assert hasattr(SignalAdapterProtocol, 'get_source_name')


class TestEnums:
    """Tests for enum types."""
    
    def test_decision_type_values(self):
        """Test DecisionType enum values."""
        assert DecisionType.PARAMETER_ADJUST.value == "parameter_adjust"
        assert DecisionType.STRATEGY_CHANGE.value == "strategy_change"
        assert DecisionType.RULE_UPDATE.value == "rule_update"
        assert DecisionType.CONFIG_UPDATE.value == "config_update"
        assert DecisionType.NO_ACTION.value == "no_action"
    
    def test_execution_status_values(self):
        """Test ExecutionStatus enum values."""
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.ROLLED_BACK.value == "rolled_back"
        assert ExecutionStatus.PENDING.value == "pending"
    
    def test_signal_type_values(self):
        """Test SignalType enum values."""
        assert SignalType.REWARD.value == "reward"
        assert SignalType.HINT.value == "hint"
        assert SignalType.FEEDBACK.value == "feedback"
        assert SignalType.ERROR.value == "error"
        assert SignalType.METRIC.value == "metric"
