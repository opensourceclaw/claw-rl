"""
OpenClaw Adapter - Adapter for OpenClaw Gateway

This module provides adapters for integrating with OpenClaw Gateway.
Note: This adapter works with OpenClaw Gateway events and does NOT
depend on neoclaw, maintaining framework independence per ADR-008.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from ..protocols.observer import Observation
from ..protocols.decision_maker import Decision, DecisionType
from ..protocols.executor import ExecutionResult, ExecutionStatus
from ..protocols.signal_adapter import AdaptedSignal, SignalType
from .base_adapter import (
    BaseObserverAdapter,
    BaseDecisionMakerAdapter,
    BaseExecutorAdapter,
    BaseSignalAdapter,
)


class OpenClawObserverAdapter(BaseObserverAdapter):
    """
    Observer adapter for OpenClaw Gateway.
    
    Collects observations from OpenClaw Gateway events:
    - Session events
    - Tool call metrics
    - Feedback signals
    
    This adapter does NOT depend on neoclaw.
    """
    
    def __init__(self):
        """Initialize OpenClaw Observer Adapter."""
        super().__init__(source_name="openclaw")
        self._session_data: Dict[str, Any] = {}
    
    def observe(self) -> Observation:
        """
        Collect and return an observation.
        
        Returns:
            Observation with OpenClaw-specific metrics
        """
        # Extract metrics from session data
        metrics = self._extract_metrics()
        feedback = self._extract_feedback()
        context = self._extract_context()
        
        return Observation(
            timestamp=datetime.now().isoformat(),
            metrics=metrics,
            feedback=feedback,
            context=context,
            metadata={
                "source": "openclaw",
                "session_id": self._session_data.get("session_id", ""),
            },
        )
    
    def _extract_metrics(self) -> Dict[str, Any]:
        """Extract metrics from session data."""
        return {
            "tool_calls": self._session_data.get("tool_calls", 0),
            "success_rate": self._session_data.get("success_rate", 0.0),
            "latency_ms": self._session_data.get("latency_ms", 0),
            "token_usage": self._session_data.get("token_usage", {}),
        }
    
    def _extract_feedback(self) -> Dict[str, Any]:
        """Extract feedback from session data."""
        return {
            "user_rating": self._session_data.get("user_rating", 0),
            "explicit_feedback": self._session_data.get("explicit_feedback", ""),
            "error_count": self._session_data.get("error_count", 0),
        }
    
    def _extract_context(self) -> Dict[str, Any]:
        """Extract context from session data."""
        return {
            "model": self._session_data.get("model", ""),
            "channel": self._session_data.get("channel", ""),
            "task_type": self._session_data.get("task_type", ""),
        }
    
    def update_from_event(self, event: Dict[str, Any]) -> None:
        """
        Update observer from OpenClaw Gateway event.
        
        Args:
            event: OpenClaw Gateway event
        """
        event_type = event.get("type", "")
        
        if event_type == "session_start":
            self._session_data["session_id"] = event.get("session_id", "")
            self._session_data["model"] = event.get("model", "")
            self._session_data["channel"] = event.get("channel", "")
        
        elif event_type == "tool_call":
            self._session_data["tool_calls"] = self._session_data.get("tool_calls", 0) + 1
            if event.get("success", True):
                self._session_data["success_count"] = self._session_data.get("success_count", 0) + 1
            else:
                self._session_data["error_count"] = self._session_data.get("error_count", 0) + 1
        
        elif event_type == "feedback":
            self._session_data["user_rating"] = event.get("rating", 0)
            self._session_data["explicit_feedback"] = event.get("feedback", "")
        
        # Update success rate
        total = self._session_data.get("tool_calls", 0)
        success = self._session_data.get("success_count", 0)
        if total > 0:
            self._session_data["success_rate"] = success / total
    
    def reset(self) -> None:
        """Reset observer state."""
        super().reset()
        self._session_data.clear()


class OpenClawSignalAdapter(BaseSignalAdapter):
    """
    Signal adapter for OpenClaw Gateway.
    
    Converts OpenClaw Gateway events to common signal format.
    
    This adapter does NOT depend on neoclaw.
    """
    
    def __init__(self):
        """Initialize OpenClaw Signal Adapter."""
        super().__init__(source_name="openclaw")
    
    def adapt(self, raw_signal: Any) -> AdaptedSignal:
        """
        Adapt an OpenClaw Gateway event to common format.
        
        Args:
            raw_signal: OpenClaw Gateway event
            
        Returns:
            AdaptedSignal in common format
        """
        self._signal_count += 1
        
        if not isinstance(raw_signal, dict):
            return self._adapt_unknown(raw_signal)
        
        event_type = raw_signal.get("type", "")
        
        if event_type == "feedback":
            return self._adapt_feedback(raw_signal)
        elif event_type == "tool_result":
            return self._adapt_tool_result(raw_signal)
        elif event_type == "error":
            return self._adapt_error(raw_signal)
        elif event_type == "metric":
            return self._adapt_metric(raw_signal)
        else:
            return self._adapt_generic(raw_signal)
    
    def _adapt_feedback(self, event: Dict[str, Any]) -> AdaptedSignal:
        """Adapt feedback event."""
        return AdaptedSignal(
            signal_id=event.get("id", f"sig_{self._signal_count:04d}"),
            signal_type=SignalType.FEEDBACK,
            source="openclaw",
            payload={
                "rating": event.get("rating", 0),
                "feedback": event.get("feedback", ""),
                "user_id": event.get("user_id", ""),
                "session_id": event.get("session_id", ""),
            },
        )
    
    def _adapt_tool_result(self, event: Dict[str, Any]) -> AdaptedSignal:
        """Adapt tool result event."""
        success = event.get("success", True)
        signal_type = SignalType.REWARD if success else SignalType.ERROR
        
        return AdaptedSignal(
            signal_id=event.get("id", f"sig_{self._signal_count:04d}"),
            signal_type=signal_type,
            source="openclaw",
            payload={
                "value": 1.0 if success else -1.0,
                "tool_name": event.get("tool_name", ""),
                "execution_time_ms": event.get("execution_time_ms", 0),
                "session_id": event.get("session_id", ""),
            },
        )
    
    def _adapt_error(self, event: Dict[str, Any]) -> AdaptedSignal:
        """Adapt error event."""
        return AdaptedSignal(
            signal_id=event.get("id", f"sig_{self._signal_count:04d}"),
            signal_type=SignalType.ERROR,
            source="openclaw",
            payload={
                "error_code": event.get("error_code", ""),
                "error_message": event.get("error_message", ""),
                "context": event.get("context", {}),
            },
        )
    
    def _adapt_metric(self, event: Dict[str, Any]) -> AdaptedSignal:
        """Adapt metric event."""
        return AdaptedSignal(
            signal_id=event.get("id", f"sig_{self._signal_count:04d}"),
            signal_type=SignalType.METRIC,
            source="openclaw",
            payload={
                "metric_name": event.get("metric_name", ""),
                "metric_value": event.get("metric_value", 0),
                "unit": event.get("unit", ""),
                "timestamp": event.get("timestamp", datetime.now().isoformat()),
            },
        )
    
    def _adapt_generic(self, event: Dict[str, Any]) -> AdaptedSignal:
        """Adapt generic event."""
        return AdaptedSignal(
            signal_id=event.get("id", f"sig_{self._signal_count:04d}"),
            signal_type=self.detect_type(event),
            source="openclaw",
            payload=event,
        )
    
    def _adapt_unknown(self, raw_signal: Any) -> AdaptedSignal:
        """Adapt unknown signal type."""
        return AdaptedSignal(
            signal_id=f"sig_{self._signal_count:04d}",
            signal_type=SignalType.FEEDBACK,
            source="openclaw",
            payload={"raw": str(raw_signal)},
        )
    
    def detect_type(self, raw_signal: Any) -> SignalType:
        """
        Detect the type of an OpenClaw Gateway event.
        
        Args:
            raw_signal: OpenClaw Gateway event
            
        Returns:
            Detected signal type
        """
        if not isinstance(raw_signal, dict):
            return SignalType.FEEDBACK
        
        event_type = raw_signal.get("type", "")
        
        type_mapping = {
            "feedback": SignalType.FEEDBACK,
            "tool_result": SignalType.REWARD if raw_signal.get("success", True) else SignalType.ERROR,
            "error": SignalType.ERROR,
            "metric": SignalType.METRIC,
            "hint": SignalType.HINT,
        }
        
        return type_mapping.get(event_type, SignalType.FEEDBACK)
    
    def validate(self, raw_signal: Any) -> bool:
        """
        Validate an OpenClaw Gateway event.
        
        Args:
            raw_signal: OpenClaw Gateway event
            
        Returns:
            True if event is valid
        """
        if not isinstance(raw_signal, dict):
            return False
        
        # Must have type field
        if "type" not in raw_signal:
            return False
        
        return True
    
    def get_source_name(self) -> str:
        """Get the name of the source framework."""
        return "openclaw"
