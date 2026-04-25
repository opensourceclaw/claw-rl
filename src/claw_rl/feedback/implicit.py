"""
Implicit Feedback Inference - Infer feedback from user behavior

This module infers implicit feedback signals from user behavior patterns,
such as response time, retry actions, and session context.
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math


class ImplicitSignalType(Enum):
    """Types of implicit feedback signals."""
    RESPONSE_TIME = "response_time"       # How fast user responded
    RETRY_ACTION = "retry_action"         # User retried an action
    CONTINUATION = "continuation"         # User continued without complaint
    ABANDONMENT = "abandonment"           # User abandoned the session
    REPHRASE = "rephrase"                 # User rephrased the question
    ACCEPTANCE = "acceptance"             # User accepted without feedback
    EDIT_DISTANCE = "edit_distance"       # How much user edited output


@dataclass
class UserAction:
    """Record of a user action."""
    action_type: str                      # Type of action
    timestamp: str                        # ISO 8601 timestamp
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    content: Optional[str] = None         # Action content
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "action_type": self.action_type,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "content": self.content,
            "metadata": self.metadata,
        }


@dataclass
class ImplicitSignal:
    """Inferred implicit feedback signal."""
    signal_type: str                      # ImplicitSignalType value
    signal: str                           # "positive", "negative", "neutral", or extended
    confidence: float                     # 0.0 to 1.0
    timestamp: str
    reason: str                           # Why this signal was inferred
    session_id: Optional[str] = None
    actions_analyzed: int = 1             # Number of actions analyzed
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "signal_type": self.signal_type,
            "signal": self.signal,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "session_id": self.session_id,
            "actions_analyzed": self.actions_analyzed,
            "metadata": self.metadata,
        }


class ImplicitFeedbackInference:
    """
    Infer implicit feedback from user behavior.
    
    Analyzes user actions to infer satisfaction levels:
    - Fast response → likely satisfied
    - Retry/rephrase → likely unsatisfied
    - Continuation without feedback → likely satisfied
    - Abandonment → likely unsatisfied
    
    Example:
        >>> inference = ImplicitFeedbackInference()
        >>> 
        >>> # Track user action
        >>> action = UserAction(
        ...     action_type="message",
        ...     timestamp="2026-04-03T07:00:00",
        ...     session_id="session-123",
        ... )
        >>> inference.track_action(action)
        >>> 
        >>> # Analyze and infer
        >>> signals = inference.infer_signals(session_id="session-123")
        >>> print(signals[0].signal)
        'positive'
    """
    
    # Thresholds for response time analysis
    FAST_RESPONSE_THRESHOLD_SEC = 10      # < 10s = fast (positive)
    SLOW_RESPONSE_THRESHOLD_SEC = 60      # > 60s = slow (may be negative)
    VERY_SLOW_RESPONSE_THRESHOLD_SEC = 180  # > 180s = very slow (likely negative)
    
    # Thresholds for edit distance
    LOW_EDIT_DISTANCE_THRESHOLD = 0.2     # < 20% changed = positive
    HIGH_EDIT_DISTANCE_THRESHOLD = 0.5    # > 50% changed = negative
    
    def __init__(self):
        """Initialize ImplicitFeedbackInference."""
        self._actions: List[UserAction] = []
        self._session_actions: Dict[str, List[UserAction]] = {}
    
    def track_action(self, action: UserAction) -> None:
        """
        Track a user action.
        
        Args:
            action: User action to track
        """
        self._actions.append(action)
        
        # Also track by session
        if action.session_id:
            if action.session_id not in self._session_actions:
                self._session_actions[action.session_id] = []
            self._session_actions[action.session_id].append(action)
    
    def track_actions(self, actions: List[UserAction]) -> None:
        """
        Track multiple user actions.
        
        Args:
            actions: List of user actions to track
        """
        for action in actions:
            self.track_action(action)
    
    def infer_signals(
        self,
        session_id: Optional[str] = None,
        actions: Optional[List[UserAction]] = None,
    ) -> List[ImplicitSignal]:
        """
        Infer implicit feedback signals from tracked actions.
        
        Args:
            session_id: Session ID to analyze (uses session actions)
            actions: Specific actions to analyze (overrides session_id)
        
        Returns:
            List of inferred implicit signals
        """
        # Get actions to analyze
        if actions:
            actions_to_analyze = actions
        elif session_id:
            actions_to_analyze = self._session_actions.get(session_id, [])
        else:
            actions_to_analyze = self._actions
        
        if not actions_to_analyze:
            return []
        
        signals = []
        
        # Analyze different signal types
        signals.extend(self._analyze_response_time(actions_to_analyze, session_id))
        signals.extend(self._analyze_retry_patterns(actions_to_analyze, session_id))
        signals.extend(self._analyze_continuation(actions_to_analyze, session_id))
        signals.extend(self._analyze_abandonment(actions_to_analyze, session_id))
        signals.extend(self._analyze_rephrase(actions_to_analyze, session_id))
        
        return signals
    
    def _analyze_response_time(
        self,
        actions: List[UserAction],
        session_id: Optional[str] = None,
    ) -> List[ImplicitSignal]:
        """
        Analyze response time patterns.
        
        Fast response → likely satisfied
        Slow response → may indicate confusion
        
        Args:
            actions: Actions to analyze
            session_id: Session ID
        
        Returns:
            List of implicit signals
        """
        signals = []
        
        # Find message pairs (AI response → user next message)
        for i, action in enumerate(actions):
            if action.action_type == "ai_response":
                # Find next user message
                for j in range(i + 1, len(actions)):
                    next_action = actions[j]
                    if next_action.action_type == "user_message":
                        # Calculate response time
                        try:
                            ai_time = datetime.fromisoformat(action.timestamp)
                            user_time = datetime.fromisoformat(next_action.timestamp)
                            response_time_sec = (user_time - ai_time).total_seconds()
                            
                            # Infer signal based on response time
                            if response_time_sec < self.FAST_RESPONSE_THRESHOLD_SEC:
                                signal = ImplicitSignal(
                                    signal_type=ImplicitSignalType.RESPONSE_TIME.value,
                                    signal="positive",
                                    confidence=0.6,
                                    timestamp=next_action.timestamp,
                                    reason=f"Fast response time ({response_time_sec:.1f}s)",
                                    session_id=session_id,
                                    actions_analyzed=2,
                                    metadata={"response_time_sec": response_time_sec},
                                )
                                signals.append(signal)
                            elif response_time_sec > self.VERY_SLOW_RESPONSE_THRESHOLD_SEC:
                                signal = ImplicitSignal(
                                    signal_type=ImplicitSignalType.RESPONSE_TIME.value,
                                    signal="negative",
                                    confidence=0.5,
                                    timestamp=next_action.timestamp,
                                    reason=f"Very slow response time ({response_time_sec:.1f}s)",
                                    session_id=session_id,
                                    actions_analyzed=2,
                                    metadata={"response_time_sec": response_time_sec},
                                )
                                signals.append(signal)
                        except ValueError:
                            pass
                        break
        
        return signals
    
    def _analyze_retry_patterns(
        self,
        actions: List[UserAction],
        session_id: Optional[str] = None,
    ) -> List[ImplicitSignal]:
        """
        Analyze retry patterns.
        
        Retry/repeat → likely unsatisfied with previous result
        
        Args:
            actions: Actions to analyze
            session_id: Session ID
        
        Returns:
            List of implicit signals
        """
        signals = []
        
        # Track repeated actions
        action_counts: Dict[str, int] = {}
        for action in actions:
            if action.action_type == "user_message" and action.content:
                # Simple content hash for comparison
                content_key = action.content[:50].lower().strip()
                action_counts[content_key] = action_counts.get(content_key, 0) + 1
                
                if action_counts[content_key] >= 2:
                    signal = ImplicitSignal(
                        signal_type=ImplicitSignalType.RETRY_ACTION.value,
                        signal="negative",
                        confidence=0.7,
                        timestamp=action.timestamp,
                        reason="Repeated similar action detected",
                        session_id=session_id,
                        actions_analyzed=len(actions),
                        metadata={"repeat_count": action_counts[content_key]},
                    )
                    signals.append(signal)
        
        return signals
    
    def _analyze_continuation(
        self,
        actions: List[UserAction],
        session_id: Optional[str] = None,
    ) -> List[ImplicitSignal]:
        """
        Analyze continuation patterns.
        
        User continues with new task → likely satisfied with previous
        
        Args:
            actions: Actions to analyze
            session_id: Session ID
        
        Returns:
            List of implicit signals
        """
        signals = []
        
        # Look for task transitions without complaints
        for i, action in enumerate(actions):
            if action.action_type == "user_message" and action.content:
                # Check if this is a new task (not a correction/retry)
                content_lower = action.content.lower()
                is_correction = any(
                    word in content_lower 
                    for word in ["incorrect", "wrong", "should", "don't", "not", "retry", "try again"]
                )
                
                if not is_correction and i > 0:
                    # Previous task likely completed satisfactorily
                    prev_action = actions[i - 1]
                    if prev_action.action_type == "ai_response":
                        signal = ImplicitSignal(
                            signal_type=ImplicitSignalType.CONTINUATION.value,
                            signal="positive",
                            confidence=0.5,
                            timestamp=action.timestamp,
                            reason="User continued without complaint",
                            session_id=session_id,
                            actions_analyzed=2,
                        )
                        signals.append(signal)
        
        return signals
    
    def _analyze_abandonment(
        self,
        actions: List[UserAction],
        session_id: Optional[str] = None,
    ) -> List[ImplicitSignal]:
        """
        Analyze abandonment patterns.
        
        Session ended abruptly → may indicate dissatisfaction
        
        Args:
            actions: Actions to analyze
            session_id: Session ID
        
        Returns:
            List of implicit signals
        """
        signals = []
        
        if len(actions) < 2:
            return signals
        
        # Check last action
        last_action = actions[-1]
        
        # If last action was user message with no response, might be abandonment
        if last_action.action_type == "user_message":
            signal = ImplicitSignal(
                signal_type=ImplicitSignalType.ABANDONMENT.value,
                signal="neutral",  # Can't be sure
                confidence=0.3,
                timestamp=last_action.timestamp,
                reason="Session may have been abandoned",
                session_id=session_id,
                actions_analyzed=len(actions),
            )
            signals.append(signal)
        
        return signals
    
    def _analyze_rephrase(
        self,
        actions: List[UserAction],
        session_id: Optional[str] = None,
    ) -> List[ImplicitSignal]:
        """
        Analyze rephrase patterns.
        
        User rephrases question → previous answer was not helpful
        
        Args:
            actions: Actions to analyze
            session_id: Session ID
        
        Returns:
            List of implicit signals
        """
        signals = []
        
        # Look for consecutive user messages with similar intent
        for i in range(1, len(actions)):
            prev_action = actions[i - 1]
            curr_action = actions[i]
            
            if (prev_action.action_type == "user_message" and 
                curr_action.action_type == "user_message"):
                # Check if there's an AI response in between
                has_ai_response = any(
                    a.action_type == "ai_response"
                    for a in actions[i - 1:i + 1]
                )
                
                if not has_ai_response and prev_action.content and curr_action.content:
                    # Two consecutive user messages without AI response
                    # Might indicate rephrasing
                    similarity = self._calculate_similarity(
                        prev_action.content, curr_action.content
                    )
                    
                    if similarity > 0.5:  # Similar content
                        signal = ImplicitSignal(
                            signal_type=ImplicitSignalType.REPHRASE.value,
                            signal="negative",
                            confidence=0.6,
                            timestamp=curr_action.timestamp,
                            reason="User rephrased question",
                            session_id=session_id,
                            actions_analyzed=2,
                            metadata={"similarity": similarity},
                        )
                        signals.append(signal)
        
        return signals
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity based on word overlap.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def get_session_summary(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Get a summary of inferred signals for a session.
        
        Args:
            session_id: Session ID
        
        Returns:
            Dictionary with session summary
        """
        signals = self.infer_signals(session_id=session_id)
        
        if not signals:
            return {
                "session_id": session_id,
                "total_signals": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "average_confidence": 0.0,
                "overall_sentiment": "neutral",
            }
        
        positive_count = sum(1 for s in signals if s.signal == "positive")
        negative_count = sum(1 for s in signals if s.signal == "negative")
        neutral_count = sum(1 for s in signals if s.signal == "neutral")
        
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Determine overall sentiment
        if positive_count > negative_count:
            overall = "positive"
        elif negative_count > positive_count:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "session_id": session_id,
            "total_signals": len(signals),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "average_confidence": avg_confidence,
            "overall_sentiment": overall,
            "signals": [s.to_dict() for s in signals],
        }
    
    def clear_actions(self) -> None:
        """Clear all tracked actions."""
        self._actions.clear()
        self._session_actions.clear()
    
    def get_actions(self, session_id: Optional[str] = None) -> List[UserAction]:
        """
        Get tracked actions.
        
        Args:
            session_id: Optional session ID to filter
        
        Returns:
            List of user actions
        """
        if session_id:
            return self._session_actions.get(session_id, [])
        return self._actions.copy()
