"""
Signal Fusion - Combine explicit and implicit feedback signals

This module fuses explicit feedback (thumbs up/down, ratings, text)
with implicit signals (response time, retry patterns, etc.) to produce
a unified confidence-weighted feedback score.
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math

from .collector import Feedback
from .implicit import ImplicitSignal


class SignalSource(Enum):
    """Source of feedback signal."""
    EXPLICIT = "explicit"    # Direct user feedback
    IMPLICIT = "implicit"    # Inferred from behavior


@dataclass
class FusedSignal:
    """Fused feedback signal combining explicit and implicit."""
    signal: Literal["positive", "negative", "neutral"]
    confidence: float                     # 0.0 to 1.0
    timestamp: str
    session_id: Optional[str] = None
    
    # Source breakdown
    explicit_count: int = 0
    implicit_count: int = 0
    
    # Weighted scores
    explicit_score: float = 0.0           # -1.0 to 1.0
    implicit_score: float = 0.0           # -1.0 to 1.0
    
    # Details
    sources: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "signal": self.signal,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "explicit_count": self.explicit_count,
            "implicit_count": self.implicit_count,
            "explicit_score": self.explicit_score,
            "implicit_score": self.implicit_score,
            "sources": self.sources,
            "reasons": self.reasons,
            "metadata": self.metadata,
        }


class SignalFusion:
    """
    Fuse explicit and implicit feedback signals.
    
    Combines multiple feedback sources with confidence weighting:
    - Explicit feedback has higher weight (0.7-1.0)
    - Implicit feedback has lower weight (0.3-0.6)
    - More recent feedback has higher weight
    
    Example:
        >>> fusion = SignalFusion()
        >>> 
        >>> # Add explicit feedback
        >>> explicit = Feedback(...)
        >>> fusion.add_explicit(explicit)
        >>> 
        >>> # Add implicit signal
        >>> implicit = ImplicitSignal(...)
        >>> fusion.add_implicit(implicit)
        >>> 
        >>> # Get fused result
        >>> fused = fusion.fuse()
        >>> print(fused.signal)
        'positive'
    """
    
    # Weight configuration
    EXPLICIT_BASE_WEIGHT = 0.8           # Base weight for explicit feedback
    IMPLICIT_BASE_WEIGHT = 0.4           # Base weight for implicit signals
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    LOW_CONFIDENCE_THRESHOLD = 0.3
    
    # Time decay
    TIME_DECAY_FACTOR = 0.95             # Decay per hour
    TIME_DECAY_MIN_WEIGHT = 0.3          # Minimum weight after decay
    
    def __init__(self):
        """Initialize SignalFusion."""
        self._explicit_feedbacks: List[Feedback] = []
        self._implicit_signals: List[ImplicitSignal] = []
    
    def add_explicit(self, feedback: Feedback) -> None:
        """
        Add explicit feedback.
        
        Args:
            feedback: Explicit feedback to add
        """
        self._explicit_feedbacks.append(feedback)
    
    def add_implicit(self, signal: ImplicitSignal) -> None:
        """
        Add implicit signal.
        
        Args:
            signal: Implicit signal to add
        """
        self._implicit_signals.append(signal)
    
    def add_explicit_batch(self, feedbacks: List[Feedback]) -> None:
        """Add multiple explicit feedbacks."""
        for fb in feedbacks:
            self.add_explicit(fb)
    
    def add_implicit_batch(self, signals: List[ImplicitSignal]) -> None:
        """Add multiple implicit signals."""
        for signal in signals:
            self.add_implicit(signal)
    
    def fuse(
        self,
        session_id: Optional[str] = None,
        reference_time: Optional[str] = None,
    ) -> FusedSignal:
        """
        Fuse all signals into a single result.
        
        Args:
            session_id: Optional session ID to include
            reference_time: Reference time for time decay (defaults to now)
        
        Returns:
            FusedSignal with combined confidence
        """
        now = reference_time or datetime.now().isoformat()
        
        # Calculate explicit score
        explicit_score, explicit_confidence, explicit_reasons = self._calculate_explicit_score(
            reference_time=now
        )
        
        # Calculate implicit score
        implicit_score, implicit_confidence, implicit_reasons = self._calculate_implicit_score(
            reference_time=now
        )
        
        # Weight the scores
        explicit_weight = self.EXPLICIT_BASE_WEIGHT * explicit_confidence
        implicit_weight = self.IMPLICIT_BASE_WEIGHT * implicit_confidence
        
        # Normalize weights
        total_weight = explicit_weight + implicit_weight
        if total_weight <= 0:
            # No valid feedback, return neutral result
            return FusedSignal(
                signal="neutral",
                confidence=0.0,
                timestamp=now,
                session_id=session_id,
                explicit_count=len(self._explicit_feedbacks),
                implicit_count=len(self._implicit_signals),
                explicit_score=0.0,
                implicit_score=0.0,
                sources=[],
                reasons=["No valid feedback with confidence > 0"],
            )
        
        explicit_weight /= total_weight
        implicit_weight /= total_weight
        
        # Calculate fused score
        fused_score = explicit_score * explicit_weight + implicit_score * implicit_weight
        
        # Calculate fused confidence
        # Higher when both explicit and implicit agree
        confidence_boost = 0.0
        if explicit_score != 0 and implicit_score != 0:
            # Both have signal
            if (explicit_score > 0 and implicit_score > 0) or (explicit_score < 0 and implicit_score < 0):
                # Agreement - boost confidence
                confidence_boost = 0.15
            else:
                # Disagreement - reduce confidence
                confidence_boost = -0.1
        
        base_confidence = (explicit_confidence * explicit_weight + implicit_confidence * implicit_weight)
        fused_confidence = min(1.0, max(0.0, base_confidence + confidence_boost))
        
        # Determine signal
        if fused_score > 0.2:
            signal = "positive"
        elif fused_score < -0.2:
            signal = "negative"
        else:
            signal = "neutral"
        
        # Combine sources and reasons
        sources = []
        if self._explicit_feedbacks:
            sources.append("explicit")
        if self._implicit_signals:
            sources.append("implicit")
        
        reasons = explicit_reasons + implicit_reasons
        
        return FusedSignal(
            signal=signal,
            confidence=fused_confidence,
            timestamp=now,
            session_id=session_id,
            explicit_count=len(self._explicit_feedbacks),
            implicit_count=len(self._implicit_signals),
            explicit_score=explicit_score,
            implicit_score=implicit_score,
            sources=sources,
            reasons=reasons,
        )
    
    def _calculate_explicit_score(
        self,
        reference_time: Optional[str] = None,
    ) -> tuple:
        """
        Calculate weighted score from explicit feedback.
        
        Returns:
            (score, confidence, reasons) tuple
        """
        if not self._explicit_feedbacks:
            return (0.0, 0.0, [])
        
        total_weight = 0.0
        weighted_score = 0.0
        reasons = []
        
        ref_time = datetime.fromisoformat(reference_time) if reference_time else datetime.now()
        
        for fb in self._explicit_feedbacks:
            # Validate confidence range
            if not 0 <= fb.confidence <= 1:
                continue  # Skip invalid feedback
            
            # Validate signal value
            if fb.signal not in ("positive", "negative", "neutral"):
                continue  # Skip invalid feedback
            
            # Calculate base score from signal
            if fb.signal == "positive":
                base_score = 1.0
            elif fb.signal == "negative":
                base_score = -1.0
            else:
                base_score = 0.0
            
            # Apply confidence
            weight = fb.confidence
            
            # Apply time decay
            try:
                fb_time = datetime.fromisoformat(fb.timestamp)
                hours_ago = max(0, (ref_time - fb_time).total_seconds() / 3600)
                time_weight = max(
                    self.TIME_DECAY_MIN_WEIGHT,
                    min(1.0, self.TIME_DECAY_FACTOR ** hours_ago)
                )
                weight *= time_weight
            except (ValueError, TypeError):
                pass
            
            # Higher weight for explicit feedback types
            type_multiplier = {
                "thumbs_up": 1.0,
                "thumbs_down": 1.0,
                "rejection": 0.95,
                "acceptance": 0.95,
                "correction": 0.9,
                "rating": 0.85,
                "text": 0.75,
            }.get(fb.feedback_type, 0.8)
            weight *= type_multiplier
            
            weighted_score += base_score * weight
            total_weight += weight
            
            # Collect reason
            if fb.content:
                reasons.append(f"Explicit ({fb.feedback_type}): {fb.content[:50]}")
            else:
                reasons.append(f"Explicit ({fb.feedback_type}): {fb.signal}")
        
        if total_weight > 0:
            final_score = weighted_score / total_weight
            avg_confidence = total_weight / len(self._explicit_feedbacks)
        else:
            final_score = 0.0
            avg_confidence = 0.0
        
        return (final_score, min(avg_confidence, 1.0), reasons)
    
    def _calculate_implicit_score(
        self,
        reference_time: Optional[str] = None,
    ) -> tuple:
        """
        Calculate weighted score from implicit signals.
        
        Returns:
            (score, confidence, reasons) tuple
        """
        if not self._implicit_signals:
            return (0.0, 0.0, [])
        
        total_weight = 0.0
        weighted_score = 0.0
        reasons = []
        
        ref_time = datetime.fromisoformat(reference_time) if reference_time else datetime.now()
        
        for signal in self._implicit_signals:
            # Validate confidence range
            if not 0 <= signal.confidence <= 1:
                continue  # Skip invalid signal
            
            # Validate signal value
            if signal.signal not in ("positive", "negative", "neutral"):
                continue  # Skip invalid signal
            
            # Calculate base score from signal
            if signal.signal == "positive":
                base_score = 1.0
            elif signal.signal == "negative":
                base_score = -1.0
            else:
                base_score = 0.0
            
            # Apply confidence
            weight = signal.confidence
            
            # Apply time decay
            try:
                signal_time = datetime.fromisoformat(signal.timestamp)
                hours_ago = max(0, (ref_time - signal_time).total_seconds() / 3600)
                time_weight = max(
                    self.TIME_DECAY_MIN_WEIGHT,
                    min(1.0, self.TIME_DECAY_FACTOR ** hours_ago)
                )
                weight *= time_weight
            except (ValueError, TypeError):
                pass
            
            # Different signal types have different reliability
            type_multiplier = {
                "continuation": 0.6,      # Not always reliable
                "response_time": 0.5,     # Context-dependent
                "retry_action": 0.8,      # Strong signal
                "rephrase": 0.7,          # Moderate signal
                "abandonment": 0.4,       # Uncertain
            }.get(signal.signal_type, 0.5)
            weight *= type_multiplier
            
            weighted_score += base_score * weight
            total_weight += weight
            
            # Collect reason
            reasons.append(f"Implicit ({signal.signal_type}): {signal.reason}")
        
        if total_weight > 0:
            final_score = weighted_score / total_weight
            avg_confidence = total_weight / len(self._implicit_signals)
        else:
            final_score = 0.0
            avg_confidence = 0.0
        
        return (final_score, min(avg_confidence, 1.0), reasons)
    
    def get_signal_breakdown(self) -> Dict[str, Any]:
        """
        Get breakdown of signals by type.
        
        Returns:
            Dictionary with signal breakdown
        """
        explicit_by_type: Dict[str, int] = {}
        implicit_by_type: Dict[str, int] = {}
        explicit_by_signal: Dict[str, int] = {}
        implicit_by_signal: Dict[str, int] = {}
        
        for fb in self._explicit_feedbacks:
            explicit_by_type[fb.feedback_type] = explicit_by_type.get(fb.feedback_type, 0) + 1
            explicit_by_signal[fb.signal] = explicit_by_signal.get(fb.signal, 0) + 1
        
        for signal in self._implicit_signals:
            implicit_by_type[signal.signal_type] = implicit_by_type.get(signal.signal_type, 0) + 1
            implicit_by_signal[signal.signal] = implicit_by_signal.get(signal.signal, 0) + 1
        
        return {
            "explicit_count": len(self._explicit_feedbacks),
            "implicit_count": len(self._implicit_signals),
            "total_count": len(self._explicit_feedbacks) + len(self._implicit_signals),
            "explicit_by_type": explicit_by_type,
            "implicit_by_type": implicit_by_type,
            "explicit_by_signal": explicit_by_signal,
            "implicit_by_signal": implicit_by_signal,
        }
    
    def clear(self) -> None:
        """Clear all signals."""
        self._explicit_feedbacks.clear()
        self._implicit_signals.clear()


def fuse_feedbacks(
    explicit_feedbacks: Optional[List[Feedback]] = None,
    implicit_signals: Optional[List[ImplicitSignal]] = None,
    session_id: Optional[str] = None,
) -> FusedSignal:
    """
    Convenience function to fuse feedbacks in one call.
    
    Args:
        explicit_feedbacks: List of explicit feedbacks
        implicit_signals: List of implicit signals
        session_id: Session ID
    
    Returns:
        FusedSignal
    """
    fusion = SignalFusion()
    
    if explicit_feedbacks:
        fusion.add_explicit_batch(explicit_feedbacks)
    
    if implicit_signals:
        fusion.add_implicit_batch(implicit_signals)
    
    return fusion.fuse(session_id=session_id)
