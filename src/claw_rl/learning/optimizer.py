"""
Strategy Optimizer - Feedback-driven strategy optimization

This module optimizes learning strategies based on collected feedback.
Uses feedback signals to adjust strategy parameters and improve performance.
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os

from ..feedback.collector import Feedback
from ..feedback.implicit import ImplicitSignal
from ..feedback.signal_fusion import FusedSignal, SignalFusion


class OptimizationStrategy(Enum):
    """Strategy optimization approaches."""
    GRADIENT = "gradient"           # Gradual adjustment based on feedback
    THRESHOLD = "threshold"         # Adjust when crossing thresholds
    BANDIT = "bandit"               # Multi-armed bandit exploration
    BAYESIAN = "bayesian"           # Bayesian optimization


class AdjustmentDirection(Enum):
    """Direction of parameter adjustment."""
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


@dataclass
class StrategyParameter:
    """A tunable strategy parameter."""
    name: str
    current_value: float
    min_value: float
    max_value: float
    adjustment_rate: float = 0.1    # How much to adjust per step
    
    # Statistics
    total_adjustments: int = 0
    last_adjustment: Optional[str] = None
    adjustment_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Maximum history size to prevent memory issues
    MAX_HISTORY_SIZE: int = field(default=100, repr=False)
    
    def adjust(self, direction: AdjustmentDirection, magnitude: float = 1.0) -> float:
        """
        Adjust the parameter value.
        
        Args:
            direction: Direction of adjustment
            magnitude: Magnitude multiplier
        
        Returns:
            New parameter value
        """
        if direction == AdjustmentDirection.MAINTAIN:
            return self.current_value
        
        delta = self.adjustment_rate * magnitude
        
        if direction == AdjustmentDirection.INCREASE:
            new_value = min(self.max_value, self.current_value + delta)
        else:
            new_value = max(self.min_value, self.current_value - delta)
        
        # Record adjustment
        self.adjustment_history.append({
            "from": self.current_value,
            "to": new_value,
            "direction": direction.value,
            "magnitude": magnitude,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Limit history size to prevent memory issues
        if len(self.adjustment_history) > self.MAX_HISTORY_SIZE:
            self.adjustment_history.pop(0)
        
        self.current_value = new_value
        self.total_adjustments += 1
        self.last_adjustment = datetime.now().isoformat()
        
        return new_value
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "current_value": self.current_value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "adjustment_rate": self.adjustment_rate,
            "total_adjustments": self.total_adjustments,
            "last_adjustment": self.last_adjustment,
        }


@dataclass
class OptimizationResult:
    """Result of a strategy optimization step."""
    timestamp: str
    feedback_count: int
    signal_breakdown: Dict[str, int]
    
    # Parameter adjustments
    adjustments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Overall effect
    overall_direction: str = "maintain"
    confidence: float = 0.0
    
    # Metadata
    strategy_used: str = "gradient"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "feedback_count": self.feedback_count,
            "signal_breakdown": self.signal_breakdown,
            "adjustments": self.adjustments,
            "overall_direction": self.overall_direction,
            "confidence": self.confidence,
            "strategy_used": self.strategy_used,
            "metadata": self.metadata,
        }


class StrategyOptimizer:
    """
    Feedback-driven strategy optimizer.
    
    Adjusts strategy parameters based on collected feedback:
    - Positive feedback → strengthen current strategy
    - Negative feedback → explore alternatives
    - Neutral feedback → maintain current approach
    
    Example:
        >>> optimizer = StrategyOptimizer()
        >>> 
        >>> # Define parameters
        >>> optimizer.add_parameter("learning_rate", 0.1, 0.01, 0.5)
        >>> optimizer.add_parameter("exploration_rate", 0.2, 0.0, 0.5)
        >>> 
        >>> # Collect feedback
        >>> optimizer.collect_feedback(feedback)
        >>> 
        >>> # Optimize
        >>> result = optimizer.optimize()
        >>> print(result.adjustments)
    """
    
    # Default parameters
    DEFAULT_PARAMETERS = {
        "learning_rate": {
            "default": 0.1,
            "min": 0.01,
            "max": 0.5,
            "adjustment_rate": 0.02,
        },
        "exploration_rate": {
            "default": 0.2,
            "min": 0.0,
            "max": 0.5,
            "adjustment_rate": 0.05,
        },
        "confidence_threshold": {
            "default": 0.7,
            "min": 0.5,
            "max": 0.95,
            "adjustment_rate": 0.05,
        },
    }
    
    def __init__(
        self,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.GRADIENT,
        data_dir: Optional[str] = None,
    ):
        """
        Initialize StrategyOptimizer.
        
        Args:
            optimization_strategy: Strategy optimization approach
            data_dir: Directory for storing optimization data
        """
        self.optimization_strategy = optimization_strategy
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data")
        
        # Parameters
        self.parameters: Dict[str, StrategyParameter] = {}
        
        # Feedback collection
        self._explicit_feedbacks: List[Feedback] = []
        self._implicit_signals: List[ImplicitSignal] = []
        
        # Signal fusion
        self._fusion = SignalFusion()
        
        # Optimization history
        self._optimization_history: List[OptimizationResult] = []
        
        # Initialize default parameters
        self._initialize_default_parameters()
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _initialize_default_parameters(self) -> None:
        """Initialize default strategy parameters."""
        for name, config in self.DEFAULT_PARAMETERS.items():
            self.add_parameter(
                name=name,
                initial_value=config["default"],
                min_value=config["min"],
                max_value=config["max"],
                adjustment_rate=config["adjustment_rate"],
            )
    
    def add_parameter(
        self,
        name: str,
        initial_value: float,
        min_value: float,
        max_value: float,
        adjustment_rate: float = 0.1,
    ) -> None:
        """
        Add a tunable parameter.
        
        Args:
            name: Parameter name
            initial_value: Initial value
            min_value: Minimum value
            max_value: Maximum value
            adjustment_rate: Rate of adjustment per step
        """
        self.parameters[name] = StrategyParameter(
            name=name,
            current_value=initial_value,
            min_value=min_value,
            max_value=max_value,
            adjustment_rate=adjustment_rate,
        )
    
    def get_parameter(self, name: str) -> Optional[float]:
        """
        Get current value of a parameter.
        
        Args:
            name: Parameter name
        
        Returns:
            Current value or None if not found
        """
        param = self.parameters.get(name)
        return param.current_value if param else None
    
    def set_parameter(self, name: str, value: float) -> bool:
        """
        Set parameter value directly.
        
        Args:
            name: Parameter name
            value: New value
        
        Returns:
            True if successful, False if parameter not found
        """
        param = self.parameters.get(name)
        if param:
            param.current_value = max(param.min_value, min(param.max_value, value))
            return True
        return False
    
    def collect_feedback(self, feedback: Feedback) -> None:
        """
        Collect explicit feedback.
        
        Args:
            feedback: Explicit feedback to collect
        """
        self._explicit_feedbacks.append(feedback)
        self._fusion.add_explicit(feedback)
    
    def collect_implicit(self, signal: ImplicitSignal) -> None:
        """
        Collect implicit signal.
        
        Args:
            signal: Implicit signal to collect
        """
        self._implicit_signals.append(signal)
        self._fusion.add_implicit(signal)
    
    def collect_feedback_batch(self, feedbacks: List[Feedback]) -> None:
        """Collect multiple explicit feedbacks."""
        for fb in feedbacks:
            self.collect_feedback(fb)
    
    def collect_implicit_batch(self, signals: List[ImplicitSignal]) -> None:
        """Collect multiple implicit signals."""
        for signal in signals:
            self.collect_implicit(signal)
    
    def optimize(
        self,
        session_id: Optional[str] = None,
        clear_feedback: bool = True,
    ) -> OptimizationResult:
        """
        Optimize strategy parameters based on collected feedback.
        
        Args:
            session_id: Optional session ID for context
            clear_feedback: Whether to clear feedback after optimization (default: True)
        
        Returns:
            OptimizationResult with adjustments made
        """
        # Fuse all signals
        fused = self._fusion.fuse(session_id=session_id)
        
        # Determine overall direction
        if fused.signal == "positive":
            # Positive feedback: maintain or slightly increase confidence
            overall_direction = AdjustmentDirection.MAINTAIN
            # Slightly decrease exploration
            self._adjust_exploration(AdjustmentDirection.DECREASE, 0.5)
        elif fused.signal == "negative":
            # Negative feedback: increase exploration
            overall_direction = AdjustmentDirection.DECREASE
            self._adjust_exploration(AdjustmentDirection.INCREASE, 1.0)
            # Adjust learning rate
            self._adjust_learning_rate(AdjustmentDirection.INCREASE, 0.5)
        else:
            # Neutral: maintain current approach
            overall_direction = AdjustmentDirection.MAINTAIN
        
        # Get signal breakdown
        breakdown = self._fusion.get_signal_breakdown()
        
        # Build result
        adjustments = {}
        for name, param in self.parameters.items():
            if param.adjustment_history:
                last_adj = param.adjustment_history[-1]
                adjustments[name] = {
                    "from": last_adj["from"],
                    "to": last_adj["to"],
                    "direction": last_adj["direction"],
                }
        
        result = OptimizationResult(
            timestamp=datetime.now().isoformat(),
            feedback_count=fused.explicit_count + fused.implicit_count,
            signal_breakdown=breakdown,
            adjustments=adjustments,
            overall_direction=overall_direction.value,
            confidence=fused.confidence,
            strategy_used=self.optimization_strategy.value,
            metadata={
                "fused_signal": fused.signal,
                "explicit_score": fused.explicit_score,
                "implicit_score": fused.implicit_score,
            },
        )
        
        # Record in history
        self._optimization_history.append(result)
        
        # Clear collected feedback (optional)
        if clear_feedback:
            self._fusion.clear()
            self._explicit_feedbacks.clear()
            self._implicit_signals.clear()
        
        return result
    
    def _adjust_exploration(
        self,
        direction: AdjustmentDirection,
        magnitude: float = 1.0,
    ) -> None:
        """Adjust exploration rate parameter."""
        if "exploration_rate" in self.parameters:
            self.parameters["exploration_rate"].adjust(direction, magnitude)
    
    def _adjust_learning_rate(
        self,
        direction: AdjustmentDirection,
        magnitude: float = 1.0,
    ) -> None:
        """Adjust learning rate parameter."""
        if "learning_rate" in self.parameters:
            self.parameters["learning_rate"].adjust(direction, magnitude)
    
    def get_optimization_history(
        self,
        limit: Optional[int] = None,
    ) -> List[OptimizationResult]:
        """
        Get optimization history.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of optimization results
        """
        if limit:
            return self._optimization_history[-limit:]
        return self._optimization_history.copy()
    
    def get_parameter_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all parameters.
        
        Returns:
            Dictionary with parameter status
        """
        return {
            name: param.to_dict()
            for name, param in self.parameters.items()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get optimization statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self._optimization_history:
            return {
                "total_optimizations": 0,
                "avg_confidence": 0.0,
                "direction_distribution": {},
            }
        
        total = len(self._optimization_history)
        avg_confidence = sum(r.confidence for r in self._optimization_history) / total
        
        direction_dist = {}
        for result in self._optimization_history:
            direction = result.overall_direction
            direction_dist[direction] = direction_dist.get(direction, 0) + 1
        
        return {
            "total_optimizations": total,
            "avg_confidence": avg_confidence,
            "direction_distribution": direction_dist,
            "parameters": self.get_parameter_status(),
        }
    
    def reset_parameters(self) -> None:
        """Reset all parameters to default values."""
        for name, config in self.DEFAULT_PARAMETERS.items():
            if name in self.parameters:
                self.parameters[name].current_value = config["default"]
                self.parameters[name].total_adjustments = 0
                self.parameters[name].adjustment_history.clear()
    
    def save_state(self, path: Optional[str] = None) -> str:
        """
        Save optimizer state to file.
        
        Args:
            path: Optional path to save to
        
        Returns:
            Path where state was saved
        """
        if path is None:
            path = os.path.join(self.data_dir, "optimizer_state.json")
        
        state = {
            "optimization_strategy": self.optimization_strategy.value,
            "parameters": self.get_parameter_status(),
            "optimization_history": [r.to_dict() for r in self._optimization_history[-100:]],  # Last 100
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        return path
    
    def load_state(self, path: Optional[str] = None) -> bool:
        """
        Load optimizer state from file.
        
        Args:
            path: Optional path to load from
        
        Returns:
            True if loaded successfully
        """
        if path is None:
            path = os.path.join(self.data_dir, "optimizer_state.json")
        
        if not os.path.exists(path):
            return False
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            # Restore optimization strategy
            if "optimization_strategy" in state:
                self.optimization_strategy = OptimizationStrategy(state["optimization_strategy"])
            
            # Restore parameters with validation
            for name, param_data in state.get("parameters", {}).items():
                if name in self.parameters:
                    # Validate value is within bounds
                    value = param_data.get("current_value", self.DEFAULT_PARAMETERS.get(name, {}).get("default", 0.5))
                    param = self.parameters[name]
                    
                    if param.min_value <= value <= param.max_value:
                        param.current_value = value
                    else:
                        # Use default if out of bounds
                        param.current_value = self.DEFAULT_PARAMETERS.get(name, {}).get("default", param.current_value)
                    
                    param.total_adjustments = param_data.get("total_adjustments", 0)
            
            # Restore history
            self._optimization_history = [
                OptimizationResult(**r) for r in state.get("optimization_history", [])
            ]
            
            return True
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    def __repr__(self) -> str:
        return (
            f"StrategyOptimizer(strategy={self.optimization_strategy.value}, "
            f"parameters={len(self.parameters)}, "
            f"optimizations={len(self._optimization_history)})"
        )
