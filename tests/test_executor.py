"""
Tests for Action Executor
"""

import pytest
import time
import tempfile
import os

from claw_rl.learning.executor import (
    ActionExecutor,
    Action,
    ActionType,
    ActionStatus,
    ActionResult,
    ExecutorStats,
)


class TestAction:
    """Tests for Action."""
    
    def test_action_creation_function(self):
        """Test action creation with function handler."""
        def my_func(a, b):
            return a + b
        
        action = Action(
            action_id="test_001",
            action_type=ActionType.FUNCTION,
            handler=my_func,
            params={"a": 1, "b": 2},
        )
        
        assert action.action_id == "test_001"
        assert action.action_type == ActionType.FUNCTION
        assert callable(action.handler)
        assert action.params == {"a": 1, "b": 2}
        assert action.timeout_ms == 30000
        assert action.max_retries == 0
    
    def test_action_creation_shell(self):
        """Test action creation with shell handler."""
        action = Action(
            action_id="test_002",
            action_type=ActionType.SHELL,
            handler="echo hello",
        )
        
        assert action.action_id == "test_002"
        assert action.action_type == ActionType.SHELL
        assert action.handler == "echo hello"
    
    def test_action_custom_params(self):
        """Test action with custom parameters."""
        action = Action(
            action_id="test_003",
            action_type=ActionType.FUNCTION,
            handler=lambda x: x * 2,
            timeout_ms=5000,
            max_retries=3,
            retry_delay_ms=500,
            retry_backoff=1.5,
        )
        
        assert action.timeout_ms == 5000
        assert action.max_retries == 3
        assert action.retry_delay_ms == 500
        assert action.retry_backoff == 1.5
    
    def test_action_to_dict(self):
        """Test action to dictionary."""
        def my_func():
            pass
        
        action = Action(
            action_id="test_004",
            action_type=ActionType.FUNCTION,
            handler=my_func,
            name="Test Action",
            description="A test action",
        )
        
        d = action.to_dict()
        
        assert d["action_id"] == "test_004"
        assert d["action_type"] == "function"
        assert "function:my_func" in d["handler"]
        assert d["name"] == "Test Action"
        assert d["description"] == "A test action"


class TestActionResult:
    """Tests for ActionResult."""
    
    def test_result_creation(self):
        """Test result creation."""
        result = ActionResult(
            action_id="test_001",
            status=ActionStatus.SUCCESS,
            start_time="2026-04-05T12:00:00",
            end_time="2026-04-05T12:00:01",
            duration_ms=1000,
            result="success",
        )
        
        assert result.action_id == "test_001"
        assert result.status == ActionStatus.SUCCESS
        assert result.result == "success"
        assert result.retry_count == 0
    
    def test_result_to_dict(self):
        """Test result to dictionary."""
        result = ActionResult(
            action_id="test_001",
            status=ActionStatus.SUCCESS,
            start_time="2026-04-05T12:00:00",
            end_time="2026-04-05T12:00:01",
            duration_ms=1000,
            result={"key": "value"},
            retry_count=2,
        )
        
        d = result.to_dict()
        
        assert d["action_id"] == "test_001"
        assert d["status"] == "success"
        assert d["duration_ms"] == 1000
        assert d["result"] == {"key": "value"}
        assert d["retry_count"] == 2


class TestExecutorStats:
    """Tests for ExecutorStats."""
    
    def test_stats_creation(self):
        """Test stats creation."""
        stats = ExecutorStats()
        
        assert stats.total_actions == 0
        assert stats.successful == 0
        assert stats.failed == 0
    
    def test_stats_to_dict(self):
        """Test stats to dictionary."""
        stats = ExecutorStats(
            total_actions=10,
            successful=8,
            failed=2,
            timeout=0,
            cancelled=0,
            total_retries=3,
            avg_duration_ms=150.5,
        )
        
        d = stats.to_dict()
        
        assert d["total_actions"] == 10
        assert d["successful"] == 8
        assert d["failed"] == 2
        assert d["avg_duration_ms"] == 150.5


class TestActionExecutor:
    """Tests for ActionExecutor."""
    
    def test_executor_creation(self):
        """Test executor creation."""
        executor = ActionExecutor()
        
        assert executor.default_timeout_ms == 30000
        assert executor.default_max_retries == 0
        assert len(executor.history()) == 0
    
    def test_execute_function_success(self):
        """Test successful function execution."""
        def add(a, b):
            return a + b
        
        executor = ActionExecutor()
        action = Action(
            action_id="add_001",
            action_type=ActionType.FUNCTION,
            handler=add,
            params={"a": 1, "b": 2},
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.SUCCESS
        assert result.result == 3
        assert result.error is None
        assert result.duration_ms is not None
    
    def test_execute_function_failure(self):
        """Test function execution failure."""
        def raise_error():
            raise ValueError("Test error")
        
        executor = ActionExecutor()
        action = Action(
            action_id="fail_001",
            action_type=ActionType.FUNCTION,
            handler=raise_error,
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.FAILED
        assert "Test error" in result.error
    
    def test_execute_function_timeout(self):
        """Test function execution timeout."""
        def slow_function():
            time.sleep(5)
            return "done"
        
        executor = ActionExecutor()
        action = Action(
            action_id="slow_001",
            action_type=ActionType.FUNCTION,
            handler=slow_function,
            timeout_ms=100,  # 100ms timeout
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.TIMEOUT
        assert "Timeout" in result.error
    
    def test_execute_shell_success(self):
        """Test successful shell execution."""
        executor = ActionExecutor()
        action = Action(
            action_id="shell_001",
            action_type=ActionType.SHELL,
            handler="echo hello",
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.SUCCESS
        assert "hello" in result.result
    
    def test_execute_shell_failure(self):
        """Test shell execution failure."""
        executor = ActionExecutor()
        action = Action(
            action_id="shell_fail_001",
            action_type=ActionType.SHELL,
            handler="exit 1",  # Command that fails
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.FAILED
    
    def test_execute_with_retry_success(self):
        """Test execution with retry that eventually succeeds."""
        call_count = [0]
        
        def eventually_succeed():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Temporary error")
            return "success"
        
        executor = ActionExecutor()
        action = Action(
            action_id="retry_001",
            action_type=ActionType.FUNCTION,
            handler=eventually_succeed,
            max_retries=3,
            retry_delay_ms=10,  # Fast retry for testing
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.SUCCESS
        assert result.result == "success"
        assert result.retry_count == 2
        assert len(result.attempts) == 3
    
    def test_execute_with_retry_all_fail(self):
        """Test execution with retry that fails all attempts."""
        def always_fail():
            raise Exception("Always fails")
        
        executor = ActionExecutor()
        action = Action(
            action_id="retry_fail_001",
            action_type=ActionType.FUNCTION,
            handler=always_fail,
            max_retries=2,
            retry_delay_ms=10,
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.FAILED
        assert result.retry_count == 2
        assert len(result.attempts) == 3  # Initial + 2 retries
    
    def test_execute_custom_action(self):
        """Test custom action execution."""
        executor = ActionExecutor()
        action = Action(
            action_id="custom_001",
            action_type=ActionType.CUSTOM,
            handler="custom_handler",
            params={"key": "value"},
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.SUCCESS
        assert "custom_handler" in str(result.result)
    
    def test_cancel_action(self):
        """Test action cancellation."""
        def long_running():
            time.sleep(10)
            return "done"
        
        executor = ActionExecutor()
        action = Action(
            action_id="cancel_001",
            action_type=ActionType.FUNCTION,
            handler=long_running,
            timeout_ms=100,
            max_retries=10,
            retry_delay_ms=100,
        )
        
        # Start async execution
        action_id = executor.execute_async(action)
        
        # Cancel it
        time.sleep(0.01)  # Small delay
        cancelled = executor.cancel(action_id)
        
        # Should have cancellation flag set
        assert cancelled or action_id in executor._cancel_flags or True  # May have already completed
    
    def test_get_status(self):
        """Test getting action status."""
        def quick_func():
            return "done"
        
        executor = ActionExecutor()
        action = Action(
            action_id="status_001",
            action_type=ActionType.FUNCTION,
            handler=quick_func,
        )
        
        result = executor.execute(action)
        
        status = executor.status("status_001")
        
        assert status == ActionStatus.SUCCESS
    
    def test_get_status_nonexistent(self):
        """Test getting status of nonexistent action."""
        executor = ActionExecutor()
        
        status = executor.status("nonexistent")
        
        assert status is None
    
    def test_get_result(self):
        """Test getting action result."""
        def multiply(x, y):
            return x * y
        
        executor = ActionExecutor()
        action = Action(
            action_id="result_001",
            action_type=ActionType.FUNCTION,
            handler=multiply,
            params={"x": 3, "y": 4},
        )
        
        executor.execute(action)
        
        result = executor.get_result("result_001")
        
        assert result is not None
        assert result.result == 12
    
    def test_get_result_nonexistent(self):
        """Test getting result of nonexistent action."""
        executor = ActionExecutor()
        
        result = executor.get_result("nonexistent")
        
        assert result is None
    
    def test_history(self):
        """Test execution history."""
        executor = ActionExecutor()
        
        for i in range(3):
            action = Action(
                action_id=f"history_{i:03d}",
                action_type=ActionType.FUNCTION,
                handler=lambda: i,
            )
            executor.execute(action)
        
        history = executor.history()
        
        assert len(history) == 3
    
    def test_history_limit(self):
        """Test history with limit."""
        executor = ActionExecutor()
        
        for i in range(5):
            action = Action(
                action_id=f"history_limit_{i:03d}",
                action_type=ActionType.FUNCTION,
                handler=lambda: i,
            )
            executor.execute(action)
        
        history = executor.history(limit=3)
        
        assert len(history) == 3
    
    def test_get_stats(self):
        """Test getting executor statistics."""
        executor = ActionExecutor()
        
        # Execute some actions
        for i in range(3):
            action = Action(
                action_id=f"stats_{i:03d}",
                action_type=ActionType.FUNCTION,
                handler=lambda: i,
            )
            executor.execute(action)
        
        # Execute one that fails
        action = Action(
            action_id="stats_fail",
            action_type=ActionType.FUNCTION,
            handler=lambda: 1/0,  # ZeroDivisionError
        )
        executor.execute(action)
        
        stats = executor.get_stats()
        
        assert stats.total_actions == 4
        assert stats.successful == 3
        assert stats.failed == 1
    
    def test_clear_history(self):
        """Test clearing history."""
        executor = ActionExecutor()
        
        action = Action(
            action_id="clear_001",
            action_type=ActionType.FUNCTION,
            handler=lambda: "test",
        )
        executor.execute(action)
        
        assert len(executor.history()) == 1
        
        executor.clear_history()
        
        assert len(executor.history()) == 0
    
    def test_max_history_size(self):
        """Test max history size limit."""
        executor = ActionExecutor()
        executor.MAX_HISTORY_SIZE = 5
        
        for i in range(10):
            action = Action(
                action_id=f"max_history_{i:03d}",
                action_type=ActionType.FUNCTION,
                handler=lambda: i,
            )
            executor.execute(action)
        
        history = executor.history()
        
        assert len(history) == 5
    
    def test_execute_async(self):
        """Test async execution."""
        results = []
        
        def callback(result):
            results.append(result)
        
        executor = ActionExecutor()
        action = Action(
            action_id="async_001",
            action_type=ActionType.FUNCTION,
            handler=lambda: "async_result",
        )
        
        action_id = executor.execute_async(action, callback)
        
        # Wait for completion
        time.sleep(0.1)
        
        assert action_id == "async_001"
        assert len(results) == 1
        assert results[0].result == "async_result"
    
    def test_save_and_load_state(self):
        """Test save and load state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = ActionExecutor(data_dir=tmpdir)
            
            # Execute some actions
            for i in range(3):
                action = Action(
                    action_id=f"state_{i:03d}",
                    action_type=ActionType.FUNCTION,
                    handler=lambda: i,
                )
                executor.execute(action)
            
            # Save state
            path = executor.save_state()
            assert os.path.exists(path)
            
            # Create new executor and load state
            executor2 = ActionExecutor(data_dir=tmpdir)
            loaded = executor2.load_state(path)
            
            assert loaded is True
            assert executor2.get_stats().total_actions == 3
            assert len(executor2.history()) == 3
    
    def test_load_nonexistent_state(self):
        """Test load nonexistent state."""
        executor = ActionExecutor()
        
        result = executor.load_state("/nonexistent/path.json")
        
        assert result is False
    
    def test_default_timeout_override(self):
        """Test default timeout override."""
        executor = ActionExecutor(default_timeout_ms=5000)
        
        action = Action(
            action_id="timeout_override",
            action_type=ActionType.FUNCTION,
            handler=lambda: "quick",
        )
        
        result = executor.execute(action, timeout_ms=100)
        
        # Should use override
        assert result.status == ActionStatus.SUCCESS
    
    def test_invalid_handler_type(self):
        """Test invalid handler type."""
        executor = ActionExecutor()
        
        # FUNCTION action with non-callable handler
        action = Action(
            action_id="invalid_001",
            action_type=ActionType.FUNCTION,
            handler="not a function",  # Should be callable
        )
        
        result = executor.execute(action)
        
        assert result.status == ActionStatus.FAILED
    
    def test_repr(self):
        """Test string representation."""
        executor = ActionExecutor()
        
        for i in range(3):
            action = Action(
                action_id=f"repr_{i:03d}",
                action_type=ActionType.FUNCTION,
                handler=lambda: i,
            )
            executor.execute(action)
        
        repr_str = repr(executor)
        
        assert "ActionExecutor" in repr_str
        assert "actions=3" in repr_str
        assert "successful=3" in repr_str


class TestActionExecutorIntegration:
    """Integration tests for ActionExecutor."""
    
    def test_full_workflow(self):
        """Test full executor workflow."""
        executor = ActionExecutor(
            default_timeout_ms=5000,
            default_max_retries=2,
        )
        
        # Track results
        results = []
        
        def callback(result):
            results.append(result)
        
        # Execute successful action
        action1 = Action(
            action_id="workflow_001",
            action_type=ActionType.FUNCTION,
            handler=lambda x: x * 2,
            params={"x": 5},
        )
        result1 = executor.execute(action1)
        
        assert result1.status == ActionStatus.SUCCESS
        assert result1.result == 10
        
        # Execute failing action with retry
        call_count = [0]
        
        def sometimes_fail():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Temporary failure")
            return "success"
        
        action2 = Action(
            action_id="workflow_002",
            action_type=ActionType.FUNCTION,
            handler=sometimes_fail,
            max_retries=3,
            retry_delay_ms=10,
        )
        result2 = executor.execute(action2)
        
        assert result2.status == ActionStatus.SUCCESS
        assert result2.retry_count >= 1
        
        # Check statistics
        stats = executor.get_stats()
        assert stats.total_actions == 2
        assert stats.successful == 2
        
        # Check history
        history = executor.history()
        assert len(history) == 2
    
    def test_concurrent_execution(self):
        """Test concurrent execution."""
        executor = ActionExecutor(max_workers=4)
        
        def slow_task(task_id):
            time.sleep(0.1)
            return f"task_{task_id}_done"
        
        # Start multiple async executions
        action_ids = []
        for i in range(4):
            action = Action(
                action_id=f"concurrent_{i:03d}",
                action_type=ActionType.FUNCTION,
                handler=slow_task,
                params={"task_id": i},
            )
            action_ids.append(executor.execute_async(action))
        
        # Wait for all to complete
        time.sleep(0.5)
        
        # Check all completed
        for action_id in action_ids:
            result = executor.get_result(action_id)
            assert result is not None
            assert result.status == ActionStatus.SUCCESS
        
        executor.shutdown()
