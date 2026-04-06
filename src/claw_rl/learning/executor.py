"""
Action Executor - Safe execution environment with retry and timeout support

This module provides a safe environment for executing actions with:
- Timeout limits
- Retry with exponential backoff
- Execution status tracking
- Action history logging
"""

from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time
import threading
import concurrent.futures
import traceback
import json
import os


class ActionStatus(Enum):
    """Status of action execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ActionType(Enum):
    """Types of actions."""
    FUNCTION = "function"       # Python function call
    SHELL = "shell"             # Shell command
    HTTP = "http"               # HTTP request
    CUSTOM = "custom"           # Custom action type


@dataclass
class Action:
    """Definition of an action to execute."""
    action_id: str
    action_type: ActionType
    handler: Union[Callable, str, Dict[str, Any]]  # Function, command, or config
    name: Optional[str] = None
    description: Optional[str] = None
    timeout_ms: int = 30000          # Default 30 seconds
    max_retries: int = 0             # Default no retry
    retry_delay_ms: int = 1000       # Default 1 second
    retry_backoff: float = 2.0       # Exponential backoff multiplier
    params: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary (without handler for serialization)."""
        handler_repr = None
        if callable(self.handler):
            handler_repr = f"function:{self.handler.__name__}"
        elif isinstance(self.handler, str):
            handler_repr = f"shell:{self.handler}"
        else:
            handler_repr = str(self.handler)
        
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "handler": handler_repr,
            "name": self.name,
            "description": self.description,
            "timeout_ms": self.timeout_ms,
            "max_retries": self.max_retries,
            "retry_delay_ms": self.retry_delay_ms,
            "retry_backoff": self.retry_backoff,
            "params": self.params,
            "metadata": self.metadata,
        }


@dataclass
class ActionResult:
    """Result of action execution."""
    action_id: str
    status: ActionStatus
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[int] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    attempts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "result": self.result if not callable(self.result) else None,
            "error": self.error,
            "retry_count": self.retry_count,
            "attempts": self.attempts,
            "metadata": self.metadata,
        }


@dataclass
class ExecutorStats:
    """Statistics for the executor."""
    total_actions: int = 0
    successful: int = 0
    failed: int = 0
    timeout: int = 0
    cancelled: int = 0
    total_retries: int = 0
    avg_duration_ms: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_actions": self.total_actions,
            "successful": self.successful,
            "failed": self.failed,
            "timeout": self.timeout,
            "cancelled": self.cancelled,
            "total_retries": self.total_retries,
            "avg_duration_ms": self.avg_duration_ms,
        }


class ActionExecutor:
    """
    Safe action executor with timeout, retry, and status tracking.
    
    Features:
    - Timeout limits for all actions
    - Retry with exponential backoff
    - Execution status tracking
    - Action history logging
    - Thread-safe execution
    - Cancellation support
    
    Example:
        >>> executor = ActionExecutor()
        >>> 
        >>> # Define action
        >>> action = Action(
        ...     action_id="task_001",
        ...     action_type=ActionType.FUNCTION,
        ...     handler=my_function,
        ...     params={"arg": "value"},
        ...     timeout_ms=5000,
        ...     max_retries=2,
        ... )
        >>> 
        >>> # Execute
        >>> result = executor.execute(action)
        >>> 
        >>> if result.status == ActionStatus.SUCCESS:
        ...     print(f"Result: {result.result}")
    """
    
    MAX_HISTORY_SIZE = 100  # Maximum action history to keep
    
    def __init__(
        self,
        default_timeout_ms: int = 30000,
        default_max_retries: int = 0,
        default_retry_delay_ms: int = 1000,
        max_workers: int = 4,
        data_dir: Optional[str] = None,
    ):
        """
        Initialize ActionExecutor.
        
        Args:
            default_timeout_ms: Default timeout in milliseconds
            default_max_retries: Default max retries
            default_retry_delay_ms: Default retry delay in milliseconds
            max_workers: Maximum concurrent workers
            data_dir: Directory for storing executor data
        """
        self.default_timeout_ms = default_timeout_ms
        self.default_max_retries = default_max_retries
        self.default_retry_delay_ms = default_retry_delay_ms
        self.max_workers = max_workers
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data")
        
        # Execution tracking
        self._history: List[ActionResult] = []
        self._running: Dict[str, ActionResult] = {}
        self._stats = ExecutorStats()
        
        # Thread pool for concurrent execution
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
        # Cancellation flags
        self._cancel_flags: Dict[str, bool] = {}
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def execute(
        self,
        action: Action,
        timeout_ms: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> ActionResult:
        """
        Execute an action.
        
        Args:
            action: Action to execute
            timeout_ms: Override timeout (uses action timeout if None)
            max_retries: Override max retries (uses action max_retries if None)
        
        Returns:
            ActionResult with execution status and result
        """
        timeout = timeout_ms or action.timeout_ms or self.default_timeout_ms
        retries = max_retries if max_retries is not None else action.max_retries
        retries = retries if retries >= 0 else self.default_max_retries
        
        result = ActionResult(
            action_id=action.action_id,
            status=ActionStatus.PENDING,
            start_time=datetime.now().isoformat(),
            metadata=action.metadata.copy(),
        )
        
        # Initialize cancellation flag
        self._cancel_flags[action.action_id] = False
        
        attempt_count = 0
        last_error = None
        
        while attempt_count <= retries:
            # Check for cancellation
            if self._cancel_flags.get(action.action_id, False):
                result.status = ActionStatus.CANCELLED
                result.end_time = datetime.now().isoformat()
                result.duration_ms = self._calculate_duration_ms(result.start_time, result.end_time)
                self._record_attempt(result, attempt_count, ActionStatus.CANCELLED, None, "Cancelled by user")
                break
            
            # Execute with timeout
            attempt_count += 1
            result.retry_count = attempt_count - 1
            
            if attempt_count > 1:
                result.status = ActionStatus.RETRYING
            
            # Run in thread pool with timeout
            status, output, error = self._execute_with_timeout(
                action, timeout, result
            )
            
            # Record attempt
            self._record_attempt(result, attempt_count, status, output, error)
            
            if status == ActionStatus.SUCCESS:
                result.status = ActionStatus.SUCCESS
                result.result = output
                result.end_time = datetime.now().isoformat()
                result.duration_ms = self._calculate_duration_ms(result.start_time, result.end_time)
                last_error = None
                break
            elif status == ActionStatus.CANCELLED:
                result.status = ActionStatus.CANCELLED
                result.end_time = datetime.now().isoformat()
                result.duration_ms = self._calculate_duration_ms(result.start_time, result.end_time)
                break
            else:
                last_error = error
                
                # Check if we should retry
                if attempt_count <= retries:
                    # Calculate delay with exponential backoff
                    delay_ms = action.retry_delay_ms * (action.retry_backoff ** (attempt_count - 1))
                    time.sleep(delay_ms / 1000.0)
                    self._stats.total_retries += 1
                else:
                    # No more retries
                    result.status = status
                    result.error = last_error
                    result.end_time = datetime.now().isoformat()
                    result.duration_ms = self._calculate_duration_ms(result.start_time, result.end_time)
        
        # Clean up cancellation flag
        self._cancel_flags.pop(action.action_id, None)
        
        # Update statistics
        self._update_stats(result)
        
        # Record in history
        self._add_to_history(result)
        
        return result
    
    def execute_async(
        self,
        action: Action,
        callback: Optional[Callable[[ActionResult], None]] = None,
    ) -> str:
        """
        Execute an action asynchronously.
        
        Args:
            action: Action to execute
            callback: Optional callback when execution completes
        
        Returns:
            Action ID for tracking
        """
        def run_and_callback():
            result = self.execute(action)
            if callback:
                try:
                    callback(result)
                except Exception:
                    pass
        
        future = self._executor.submit(run_and_callback)
        
        return action.action_id
    
    def _execute_with_timeout(
        self,
        action: Action,
        timeout_ms: int,
        result: ActionResult,
    ) -> tuple:
        """
        Execute action with timeout.
        
        Returns:
            Tuple of (status, result, error)
        """
        with self._lock:
            result.status = ActionStatus.RUNNING
            self._running[action.action_id] = result
        
        try:
            # Use thread pool for timeout
            future = self._executor.submit(self._run_handler, action)
            
            try:
                output = future.result(timeout=timeout_ms / 1000.0)
                with self._lock:
                    self._running.pop(action.action_id, None)
                return ActionStatus.SUCCESS, output, None
            except concurrent.futures.TimeoutError:
                future.cancel()
                with self._lock:
                    self._running.pop(action.action_id, None)
                return ActionStatus.TIMEOUT, None, f"Timeout after {timeout_ms}ms"
            except Exception as e:
                with self._lock:
                    self._running.pop(action.action_id, None)
                return ActionStatus.FAILED, None, str(e)
        except Exception as e:
            with self._lock:
                self._running.pop(action.action_id, None)
            return ActionStatus.FAILED, None, str(e)
    
    def _run_handler(self, action: Action) -> Any:
        """Run the action handler."""
        if action.action_type == ActionType.FUNCTION:
            if callable(action.handler):
                return action.handler(**action.params)
            else:
                raise ValueError(f"Handler for FUNCTION action must be callable")
        
        elif action.action_type == ActionType.SHELL:
            # Shell command execution
            import subprocess
            if isinstance(action.handler, str):
                result = subprocess.run(
                    action.handler,
                    shell=True,
                    capture_output=True,
                    text=True,
                    **action.params.get("subprocess_kwargs", {}),
                )
                if result.returncode != 0:
                    raise Exception(f"Shell command failed: {result.stderr}")
                return result.stdout
            else:
                raise ValueError(f"Handler for SHELL action must be string command")
        
        elif action.action_type == ActionType.CUSTOM:
            # Custom action - just pass through
            return {"handler": str(action.handler), "params": action.params}
        
        else:
            raise ValueError(f"Unknown action type: {action.action_type}")
    
    def _record_attempt(
        self,
        result: ActionResult,
        attempt: int,
        status: ActionStatus,
        output: Any,
        error: Optional[str],
    ) -> None:
        """Record an execution attempt."""
        attempt_record = {
            "attempt": attempt,
            "status": status.value,
            "timestamp": datetime.now().isoformat(),
            "output": str(output)[:500] if output else None,  # Truncate for history
            "error": error,
        }
        result.attempts.append(attempt_record)
    
    def _calculate_duration_ms(self, start: str, end: str) -> int:
        """Calculate duration in milliseconds."""
        try:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            return int((end_dt - start_dt).total_seconds() * 1000)
        except Exception:
            return 0
    
    def _update_stats(self, result: ActionResult) -> None:
        """Update executor statistics."""
        with self._lock:
            self._stats.total_actions += 1
            
            if result.status == ActionStatus.SUCCESS:
                self._stats.successful += 1
            elif result.status == ActionStatus.FAILED:
                self._stats.failed += 1
            elif result.status == ActionStatus.TIMEOUT:
                self._stats.timeout += 1
            elif result.status == ActionStatus.CANCELLED:
                self._stats.cancelled += 1
            
            # Update average duration
            if result.duration_ms:
                total = self._stats.total_actions
                current_avg = self._stats.avg_duration_ms
                self._stats.avg_duration_ms = (
                    (current_avg * (total - 1) + result.duration_ms) / total
                )
    
    def _add_to_history(self, result: ActionResult) -> None:
        """Add result to history."""
        with self._lock:
            self._history.append(result)
            if len(self._history) > self.MAX_HISTORY_SIZE:
                self._history = self._history[-self.MAX_HISTORY_SIZE:]
    
    def cancel(self, action_id: str) -> bool:
        """
        Cancel a running action.
        
        Args:
            action_id: ID of action to cancel
        
        Returns:
            True if cancellation was requested
        """
        with self._lock:
            if action_id in self._running:
                self._cancel_flags[action_id] = True
                return True
        return False
    
    def status(self, action_id: str) -> Optional[ActionStatus]:
        """
        Get status of an action.
        
        Args:
            action_id: Action ID
        
        Returns:
            Current status or None if not found
        """
        # Check running
        with self._lock:
            if action_id in self._running:
                return self._running[action_id].status
        
        # Check history
        for result in reversed(self._history):
            if result.action_id == action_id:
                return result.status
        
        return None
    
    def get_result(self, action_id: str) -> Optional[ActionResult]:
        """
        Get result of an action.
        
        Args:
            action_id: Action ID
        
        Returns:
            ActionResult or None if not found
        """
        # Check history
        for result in reversed(self._history):
            if result.action_id == action_id:
                return result
        
        return None
    
    def history(self, limit: Optional[int] = None) -> List[ActionResult]:
        """
        Get execution history.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of ActionResults
        """
        with self._lock:
            if limit:
                return self._history[-limit:]
            return self._history.copy()
    
    def get_stats(self) -> ExecutorStats:
        """
        Get executor statistics.
        
        Returns:
            ExecutorStats object
        """
        with self._lock:
            return ExecutorStats(
                total_actions=self._stats.total_actions,
                successful=self._stats.successful,
                failed=self._stats.failed,
                timeout=self._stats.timeout,
                cancelled=self._stats.cancelled,
                total_retries=self._stats.total_retries,
                avg_duration_ms=self._stats.avg_duration_ms,
            )
    
    def clear_history(self) -> None:
        """Clear execution history."""
        with self._lock:
            self._history.clear()
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the executor.
        
        Args:
            wait: Wait for running actions to complete
        """
        self._executor.shutdown(wait=wait)
    
    def save_state(self, path: Optional[str] = None) -> str:
        """
        Save executor state to file.
        
        Args:
            path: Optional path to save to
        
        Returns:
            Path where state was saved
        """
        if path is None:
            path = os.path.join(self.data_dir, "executor_state.json")
        
        state = {
            "stats": self._stats.to_dict(),
            "history": [r.to_dict() for r in self._history[-50:]],  # Last 50
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        return path
    
    def load_state(self, path: Optional[str] = None) -> bool:
        """
        Load executor state from file.
        
        Args:
            path: Optional path to load from
        
        Returns:
            True if loaded successfully
        """
        if path is None:
            path = os.path.join(self.data_dir, "executor_state.json")
        
        if not os.path.exists(path):
            return False
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            # Restore stats
            stats_data = state.get("stats", {})
            self._stats = ExecutorStats(
                total_actions=stats_data.get("total_actions", 0),
                successful=stats_data.get("successful", 0),
                failed=stats_data.get("failed", 0),
                timeout=stats_data.get("timeout", 0),
                cancelled=stats_data.get("cancelled", 0),
                total_retries=stats_data.get("total_retries", 0),
                avg_duration_ms=stats_data.get("avg_duration_ms", 0.0),
            )
            
            # Restore history
            self._history = [
                ActionResult(
                    action_id=r["action_id"],
                    status=ActionStatus(r["status"]),
                    start_time=r["start_time"],
                    end_time=r.get("end_time"),
                    duration_ms=r.get("duration_ms"),
                    result=r.get("result"),
                    error=r.get("error"),
                    retry_count=r.get("retry_count", 0),
                    attempts=r.get("attempts", []),
                    metadata=r.get("metadata", {}),
                )
                for r in state.get("history", [])
            ]
            
            return True
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    def __repr__(self) -> str:
        return (
            f"ActionExecutor(actions={self._stats.total_actions}, "
            f"successful={self._stats.successful}, "
            f"failed={self._stats.failed})"
        )
