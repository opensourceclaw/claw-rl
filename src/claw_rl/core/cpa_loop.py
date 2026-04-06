"""
C-P-A Loop - Continuous Planning and Autonomous Learning Loop

This module implements the core C-P-A learning loop that orchestrates
the learning process through Observe, Orient, Decide, Act, and Learn phases.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time

from ..protocols.observer import ObserverProtocol, Observation
from ..protocols.decision_maker import DecisionMakerProtocol, Decision, DecisionType
from ..protocols.executor import ExecutorProtocol, ExecutionResult, ExecutionStatus
from ..protocols.signal_adapter import SignalAdapterProtocol, AdaptedSignal


class CPAPhase(Enum):
    """C-P-A Loop phases."""
    OBSERVE = "observe"
    ORIENT = "orient"
    DECIDE = "decide"
    ACT = "act"
    LEARN = "learn"


class CPALoopState(Enum):
    """C-P-A Loop states."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class CPALoopConfig:
    """
    Configuration for C-P-A Loop.
    
    Attributes:
        max_iterations: Maximum iterations per run (0 = unlimited)
        iteration_delay_ms: Delay between iterations in milliseconds
        auto_learn: Whether to automatically learn from results
        enable_logging: Whether to enable logging
        observer: Optional observer instance
        decision_maker: Optional decision maker instance
        executor: Optional executor instance
        signal_adapter: Optional signal adapter instance
    """
    max_iterations: int = 0
    iteration_delay_ms: int = 100
    auto_learn: bool = True
    enable_logging: bool = True
    observer: Optional[ObserverProtocol] = None
    decision_maker: Optional[DecisionMakerProtocol] = None
    executor: Optional[ExecutorProtocol] = None
    signal_adapter: Optional[SignalAdapterProtocol] = None


@dataclass
class CPALoopResult:
    """
    Result of a C-P-A loop iteration.
    
    Attributes:
        iteration: Iteration number
        phase: Current phase
        observation: Observation from observe phase
        decision: Decision from decide phase
        execution_result: Result from act phase
        learning_result: Result from learn phase
        duration_ms: Duration in milliseconds
        timestamp: When the iteration occurred
    """
    iteration: int
    phase: CPAPhase
    observation: Optional[Observation] = None
    decision: Optional[Decision] = None
    execution_result: Optional[ExecutionResult] = None
    learning_result: Optional[Dict[str, Any]] = None
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class CPALoop:
    """
    Continuous Planning and Autonomous Learning Loop.
    
    The C-P-A loop orchestrates the learning process through five phases:
    1. Observe: Collect observations from the environment
    2. Orient: Analyze and orient the observations
    3. Decide: Make decisions based on analysis
    4. Act: Execute the decisions
    5. Learn: Learn from the results
    
    This implementation is framework-agnostic and works with any
    Observer, DecisionMaker, and Executor implementations.
    
    Example:
        >>> from claw_rl.protocols import ObserverProtocol, DecisionMakerProtocol
        >>> from claw_rl.core import CPALoop, CPALoopConfig
        >>> 
        >>> class MyObserver(ObserverProtocol):
        ...     def observe(self) -> Observation:
        ...         return Observation(timestamp="", metrics={}, feedback={}, context={}, metadata={})
        ...     # ... implement other methods
        >>> 
        >>> config = CPALoopConfig(
        ...     max_iterations=10,
        ...     observer=MyObserver(),
        ... )
        >>> loop = CPALoop(config)
        >>> results = loop.run()
    """
    
    def __init__(self, config: Optional[CPALoopConfig] = None):
        """
        Initialize C-P-A Loop.
        
        Args:
            config: Optional configuration
        """
        self.config = config or CPALoopConfig()
        self.observer = self.config.observer
        self.decision_maker = self.config.decision_maker
        self.executor = self.config.executor
        self.signal_adapter = self.config.signal_adapter
        
        self._state = CPALoopState.IDLE
        self._iteration = 0
        self._results: List[CPALoopResult] = []
        self._observations: List[Observation] = []
        self._decisions: List[Decision] = []
        self._signals: List[AdaptedSignal] = []
    
    def run(
        self,
        max_iterations: Optional[int] = None,
        observer: Optional[ObserverProtocol] = None,
        decision_maker: Optional[DecisionMakerProtocol] = None,
        executor: Optional[ExecutorProtocol] = None,
    ) -> List[CPALoopResult]:
        """
        Run the C-P-A loop.
        
        Args:
            max_iterations: Override max iterations
            observer: Override observer
            decision_maker: Override decision maker
            executor: Override executor
            
        Returns:
            List of iteration results
        """
        # Use provided components or defaults
        observer = observer or self.observer
        decision_maker = decision_maker or self.decision_maker
        executor = executor or self.executor
        
        # Determine max iterations
        max_iter = max_iterations if max_iterations is not None else self.config.max_iterations
        if max_iter == 0:
            max_iter = float('inf')
        
        # Check required components
        if not observer:
            raise ValueError("Observer is required for C-P-A loop")
        
        # Reset state
        self._state = CPALoopState.RUNNING
        self._iteration = 0
        self._results.clear()
        
        try:
            while self._state == CPALoopState.RUNNING and self._iteration < max_iter:
                result = self._run_iteration(observer, decision_maker, executor)
                self._results.append(result)
                self._iteration += 1
                
                # Delay between iterations
                if self.config.iteration_delay_ms > 0:
                    time.sleep(self.config.iteration_delay_ms / 1000.0)
        
        finally:
            self._state = CPALoopState.STOPPED
        
        return self._results
    
    def _run_iteration(
        self,
        observer: ObserverProtocol,
        decision_maker: Optional[DecisionMakerProtocol],
        executor: Optional[ExecutorProtocol],
    ) -> CPALoopResult:
        """
        Run a single iteration of the C-P-A loop.
        
        Args:
            observer: Observer instance
            decision_maker: Decision maker instance
            executor: Executor instance
            
        Returns:
            Iteration result
        """
        start_time = time.time()
        iteration = self._iteration
        
        # Phase 1: Observe
        observation = self._observe(observer)
        self._observations.append(observation)
        
        # Phase 2: Orient (analyze observation)
        oriented_data = self._orient(observation)
        
        # Phase 3: Decide
        decision = None
        if decision_maker:
            decision = self._decide(decision_maker, oriented_data)
            self._decisions.append(decision)
        
        # Phase 4: Act
        execution_result = None
        if executor and decision:
            execution_result = self._act(executor, decision)
        
        # Phase 5: Learn
        learning_result = None
        if self.config.auto_learn:
            learning_result = self._learn(observation, decision, execution_result)
        
        duration_ms = (time.time() - start_time) * 1000
        
        return CPALoopResult(
            iteration=iteration,
            phase=CPAPhase.LEARN,
            observation=observation,
            decision=decision,
            execution_result=execution_result,
            learning_result=learning_result,
            duration_ms=duration_ms,
        )
    
    def _observe(self, observer: ObserverProtocol) -> Observation:
        """
        Observe phase: Collect observations.
        
        Args:
            observer: Observer instance
            
        Returns:
            Observation
        """
        if self.config.enable_logging:
            pass  # Log observation start
        
        observation = observer.observe()
        
        return observation
    
    def _orient(self, observation: Observation) -> Dict[str, Any]:
        """
        Orient phase: Analyze and orient observations.
        
        Args:
            observation: Observation to orient
            
        Returns:
            Oriented data
        """
        # Combine metrics, feedback, and context
        oriented = {
            "metrics": observation.metrics.copy(),
            "feedback": observation.feedback.copy(),
            "context": observation.context.copy(),
            "timestamp": observation.timestamp,
        }
        
        # Calculate derived metrics
        if observation.metrics:
            oriented["derived"] = self._calculate_derived_metrics(observation.metrics)
        
        return oriented
    
    def _calculate_derived_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate derived metrics from raw metrics.
        
        Args:
            metrics: Raw metrics
            
        Returns:
            Derived metrics
        """
        derived = {}
        
        # Calculate success rate if available
        if "success_count" in metrics and "total_count" in metrics:
            total = metrics["total_count"]
            if total > 0:
                derived["success_rate"] = metrics["success_count"] / total
        
        # Calculate error rate if available
        if "error_count" in metrics and "total_count" in metrics:
            total = metrics["total_count"]
            if total > 0:
                derived["error_rate"] = metrics["error_count"] / total
        
        return derived
    
    def _decide(
        self,
        decision_maker: DecisionMakerProtocol,
        oriented_data: Dict[str, Any],
    ) -> Decision:
        """
        Decide phase: Make decisions based on oriented data.
        
        Args:
            decision_maker: Decision maker instance
            oriented_data: Oriented data
            
        Returns:
            Decision
        """
        return decision_maker.decide(oriented_data)
    
    def _act(
        self,
        executor: ExecutorProtocol,
        decision: Decision,
    ) -> ExecutionResult:
        """
        Act phase: Execute decisions.
        
        Args:
            executor: Executor instance
            decision: Decision to execute
            
        Returns:
            Execution result
        """
        return executor.execute(decision.to_dict())
    
    def _learn(
        self,
        observation: Observation,
        decision: Optional[Decision],
        execution_result: Optional[ExecutionResult],
    ) -> Dict[str, Any]:
        """
        Learn phase: Learn from results.
        
        Args:
            observation: Observation from observe phase
            decision: Decision from decide phase
            execution_result: Result from act phase
            
        Returns:
            Learning result
        """
        learning_result = {
            "observation_id": observation.timestamp,
            "had_decision": decision is not None,
            "had_execution": execution_result is not None,
        }
        
        if decision:
            learning_result["decision_type"] = decision.decision_type.value
            learning_result["decision_confidence"] = decision.confidence
        
        if execution_result:
            learning_result["execution_success"] = execution_result.success
            learning_result["execution_status"] = execution_result.status.value
        
        return learning_result
    
    def pause(self) -> None:
        """Pause the loop."""
        self._state = CPALoopState.PAUSED
    
    def resume(self) -> None:
        """Resume the loop."""
        self._state = CPALoopState.RUNNING
    
    def stop(self) -> None:
        """Stop the loop."""
        self._state = CPALoopState.STOPPED
    
    def get_state(self) -> CPALoopState:
        """Get current loop state."""
        return self._state
    
    def get_iteration(self) -> int:
        """Get current iteration number."""
        return self._iteration
    
    def get_results(self) -> List[CPALoopResult]:
        """Get all iteration results."""
        return self._results.copy()
    
    def get_observations(self) -> List[Observation]:
        """Get all observations."""
        return self._observations.copy()
    
    def get_decisions(self) -> List[Decision]:
        """Get all decisions."""
        return self._decisions.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get loop statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self._results:
            return {
                "total_iterations": 0,
                "total_duration_ms": 0.0,
                "avg_duration_ms": 0.0,
                "success_rate": 0.0,
            }
        
        total_duration = sum(r.duration_ms for r in self._results)
        successful = sum(1 for r in self._results if r.execution_result and r.execution_result.success)
        total_executions = sum(1 for r in self._results if r.execution_result)
        
        return {
            "total_iterations": len(self._results),
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / len(self._results),
            "success_rate": successful / total_executions if total_executions > 0 else 0.0,
            "decisions_made": len(self._decisions),
            "observations_collected": len(self._observations),
        }
    
    def reset(self) -> None:
        """Reset the loop state."""
        self._state = CPALoopState.IDLE
        self._iteration = 0
        self._results.clear()
        self._observations.clear()
        self._decisions.clear()
        self._signals.clear()
        
        if self.observer:
            self.observer.reset()
        if self.decision_maker:
            self.decision_maker.reset()
        if self.executor:
            self.executor.reset()
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CPALoop("
            f"state={self._state.value}, "
            f"iteration={self._iteration}, "
            f"results={len(self._results)}"
            f")"
        )
