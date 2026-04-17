# CPALoop Integration Test (Corrected)

import pytest
from pathlib import Path
from claw_rl.core.cpa_loop import CPALoop, CPALoopConfig
from claw_rl.protocols.observer import ObserverProtocol, Observation
from claw_rl.protocols.decision_maker import DecisionMakerProtocol, Decision, DecisionType
from claw_rl.protocols.executor import ExecutorProtocol, ExecutionResult, ExecutionStatus

class MockObserver(ObserverProtocol):
    def observe(self) -> Observation:
        return Observation(
            timestamp="",
            metrics={},
            feedback={},
            context={},
            metadata={}
        )

class MockDecisionMaker(DecisionMakerProtocol):
    def decide(self, observation: Observation) -> Decision:
        return Decision(
            decision_id="test_dec_001",
            decision_type=DecisionType.PARAMETER_ADJUST,
            action="test_action",
            parameters={"test": "value"},
            confidence=0.95,
            reasoning="test reason"
        )

class MockExecutor(ExecutorProtocol):
    def execute(self, decision: Decision) -> ExecutionResult:
        return ExecutionResult(
            decision_id="test_exec_001",
            status=ExecutionStatus.SUCCESS,
            success=True,
            result={"test": "result"},
            metrics={"test": "metric"}
        )

def test_cpa_loop_initialization():
    """Test CPALoop initialization"""
    config = CPALoopConfig()
    loop = CPALoop(config)
    assert loop is not None
    assert hasattr(loop, 'config')
    assert hasattr(loop, 'run')

def test_cpa_loop_run_with_mock_components():
    """Test CPALoop run with mock components"""
    # Create mock components
    observer = MockObserver()
    decision_maker = MockDecisionMaker()
    executor = MockExecutor()
    
    # Create config with mocks
    config = CPALoopConfig(
        observer=observer,
        decision_maker=decision_maker,
        executor=executor
    )
    
    loop = CPALoop(config)
    
    # Run loop (with limited iterations)
    results = loop.run(max_iterations=1)
    
    assert results is not None
    assert len(results) == 1
    assert results[0].phase in ["observe", "orient"]

def test_cpa_loop_config_validation():
    """Test CPALoop config validation"""
    # Test with minimal config
    config = CPALoopConfig()
    loop = CPALoop(config)
    
    # Should be able to initialize even without components
    assert loop.config.max_iterations == 0
    assert loop.config.iteration_delay_ms == 100
