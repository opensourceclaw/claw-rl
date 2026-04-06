"""
Signal Adapter Protocol - Abstract interface for adapting signals

This protocol defines the interface for converting framework-specific
signals to a common format.
"""

from typing import Protocol, Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SignalType(Enum):
    """Types of signals."""
    REWARD = "reward"
    HINT = "hint"
    FEEDBACK = "feedback"
    ERROR = "error"
    METRIC = "metric"


@dataclass
class AdaptedSignal:
    """
    A signal adapted to common format.
    
    Attributes:
        signal_id: Unique identifier
        signal_type: Type of signal
        source: Signal source (framework name)
        payload: Signal payload in common format
        timestamp: When signal was received
        metadata: Additional metadata
    """
    signal_id: str
    signal_type: SignalType
    source: str
    payload: Dict[str, Any]
    timestamp: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value,
            "source": self.source,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdaptedSignal':
        """Create from dictionary."""
        return cls(
            signal_id=data["signal_id"],
            signal_type=SignalType(data["signal_type"]),
            source=data["source"],
            payload=data["payload"],
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )
    
    def to_reward(self) -> Optional[float]:
        """
        Convert to reward value if applicable.
        
        Returns:
            Reward value, or None if not a reward signal
        """
        if self.signal_type == SignalType.REWARD:
            return self.payload.get("value", 0.0)
        return None
    
    def to_hint(self) -> Optional[str]:
        """
        Convert to hint if applicable.
        
        Returns:
            Hint text, or None if not a hint signal
        """
        if self.signal_type == SignalType.HINT:
            return self.payload.get("text", "")
        return None


class SignalAdapterProtocol(Protocol):
    """
    Protocol for adapting framework-specific signals to common format.
    
    A SignalAdapter is responsible for:
    - Converting framework signals to common format
    - Handling multiple signal types
    - Providing signal type detection
    - Validating signals
    
    This is a Protocol (interface) - frameworks must provide their own
    implementation through adapters.
    
    Example:
        >>> class NeoClawSignalAdapter(SignalAdapterProtocol):
        ...     def adapt(self, raw_signal: Any) -> AdaptedSignal:
        ...         # Convert NeoClaw signal to common format
        ...         return AdaptedSignal(
        ...             signal_id=raw_signal.id,
        ...             signal_type=self._detect_type(raw_signal),
        ...             source="neoclaw",
        ...             payload={
        ...                 "value": raw_signal.value,
        ...                 "context": raw_signal.context,
        ...             },
        ...         )
    """
    
    def adapt(self, raw_signal: Any) -> AdaptedSignal:
        """
        Adapt a framework-specific signal to common format.
        
        Args:
            raw_signal: Framework-specific signal
            
        Returns:
            AdaptedSignal in common format
            
        This method should:
        - Extract signal type
        - Convert payload to common format
        - Generate unique ID if needed
        - Add source identification
        """
        ...
    
    def adapt_batch(self, raw_signals: List[Any]) -> List[AdaptedSignal]:
        """
        Adapt multiple signals.
        
        Args:
            raw_signals: List of framework-specific signals
            
        Returns:
            List of adapted signals
        """
        ...
    
    def detect_type(self, raw_signal: Any) -> SignalType:
        """
        Detect the type of a raw signal.
        
        Args:
            raw_signal: Framework-specific signal
            
        Returns:
            Detected signal type
        """
        ...
    
    def validate(self, raw_signal: Any) -> bool:
        """
        Validate a raw signal.
        
        Args:
            raw_signal: Framework-specific signal
            
        Returns:
            True if signal is valid
        """
        ...
    
    def get_source_name(self) -> str:
        """
        Get the name of the source framework.
        
        Returns:
            Framework name (e.g., "neoclaw", "openclaw")
        """
        ...
