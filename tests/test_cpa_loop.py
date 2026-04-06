"""
Tests for C-P-A Loop
"""

import pytest
from typing import Dict, Any, Optional
from datetime import datetime

from claw_rl.core.cpa_loop import (
    CPALoop,
    CPALoopConfig,
    CPALoopState,
    CPAPhase,
    CPALoopResult,
)
from claw_rl.protocols.observer import ObserverProtocol, Observation
from claw_rl.protocols.decision_maker import DecisionMakerProtocol, Decision, DecisionType
from claw_rl.protocols.executor import ExecutorProtocol, ExecutionResult, ExecutionStatus


class MockObserver(ObserverProtocol):
    """Mock observer for testing."""
    
    def __init__(self):
        self.call_count = 0
        self._metrics: Dict[str, Any] = {}
        self._feedback: Dict[str, Any] = {}
        self._context: Dict[str, Any] = {}
    
    def observe(self) -> Observation:
        self.call_count += 1
        return Observation(
            timestamp=datetime.now().isoformat(),
            metrics=self._metrics.copy(),
            feedback=self._feedback.copy(),
            context=self._context.copy(),
            metadata={"call_count": self.call_count},
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        return self._metrics.copy()
    
    def get_feedback(self) -> Dict[str, Any]:
        return self._feedback.copy()
    
    def get_context(self) -> Dict[str, Any]:
        return self._context.copy()
    
    def reset(self) -> None:
        self.call_count = 0
        self._metrics.clear()
        self._feedback.clear()
        self._context.clear()
    
    def set_metrics(self, metrics: Dict[str, Any]) -> None:
        self._metrics = metrics
    
    def set_feedback(self, feedback: Dict[str, Any]) -> None:
        self._feedback = feedback


class MockDecisionMaker(DecisionMakerProtocol):
    """Mock decision maker for testing."""
    
    def __init__(self):
        self.call_count = 0
        self.decision_type = DecisionType.NO_ACTION
    
    def decide(self, observations: Dict[str, Any]) -> Decision:
        self.call_count += 1
        return Decision(
            decision_id=f"dec_{self.call_count:04d}",
            decision_type=self.decision_type,
            action="test_action",
            parameters={"test": True},
            confidence=0.9,
            reasoning="Test decision",
        )
    
    def get_confidence(self, observations: Dict[str, Any]) -> float:
        return 0.9
    
    def explain(self, decision: Decision) -> str:
        return f"Decision {decision.decision_id}: test explanation"
    
    def reset(self) -> None:
        self.call_count = 0


class MockExecutor(ExecutorProtocol):
    """Mock executor for testing."""
    
    def __init__(self):
        self.call_count = 0
        self.should_succeed = True
    
    def execute(self, decision: Dict[str, Any]) -> ExecutionResult:
        self.call_count += 1
        return ExecutionResult(
            decision_id=decision.get("decision_id", "unknown"),
            status=ExecutionStatus.SUCCESS if self.should_succeed else ExecutionStatus.FAILED,
            success=self.should_succeed,
            result={"executed": True},
        )
    
    def rollback(self, decision_id: str) -> ExecutionResult:
        return ExecutionResult(
            decision_id=decision_id,
            status=ExecutionStatus.ROLLED_BACK,
            success=True,
            result={"rolled_back": True},
        )
    
    def get_status(self, decision_id: str) -> Optional[ExecutionStatus]:
        return ExecutionStatus.SUCCESS
    
    def get_metrics(self) -> Dict[str, Any]:
        return {"total_executions": self.call_count}
    
    def reset(self) -> None:
        self.call_count = 0


class TestCPALoopConfig:
    """Tests for CPALoopConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CPALoopConfig()
        
        assert config.max_iterations == 0
        assert config.iteration_delay_ms == 100
        assert config.auto_learn is True
        assert config.enable_logging is True
        assert config.observer is None
    
    def test_custom_config(self):
        """Test custom configuration."""
        observer = MockObserver()
        config = CPALoopConfig(
            max_iterations=10,
            iteration_delay_ms=50,
            auto_learn=False,
            observer=observer,
        )
        
        assert config.max_iterations == 10
        assert config.iteration_delay_ms == 50
        assert config.auto_learn is False
        assert config.observer == observer


class TestCPALoopResult:
    """Tests for CPALoopResult."""
    
    def test_create_result(self):
        """Test creating a result."""
        result = CPALoopResult(
            iteration=1,
            phase=CPAPhase.LEARN,
        )
        
        assert result.iteration == 1
        assert result.phase == CPAPhase.LEARN
        assert result.observation is None
        assert result.decision is None
        assert result.execution_result is None
    
    def test_result_with_data(self):
        """Test result with data."""
        observation = Observation(
            timestamp="2026-04-06T10:00:00",
            metrics={"accuracy": 0.9},
            feedback={},
            context={},
            metadata={},
        )
        decision = Decision(
            decision_id="dec_001",
            decision_type=DecisionType.NO_ACTION,
            action="none",
            parameters={},
            confidence=1.0,
        )
        
        result = CPALoopResult(
            iteration=1,
            phase=CPAPhase.ACT,
            observation=observation,
            decision=decision,
            duration_ms=10.5,
        )
        
        assert result.observation.metrics["accuracy"] == 0.9
        assert result.decision.decision_id == "dec_001"
        assert result.duration_ms == 10.5


class TestCPALoop:
    """Tests for CPALoop."""
    
    def test_create_loop(self):
        """Test creating a loop."""
        observer = MockObserver()
        config = CPALoopConfig(observer=observer)
        loop = CPALoop(config)
        
        assert loop.observer == observer
        assert loop.get_state() == CPALoopState.IDLE
    
    def test_run_without_observer(self):
        """Test running without observer raises error."""
        loop = CPALoop()
        
        with pytest.raises(ValueError, match="Observer is required"):
            loop.run()
    
    def test_run_single_iteration(self):
        """Test running a single iteration."""
        observer = MockObserver()
        loop = CPALoop(CPALoopConfig(observer=observer))
        
        results = loop.run(max_iterations=1)
        
        assert len(results) == 1
        assert observer.call_count == 1
        assert loop.get_iteration() == 1
    
    def test_run_multiple_iterations(self):
        """Test running multiple iterations."""
        observer = MockObserver()
        loop = CPALoop(CPALoopConfig(
            observer=observer,
            iteration_delay_ms=0,  # No delay for testing
        ))
        
        results = loop.run(max_iterations=5)
        
        assert len(results) == 5
        assert observer.call_count == 5
    
    def test_run_with_all_components(self):
        """Test running with all components."""
        observer = MockObserver()
        decision_maker = MockDecisionMaker()
        executor = MockExecutor()
        
        loop = CPALoop(CPALoopConfig(
            observer=observer,
            decision_maker=decision_maker,
            executor=executor,
            iteration_delay_ms=0,
        ))
        
        results = loop.run(max_iterations=3)
        
        assert len(results) == 3
        assert observer.call_count == 3
        assert decision_maker.call_count == 3
        assert executor.call_count == 3
        
        # Check results have all phases
        for result in results:
            assert result.observation is not None
            assert result.decision is not None
            assert result.execution_result is not None
            assert result.learning_result is not None
    
    def test_run_without_decision_maker(self):
        """Test running without decision maker."""
        observer = MockObserver()
        executor = MockExecutor()
        
        loop = CPALoop(CPALoopConfig(
            observer=observer,
            executor=executor,
            iteration_delay_ms=0,
        ))
        
        results = loop.run(max_iterations=2)
        
        assert len(results) == 2
        assert executor.call_count == 0  # No decisions to execute
        
        for result in results:
            assert result.decision is None
            assert result.execution_result is None
    
    def test_pause_and_resume(self):
        """Test pause and resume."""
        observer = MockObserver()
        loop = CPALoop(CPALoopConfig(
            observer=observer,
            iteration_delay_ms=10,
        ))
        
        # Start running in background (simplified for test)
        loop._state = CPALoopState.RUNNING
        loop.pause()
        
        assert loop.get_state() == CPALoopState.PAUSED
        
        loop.resume()
        assert loop.get_state() == CPALoopState.RUNNING
    
    def test_stop(self):
        """Test stopping the loop."""
        observer = MockObserver()
        loop = CPALoop(CPALoopConfig(observer=observer))
        
        loop._state = CPALoopState.RUNNING
        loop.stop()
        
        assert loop.get_state() == CPALoopState.STOPPED
    
    def test_reset(self):
        """Test resetting the loop."""
        observer = MockObserver()
        decision_maker = MockDecisionMaker()
        executor = MockExecutor()
        
        loop = CPALoop(CPALoopConfig(
            observer=observer,
            decision_maker=decision_maker,
            executor=executor,
        ))
        
        loop.run(max_iterations=3)
        
        assert loop.get_iteration() == 3
        assert len(loop.get_results()) == 3
        
        loop.reset()
        
        assert loop.get_iteration() == 0
        assert len(loop.get_results()) == 0
        assert observer.call_count == 0  # Observer was reset
    
    def test_get_statistics(self):
        """Test getting statistics."""
        observer = MockObserver()
        decision_maker = MockDecisionMaker()
        executor = MockExecutor()
        
        loop = CPALoop(CPALoopConfig(
            observer=observer,
            decision_maker=decision_maker,
            executor=executor,
            iteration_delay_ms=0,
        ))
        
        loop.run(max_iterations=5)
        
        stats = loop.get_statistics()
        
        assert stats["total_iterations"] == 5
        assert stats["decisions_made"] == 5
        assert stats["observations_collected"] == 5
        assert stats["success_rate"] == 1.0
        assert stats["avg_duration_ms"] > 0
    
    def test_get_statistics_empty(self):
        """Test getting statistics when no iterations."""
        loop = CPALoop()
        
        stats = loop.get_statistics()
        
        assert stats["total_iterations"] == 0
        assert stats["avg_duration_ms"] == 0.0
        assert stats["success_rate"] == 0.0
    
    def test_get_observations(self):
        """Test getting observations."""
        observer = MockObserver()
        loop = CPALoop(CPALoopConfig(observer=observer))
        
        loop.run(max_iterations=3)
        
        observations = loop.get_observations()
        
        assert len(observations) == 3
    
    def test_get_decisions(self):
        """Test getting decisions."""
        observer = MockObserver()
        decision_maker = MockDecisionMaker()
        
        loop = CPALoop(CPALoopConfig(
            observer=observer,
            decision_maker=decision_maker,
        ))
        
        loop.run(max_iterations=3)
        
        decisions = loop.get_decisions()
        
        assert len(decisions) == 3
    
    def test_run_with_override_components(self):
        """Test running with override components."""
        observer1 = MockObserver()
        observer2 = MockObserver()
        
        loop = CPALoop(CPALoopConfig(observer=observer1))
        
        # Override with observer2
        results = loop.run(max_iterations=2, observer=observer2)
        
        assert len(results) == 2
        assert observer2.call_count == 2
        assert observer1.call_count == 0
    
    def test_repr(self):
        """Test string representation."""
        observer = MockObserver()
        loop = CPALoop(CPALoopConfig(observer=observer))
        
        result = repr(loop)
        
        assert "CPALoop" in result
        assert "state=idle" in result
        assert "iteration=0" in result


class TestCPAPhase:
    """Tests for CPAPhase."""
    
    def test_phase_values(self):
        """Test phase values."""
        assert CPAPhase.OBSERVE.value == "observe"
        assert CPAPhase.ORIENT.value == "orient"
        assert CPAPhase.DECIDE.value == "decide"
        assert CPAPhase.ACT.value == "act"
        assert CPAPhase.LEARN.value == "learn"


class TestCPALoopState:
    """Tests for CPALoopState."""
    
    def test_state_values(self):
        """Test state values."""
        assert CPALoopState.IDLE.value == "idle"
        assert CPALoopState.RUNNING.value == "running"
        assert CPALoopState.PAUSED.value == "paused"
        assert CPALoopState.STOPPED.value == "stopped"
