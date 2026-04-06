"""
Base Adapters - Base implementations for protocol adapters

This module provides base implementations that can be extended
for specific frameworks.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from ..protocols.observer import ObserverProtocol, Observation
from ..protocols.decision_maker import DecisionMakerProtocol, Decision, DecisionType
from ..protocols.executor import ExecutorProtocol, ExecutionResult, ExecutionStatus
from ..protocols.signal_adapter import SignalAdapterProtocol, AdaptedSignal, SignalType


class BaseObserverAdapter(ObserverProtocol):
    """
    Base implementation of ObserverProtocol.
    
    Provides common functionality for observation collection.
    Can be extended for specific frameworks.
    """
    
    def __init__(self, source_name: str = "base"):
        """
        Initialize Base Observer Adapter.
        
        Args:
            source_name: Name of the source framework
        """
        self.source_name = source_name
        self._metrics: Dict[str, Any] = {}
        self._feedback: Dict[str, Any] = {}
        self._context: Dict[str, Any] = {}
    
    def observe(self) -> Observation:
        """
        Collect and return an observation.
        
        Returns:
            Observation with current metrics, feedback, and context
        """
        return Observation(
            timestamp=datetime.now().isoformat(),
            metrics=self._metrics.copy(),
            feedback=self._feedback.copy(),
            context=self._context.copy(),
            metadata={"source": self.source_name},
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self._metrics.copy()
    
    def get_feedback(self) -> Dict[str, Any]:
        """Get available feedback signals."""
        return self._feedback.copy()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context information."""
        return self._context.copy()
    
    def reset(self) -> None:
        """Reset observer state."""
        self._metrics.clear()
        self._feedback.clear()
        self._context.clear()
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Update metrics (helper method for subclasses).
        
        Args:
            metrics: Metrics to update
        """
        self._metrics.update(metrics)
    
    def update_feedback(self, feedback: Dict[str, Any]) -> None:
        """
        Update feedback (helper method for subclasses).
        
        Args:
            feedback: Feedback to update
        """
        self._feedback.update(feedback)
    
    def update_context(self, context: Dict[str, Any]) -> None:
        """
        Update context (helper method for subclasses).
        
        Args:
            context: Context to update
        """
        self._context.update(context)


class BaseDecisionMakerAdapter(DecisionMakerProtocol):
    """
    Base implementation of DecisionMakerProtocol.
    
    Provides common functionality for decision making.
    Can be extended for specific frameworks.
    """
    
    def __init__(self, source_name: str = "base"):
        """
        Initialize Base Decision Maker Adapter.
        
        Args:
            source_name: Name of the source framework
        """
        self.source_name = source_name
        self._decision_count = 0
    
    def decide(self, observations: Dict[str, Any]) -> Decision:
        """
        Make a decision based on observations.
        
        Args:
            observations: Dictionary of observations
            
        Returns:
            Decision containing action to take
        """
        self._decision_count += 1
        
        # Default: no action needed
        return Decision(
            decision_id=f"dec_{self._decision_count:04d}",
            decision_type=DecisionType.NO_ACTION,
            action="none",
            parameters={},
            confidence=1.0,
            reasoning="Base adapter: no specific decision logic",
        )
    
    def get_confidence(self, observations: Dict[str, Any]) -> float:
        """
        Get confidence score for potential decision.
        
        Args:
            observations: Dictionary of observations
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        # Default: high confidence for no-action
        return 1.0
    
    def explain(self, decision: Decision) -> str:
        """
        Explain the reasoning behind a decision.
        
        Args:
            decision: Decision to explain
            
        Returns:
            Human-readable explanation
        """
        return f"Decision {decision.decision_id}: {decision.reasoning}"
    
    def reset(self) -> None:
        """Reset decision maker state."""
        self._decision_count = 0


class BaseExecutorAdapter(ExecutorProtocol):
    """
    Base implementation of ExecutorProtocol.
    
    Provides common functionality for decision execution.
    Can be extended for specific frameworks.
    """
    
    def __init__(self, source_name: str = "base"):
        """
        Initialize Base Executor Adapter.
        
        Args:
            source_name: Name of the source framework
        """
        self.source_name = source_name
        self._execution_history: Dict[str, ExecutionResult] = {}
        self._metrics = {
            "total_executions": 0,
            "success_count": 0,
            "failure_count": 0,
            "rollback_count": 0,
        }
    
    def execute(self, decision: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a decision.
        
        Args:
            decision: Decision to execute
            
        Returns:
            ExecutionResult containing outcome
        """
        decision_id = decision.get("decision_id", str(uuid.uuid4()))
        self._metrics["total_executions"] += 1
        
        # Default: successful execution (no-op)
        result = ExecutionResult(
            decision_id=decision_id,
            status=ExecutionStatus.SUCCESS,
            success=True,
            result={"executed": True, "action": "none"},
            metrics={"time_ms": 0},
        )
        
        self._execution_history[decision_id] = result
        self._metrics["success_count"] += 1
        
        return result
    
    def rollback(self, decision_id: str) -> ExecutionResult:
        """
        Rollback a previously executed decision.
        
        Args:
            decision_id: ID of decision to rollback
            
        Returns:
            ExecutionResult of rollback
        """
        if decision_id not in self._execution_history:
            return ExecutionResult(
                decision_id=decision_id,
                status=ExecutionStatus.FAILED,
                success=False,
                result={},
                error="Decision not found in history",
            )
        
        # Mark as rolled back
        self._execution_history[decision_id].status = ExecutionStatus.ROLLED_BACK
        self._metrics["rollback_count"] += 1
        
        return ExecutionResult(
            decision_id=decision_id,
            status=ExecutionStatus.ROLLED_BACK,
            success=True,
            result={"rolled_back": True},
        )
    
    def get_status(self, decision_id: str) -> Optional[ExecutionStatus]:
        """
        Get execution status of a decision.
        
        Args:
            decision_id: Decision ID
            
        Returns:
            Execution status, or None if not found
        """
        if decision_id in self._execution_history:
            return self._execution_history[decision_id].status
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get executor metrics."""
        metrics = self._metrics.copy()
        if metrics["total_executions"] > 0:
            metrics["success_rate"] = metrics["success_count"] / metrics["total_executions"]
            metrics["avg_execution_time"] = 0  # Base adapter: no timing
        return metrics
    
    def reset(self) -> None:
        """Reset executor state."""
        self._execution_history.clear()
        self._metrics = {
            "total_executions": 0,
            "success_count": 0,
            "failure_count": 0,
            "rollback_count": 0,
        }


class BaseSignalAdapter(SignalAdapterProtocol):
    """
    Base implementation of SignalAdapterProtocol.
    
    Provides common functionality for signal adaptation.
    Can be extended for specific frameworks.
    """
    
    def __init__(self, source_name: str = "base"):
        """
        Initialize Base Signal Adapter.
        
        Args:
            source_name: Name of the source framework
        """
        self.source_name = source_name
        self._signal_count = 0
    
    def adapt(self, raw_signal: Any) -> AdaptedSignal:
        """
        Adapt a framework-specific signal to common format.
        
        Args:
            raw_signal: Framework-specific signal
            
        Returns:
            AdaptedSignal in common format
        """
        self._signal_count += 1
        
        # Default: treat as generic signal
        return AdaptedSignal(
            signal_id=f"sig_{self._signal_count:04d}",
            signal_type=self.detect_type(raw_signal),
            source=self.source_name,
            payload={"raw": str(raw_signal)},
        )
    
    def adapt_batch(self, raw_signals: List[Any]) -> List[AdaptedSignal]:
        """
        Adapt multiple signals.
        
        Args:
            raw_signals: List of framework-specific signals
            
        Returns:
            List of adapted signals
        """
        return [self.adapt(signal) for signal in raw_signals]
    
    def detect_type(self, raw_signal: Any) -> SignalType:
        """
        Detect the type of a raw signal.
        
        Args:
            raw_signal: Framework-specific signal
            
        Returns:
            Detected signal type
        """
        # Default: treat as feedback
        if isinstance(raw_signal, dict):
            if "reward" in raw_signal or "value" in raw_signal:
                return SignalType.REWARD
            if "hint" in raw_signal or "suggestion" in raw_signal:
                return SignalType.HINT
            if "error" in raw_signal:
                return SignalType.ERROR
            if "metric" in raw_signal or "metrics" in raw_signal:
                return SignalType.METRIC
        
        return SignalType.FEEDBACK
    
    def validate(self, raw_signal: Any) -> bool:
        """
        Validate a raw signal.
        
        Args:
            raw_signal: Framework-specific signal
            
        Returns:
            True if signal is valid
        """
        # Default: all signals are valid
        return raw_signal is not None
    
    def get_source_name(self) -> str:
        """Get the name of the source framework."""
        return self.source_name
