"""
Feedback Collector - Collect and normalize user feedback

This module provides a unified interface for collecting user feedback
from multiple sources and normalizing them into a standard format.
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json


class FeedbackType(Enum):
    """Types of user feedback."""
    THUMBS_UP = "thumbs_up"           # 👍 Quick approval
    THUMBS_DOWN = "thumbs_down"       # 👎 Quick disapproval
    RATING = "rating"                  # 1-5 star rating
    TEXT = "text"                      # Free-form text feedback
    CORRECTION = "correction"          # User correction
    REJECTION = "rejection"            # Explicit rejection
    ACCEPTANCE = "acceptance"          # Explicit acceptance
    IMPLICIT = "implicit"              # Inferred from behavior


class FeedbackSource(Enum):
    """Sources of feedback."""
    WEBCHAT = "webchat"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    SIGNAL = "signal"
    SLACK = "slack"
    CLI = "cli"
    API = "api"


@dataclass
class Feedback:
    """
    Normalized feedback structure.
    
    All feedback types are converted to this standard format
    for consistent processing.
    """
    # Core fields
    feedback_type: str                    # FeedbackType value
    source: str                           # FeedbackSource value
    timestamp: str                        # ISO 8601 timestamp
    
    # Normalized signal
    signal: Literal["positive", "negative", "neutral"]
    confidence: float                     # 0.0 to 1.0
    
    # Content
    content: Optional[str] = None         # Raw feedback content
    rating: Optional[int] = None          # 1-5 for rating type
    
    # Context
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    action_context: Optional[str] = None  # What action triggered this feedback
    
    # OPD hint (for corrections)
    hint_type: Optional[str] = None       # 'should', 'should_not', 'sequence', 'conditional'
    hint_content: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Feedback":
        """Create Feedback from dictionary."""
        return cls(**data)


class FeedbackCollector:
    """
    Unified feedback collector with normalization.
    
    Collects feedback from multiple sources and normalizes them
    into a standard Feedback format.
    
    Example:
        >>> collector = FeedbackCollector()
        >>> 
        >>> # Collect thumbs up
        >>> fb = collector.collect_thumbs_up(source="discord", session_id="123")
        >>> print(fb.signal)
        'positive'
        >>> 
        >>> # Collect text feedback
        >>> fb = collector.collect_text("谢谢，很好！", source="webchat")
        >>> print(fb.signal)
        'positive'
        >>> 
        >>> # Collect rating
        >>> fb = collector.collect_rating(5, source="api")
        >>> print(fb.signal)
        'positive'
    """
    
    # Rating thresholds
    RATING_POSITIVE_THRESHOLD = 4  # >= 4 is positive
    RATING_NEGATIVE_THRESHOLD = 2  # <= 2 is negative
    
    # Positive text patterns
    POSITIVE_PATTERNS = [
        "谢谢", "感谢", "多谢", "太感谢了",
        "很好", "太好了", "不错", "好的", "正确", "对了", "完美", "满意", "喜欢",
        "继续", "再来",
        "👍", "👌", "✅", "😊", "😄",
    ]
    
    # Negative text patterns
    NEGATIVE_PATTERNS = [
        "不对", "错了", "错误", "不正确", "有问题",
        "应该", "应该是", "要", "需要",
        "不满意", "不喜欢", "反对", "失望", "不好",
        "不要", "别", "不是",
        "👎", "❌", "😠",
    ]
    
    def __init__(self, default_source: str = "api"):
        """
        Initialize FeedbackCollector.
        
        Args:
            default_source: Default source for feedback if not specified
        """
        self.default_source = default_source
        self._collected: List[Feedback] = []
    
    def collect_thumbs_up(
        self,
        source: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        action_context: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Feedback:
        """
        Collect a thumbs up feedback.
        
        Args:
            source: Feedback source
            session_id: Session ID
            message_id: Message ID
            action_context: Action that triggered this feedback
            metadata: Additional metadata
        
        Returns:
            Normalized Feedback
        """
        return Feedback(
            feedback_type=FeedbackType.THUMBS_UP.value,
            source=source or self.default_source,
            timestamp=datetime.now().isoformat(),
            signal="positive",
            confidence=0.95,
            session_id=session_id,
            message_id=message_id,
            action_context=action_context,
            metadata=metadata or {},
        )
    
    def collect_thumbs_down(
        self,
        source: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        action_context: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Feedback:
        """
        Collect a thumbs down feedback.
        
        Args:
            source: Feedback source
            session_id: Session ID
            message_id: Message ID
            action_context: Action that triggered this feedback
            metadata: Additional metadata
        
        Returns:
            Normalized Feedback
        """
        return Feedback(
            feedback_type=FeedbackType.THUMBS_DOWN.value,
            source=source or self.default_source,
            timestamp=datetime.now().isoformat(),
            signal="negative",
            confidence=0.95,
            session_id=session_id,
            message_id=message_id,
            action_context=action_context,
            metadata=metadata or {},
        )
    
    def collect_rating(
        self,
        rating: int,
        source: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        action_context: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Feedback:
        """
        Collect a rating feedback (1-5 stars).
        
        Args:
            rating: Rating value (1-5)
            source: Feedback source
            session_id: Session ID
            message_id: Message ID
            action_context: Action that triggered this feedback
            metadata: Additional metadata
        
        Returns:
            Normalized Feedback
        """
        if not 1 <= rating <= 5:
            raise ValueError(f"Rating must be 1-5, got {rating}")
        
        # Normalize to signal
        if rating >= self.RATING_POSITIVE_THRESHOLD:
            signal = "positive"
            confidence = 0.7 + (rating - 4) * 0.15  # 0.7-0.85
        elif rating <= self.RATING_NEGATIVE_THRESHOLD:
            signal = "negative"
            confidence = 0.7 + (2 - rating) * 0.15  # 0.7-0.85
        else:
            signal = "neutral"
            confidence = 0.5
        
        return Feedback(
            feedback_type=FeedbackType.RATING.value,
            source=source or self.default_source,
            timestamp=datetime.now().isoformat(),
            signal=signal,
            confidence=confidence,
            rating=rating,
            session_id=session_id,
            message_id=message_id,
            action_context=action_context,
            metadata=metadata or {},
        )
    
    def collect_text(
        self,
        text: str,
        source: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        action_context: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Feedback:
        """
        Collect text feedback and analyze sentiment.
        
        Args:
            text: Feedback text
            source: Feedback source
            session_id: Session ID
            message_id: Message ID
            action_context: Action that triggered this feedback
            metadata: Additional metadata
        
        Returns:
            Normalized Feedback
        """
        signal, confidence = self._analyze_text(text)
        feedback_type = FeedbackType.TEXT.value
        
        # Detect correction patterns
        hint_type, hint_content = self._extract_correction_hint(text)
        if hint_type:
            feedback_type = FeedbackType.CORRECTION.value
        
        return Feedback(
            feedback_type=feedback_type,
            source=source or self.default_source,
            timestamp=datetime.now().isoformat(),
            signal=signal,
            confidence=confidence,
            content=text,
            session_id=session_id,
            message_id=message_id,
            action_context=action_context,
            hint_type=hint_type,
            hint_content=hint_content,
            metadata=metadata or {},
        )
    
    def collect_correction(
        self,
        correction: str,
        source: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        action_context: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Feedback:
        """
        Collect an explicit correction feedback.
        
        Args:
            correction: Correction text
            source: Feedback source
            session_id: Session ID
            message_id: Message ID
            action_context: Action that triggered this feedback
            metadata: Additional metadata
        
        Returns:
            Normalized Feedback
        """
        hint_type, hint_content = self._extract_correction_hint(correction)
        
        return Feedback(
            feedback_type=FeedbackType.CORRECTION.value,
            source=source or self.default_source,
            timestamp=datetime.now().isoformat(),
            signal="negative",  # Corrections imply something was wrong
            confidence=0.9,
            content=correction,
            session_id=session_id,
            message_id=message_id,
            action_context=action_context,
            hint_type=hint_type,
            hint_content=hint_content,
            metadata=metadata or {},
        )
    
    def collect_rejection(
        self,
        reason: Optional[str] = None,
        source: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        action_context: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Feedback:
        """
        Collect an explicit rejection feedback.
        
        Args:
            reason: Optional reason for rejection
            source: Feedback source
            session_id: Session ID
            message_id: Message ID
            action_context: Action that triggered this feedback
            metadata: Additional metadata
        
        Returns:
            Normalized Feedback
        """
        return Feedback(
            feedback_type=FeedbackType.REJECTION.value,
            source=source or self.default_source,
            timestamp=datetime.now().isoformat(),
            signal="negative",
            confidence=0.95,
            content=reason,
            session_id=session_id,
            message_id=message_id,
            action_context=action_context,
            metadata=metadata or {},
        )
    
    def collect_acceptance(
        self,
        comment: Optional[str] = None,
        source: Optional[str] = None,
        session_id: Optional[str] = None,
        message_id: Optional[str] = None,
        action_context: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Feedback:
        """
        Collect an explicit acceptance feedback.
        
        Args:
            comment: Optional comment
            source: Feedback source
            session_id: Session ID
            message_id: Message ID
            action_context: Action that triggered this feedback
            metadata: Additional metadata
        
        Returns:
            Normalized Feedback
        """
        return Feedback(
            feedback_type=FeedbackType.ACCEPTANCE.value,
            source=source or self.default_source,
            timestamp=datetime.now().isoformat(),
            signal="positive",
            confidence=0.95,
            content=comment,
            session_id=session_id,
            message_id=message_id,
            action_context=action_context,
            metadata=metadata or {},
        )
    
    def _analyze_text(self, text: str) -> tuple:
        """
        Analyze text feedback for sentiment.
        
        Args:
            text: Feedback text
        
        Returns:
            (signal, confidence) tuple
        """
        if not text or not text.strip():
            return ("neutral", 0.0)
        
        text_lower = text.lower()
        
        # Check negative patterns first (corrections are more important)
        for pattern in self.NEGATIVE_PATTERNS:
            if pattern in text_lower:
                confidence = 0.95 if pattern in ["应该", "错了"] else 0.9
                return ("negative", confidence)
        
        # Check positive patterns
        for pattern in self.POSITIVE_PATTERNS:
            if pattern in text_lower:
                confidence = 0.95 if pattern in ["谢谢", "很好"] else 0.9
                return ("positive", confidence)
        
        # No pattern matched
        return ("neutral", 0.5)
    
    def _extract_correction_hint(self, text: str) -> tuple:
        """
        Extract OPD hint from correction text.
        
        Args:
            text: Correction text
        
        Returns:
            (hint_type, hint_content) tuple or (None, None)
        """
        if not text or not text.strip():
            return (None, None)
        
        text = text.strip()
        
        # Pattern 1: "应该 X" → "操作前 X"
        if text.startswith("应该"):
            action = text[2:].strip()
            if action:
                return ("should", f"操作前{action}")
        
        # Pattern 2: "不要 X" → "避免 X"
        if text.startswith("不要"):
            action = text[2:].strip()
            if action:
                return ("should_not", f"避免{action}")
        
        # Pattern 3: "先 X 再 Y" → "顺序：先 X 再 Y"
        if "先" in text and "再" in text:
            first_idx = text.find("先")
            again_idx = text.find("再", first_idx + 1)
            if first_idx >= 0 and again_idx > first_idx:
                step1 = text[first_idx+1:again_idx].strip()
                step2 = text[again_idx+1:].strip()
                if step1 and step2:
                    return ("sequence", f"顺序：先{step1}再{step2}")
        
        # Pattern 4: "如果 X，则 Y" → "条件：X → Y"
        if "如果" in text and ("则" in text or "就" in text):
            if_pos = text.find("如果")
            then_pos = -1
            then_word = ""
            if "则" in text:
                then_pos = text.find("则", if_pos + 2)
                then_word = "则"
            elif "就" in text:
                then_pos = text.find("就", if_pos + 2)
                then_word = "就"
            
            if if_pos >= 0 and then_pos > if_pos:
                condition = text[if_pos+2:then_pos].strip()
                action = text[then_pos+1:].strip()
                if condition and action:
                    return ("conditional", f"条件：{condition} → {action}")
        
        return (None, None)
    
    def add_feedback(self, feedback: Feedback) -> None:
        """Add feedback to collected list."""
        self._collected.append(feedback)
    
    def get_collected(self) -> List[Feedback]:
        """Get all collected feedback."""
        return self._collected.copy()
    
    def clear_collected(self) -> None:
        """Clear collected feedback."""
        self._collected.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about collected feedback.
        
        Returns:
            Dictionary with feedback statistics
        """
        if not self._collected:
            return {
                "total": 0,
                "by_type": {},
                "by_signal": {},
                "by_source": {},
            }
        
        by_type: Dict[str, int] = {}
        by_signal: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        
        for fb in self._collected:
            by_type[fb.feedback_type] = by_type.get(fb.feedback_type, 0) + 1
            by_signal[fb.signal] = by_signal.get(fb.signal, 0) + 1
            by_source[fb.source] = by_source.get(fb.source, 0) + 1
        
        return {
            "total": len(self._collected),
            "by_type": by_type,
            "by_signal": by_signal,
            "by_source": by_source,
            "positive_rate": by_signal.get("positive", 0) / len(self._collected),
            "negative_rate": by_signal.get("negative", 0) / len(self._collected),
        }
