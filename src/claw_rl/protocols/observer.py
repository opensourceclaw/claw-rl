"""
Observer Protocol - Abstract interface for observation collection

This protocol defines the interface for collecting observations
from the learning environment.
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Observation:
    """
    Represents a single observation.
    
    Attributes:
        timestamp: When the observation was made
        metrics: Performance metrics
        feedback: Feedback signals
        context: Contextual information
        metadata: Additional metadata
    """
    timestamp: str
    metrics: Dict[str, Any]
    feedback: Dict[str, Any]
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "feedback": self.feedback,
            "context": self.context,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Observation':
        """Create from dictionary."""
        return cls(
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metrics=data.get("metrics", {}),
            feedback=data.get("feedback", {}),
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
        )


class ObserverProtocol(Protocol):
    """
    Protocol for collecting observations from the learning environment.
    
    An Observer is responsible for:
    - Collecting performance metrics
    - Gathering feedback signals
    - Capturing contextual information
    - Providing observations for decision making
    
    This is a Protocol (interface) - frameworks must provide their own
    implementation through adapters.
    
    Example:
        >>> class MyObserver(ObserverProtocol):
        ...     def observe(self) -> Observation:
        ...         return Observation(
        ...             timestamp=datetime.now().isoformat(),
        ...             metrics={"accuracy": 0.95},
        ...             feedback={"user_rating": 5},
        ...             context={"task": "classification"},
        ...             metadata={"source": "my_app"},
        ...         )
    """
    
    def observe(self) -> Observation:
        """
        Collect and return an observation.
        
        Returns:
            Observation containing metrics, feedback, and context.
            
        This method should:
        - Collect current performance metrics
        - Gather any available feedback signals
        - Capture relevant context
        - Return a structured observation
        """
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        Returns:
            Dictionary of metric names to values.
            
        Example metrics:
        - accuracy: Model accuracy
        - latency: Response latency
        - throughput: Requests per second
        - error_rate: Error percentage
        """
        ...
    
    def get_feedback(self) -> Dict[str, Any]:
        """
        Get available feedback signals.
        
        Returns:
            Dictionary of feedback types to values.
            
        Example feedback:
        - user_rating: User satisfaction rating
        - explicit_feedback: Thumbs up/down
        - implicit_feedback: Derived from behavior
        - error_count: Number of errors
        """
        ...
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current context information.
        
        Returns:
            Dictionary of context attributes.
            
        Example context:
        - task_type: Type of task being performed
        - environment: Production/staging/dev
        - user_segment: User classification
        - time_of_day: Temporal context
        """
        ...
    
    def reset(self) -> None:
        """
        Reset observer state.
        
        This method should clear any accumulated state
        and prepare for fresh observations.
        """
        ...
