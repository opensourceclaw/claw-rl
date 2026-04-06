"""
Decision Maker Protocol - Abstract interface for learning decisions

This protocol defines the interface for making decisions based on
observations in the learning loop.
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DecisionType(Enum):
    """Types of decisions."""
    PARAMETER_ADJUST = "parameter_adjust"
    STRATEGY_CHANGE = "strategy_change"
    RULE_UPDATE = "rule_update"
    CONFIG_UPDATE = "config_update"
    NO_ACTION = "no_action"


@dataclass
class Decision:
    """
    Represents a learning decision.
    
    Attributes:
        decision_id: Unique identifier
        decision_type: Type of decision
        action: Action to take
        parameters: Parameters for the action
        confidence: Decision confidence (0.0 - 1.0)
        reasoning: Explanation for the decision
        timestamp: When the decision was made
        metadata: Additional metadata
    """
    decision_id: str
    decision_type: DecisionType
    action: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str = ""
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
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "action": self.action,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Decision':
        """Create from dictionary."""
        return cls(
            decision_id=data["decision_id"],
            decision_type=DecisionType(data["decision_type"]),
            action=data["action"],
            parameters=data["parameters"],
            confidence=data["confidence"],
            reasoning=data.get("reasoning", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )


class DecisionMakerProtocol(Protocol):
    """
    Protocol for making learning decisions based on observations.
    
    A DecisionMaker is responsible for:
    - Analyzing observations
    - Deciding what actions to take
    - Providing confidence scores
    - Explaining reasoning
    
    This is a Protocol (interface) - frameworks must provide their own
    implementation through adapters.
    
    Example:
        >>> class MyDecisionMaker(DecisionMakerProtocol):
        ...     def decide(self, observations: Dict[str, Any]) -> Decision:
        ...         if observations["metrics"]["accuracy"] < 0.8:
        ...             return Decision(
        ...                 decision_id="dec_001",
        ...                 decision_type=DecisionType.PARAMETER_ADJUST,
        ...                 action="increase_learning_rate",
        ...                 parameters={"learning_rate": 0.01},
        ...                 confidence=0.9,
        ...                 reasoning="Low accuracy, need to adapt faster",
        ...             )
        ...         return Decision(
        ...             decision_id="dec_002",
        ...             decision_type=DecisionType.NO_ACTION,
        ...             action="none",
        ...             parameters={},
        ...             confidence=1.0,
        ...             reasoning="Performance is acceptable",
        ...         )
    """
    
    def decide(self, observations: Dict[str, Any]) -> Decision:
        """
        Make a decision based on observations.
        
        Args:
            observations: Dictionary of observations from Observer
            
        Returns:
            Decision containing action to take
            
        This method should:
        - Analyze the observations
        - Determine if action is needed
        - Select appropriate action
        - Provide confidence score
        - Explain reasoning
        """
        ...
    
    def get_confidence(self, observations: Dict[str, Any]) -> float:
        """
        Get confidence score for potential decision.
        
        Args:
            observations: Dictionary of observations
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        ...
    
    def explain(self, decision: Decision) -> str:
        """
        Explain the reasoning behind a decision.
        
        Args:
            decision: Decision to explain
            
        Returns:
            Human-readable explanation
        """
        ...
    
    def reset(self) -> None:
        """
        Reset decision maker state.
        
        This method should clear any accumulated state
        and prepare for fresh decisions.
        """
        ...
