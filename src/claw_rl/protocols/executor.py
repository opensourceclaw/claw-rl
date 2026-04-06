"""
Executor Protocol - Abstract interface for executing decisions

This protocol defines the interface for executing decisions
in the learning loop.
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ExecutionStatus(Enum):
    """Status of execution."""
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PENDING = "pending"


@dataclass
class ExecutionResult:
    """
    Result of executing a decision.
    
    Attributes:
        decision_id: ID of the executed decision
        status: Execution status
        success: Whether execution succeeded
        result: Result data
        error: Error message if failed
        metrics: Execution metrics
        timestamp: When execution completed
        metadata: Additional metadata
    """
    decision_id: str
    status: ExecutionStatus
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None
    metrics: Dict[str, Any] = None
    timestamp: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if self.metrics is None:
            self.metrics = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision_id": self.decision_id,
            "status": self.status.value,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionResult':
        """Create from dictionary."""
        return cls(
            decision_id=data["decision_id"],
            status=ExecutionStatus(data["status"]),
            success=data["success"],
            result=data["result"],
            error=data.get("error"),
            metrics=data.get("metrics", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )


class ExecutorProtocol(Protocol):
    """
    Protocol for executing decisions in the learning loop.
    
    An Executor is responsible for:
    - Executing decisions safely
    - Handling errors and rollback
    - Tracking execution metrics
    - Providing execution results
    
    This is a Protocol (interface) - frameworks must provide their own
    implementation through adapters.
    
    Example:
        >>> class MyExecutor(ExecutorProtocol):
        ...     def execute(self, decision: Dict[str, Any]) -> ExecutionResult:
        ...         try:
        ...             # Apply parameter adjustment
        ...             params = decision["parameters"]
        ...             self.apply_params(params)
        ...             
        ...             return ExecutionResult(
        ...                 decision_id=decision["decision_id"],
        ...                 status=ExecutionStatus.SUCCESS,
        ...                 success=True,
        ...                 result={"applied": params},
        ...                 metrics={"time_ms": 10},
        ...             )
        ...         except Exception as e:
        ...             return ExecutionResult(
        ...                 decision_id=decision["decision_id"],
        ...                 status=ExecutionStatus.FAILED,
        ...                 success=False,
        ...                 result={},
        ...                 error=str(e),
        ...             )
    """
    
    def execute(self, decision: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a decision.
        
        Args:
            decision: Decision to execute (as dict)
            
        Returns:
            ExecutionResult containing outcome
            
        This method should:
        - Validate the decision
        - Execute the action
        - Handle errors gracefully
        - Return execution result
        """
        ...
    
    def rollback(self, decision_id: str) -> ExecutionResult:
        """
        Rollback a previously executed decision.
        
        Args:
            decision_id: ID of decision to rollback
            
        Returns:
            ExecutionResult of rollback
        """
        ...
    
    def get_status(self, decision_id: str) -> Optional[ExecutionStatus]:
        """
        Get execution status of a decision.
        
        Args:
            decision_id: Decision ID
            
        Returns:
            Execution status, or None if not found
        """
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get executor metrics.
        
        Returns:
            Dictionary of metrics:
            - total_executions: Total number of executions
            - success_rate: Success rate
            - avg_execution_time: Average execution time
            - rollback_count: Number of rollbacks
        """
        ...
    
    def reset(self) -> None:
        """
        Reset executor state.
        
        This method should clear any accumulated state
        and prepare for fresh executions.
        """
        ...
