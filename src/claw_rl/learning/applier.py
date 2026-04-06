"""
Parameter Applier - Apply optimized parameters to running system

This module applies optimized parameters from StrategyOptimizer to the system,
with validation, rollback support, and execution logging.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import copy


class ApplyStatus(Enum):
    """Status of parameter application."""
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PENDING = "pending"


@dataclass
class ApplyResult:
    """Result of a parameter apply operation."""
    timestamp: str
    status: ApplyStatus
    parameters_applied: Dict[str, Any]
    previous_state: Dict[str, Any]
    error: Optional[str] = None
    rollback_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "status": self.status.value,
            "parameters_applied": self.parameters_applied,
            "previous_state": self.previous_state,
            "error": self.error,
            "rollback_available": self.rollback_available,
            "metadata": self.metadata,
        }


@dataclass
class ParameterSnapshot:
    """Snapshot of parameter state for rollback."""
    snapshot_id: str
    timestamp: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


class ParameterApplier:
    """
    Applies optimized parameters to the running system.
    
    Features:
    - Parameter validation before apply
    - Atomic apply (all or nothing)
    - Automatic rollback on failure
    - Execution history logging
    - Snapshot management for manual rollback
    
    Example:
        >>> applier = ParameterApplier()
        >>> 
        >>> # Register parameters
        >>> applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        >>> applier.register("exploration_rate", 0.2, min_value=0.0, max_value=0.5)
        >>> 
        >>> # Apply new parameters
        >>> result = applier.apply({
        ...     "learning_rate": 0.15,
        ...     "exploration_rate": 0.25,
        ... })
        >>> 
        >>> if result.status == ApplyStatus.SUCCESS:
        ...     print("Parameters applied successfully")
        ... 
        >>> # Rollback if needed
        >>> applier.rollback()
    """
    
    MAX_HISTORY_SIZE = 100  # Maximum apply history to keep
    MAX_SNAPSHOTS = 10      # Maximum snapshots to keep
    
    def __init__(
        self,
        data_dir: Optional[str] = None,
        auto_snapshot: bool = True,
    ):
        """
        Initialize ParameterApplier.
        
        Args:
            data_dir: Directory for storing applier data
            auto_snapshot: Automatically create snapshot before apply
        """
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data")
        self.auto_snapshot = auto_snapshot
        
        # Registered parameters
        self._parameters: Dict[str, Dict[str, Any]] = {}
        
        # Current values
        self._current_values: Dict[str, Any] = {}
        
        # Apply history
        self._apply_history: List[ApplyResult] = []
        
        # Snapshots for rollback
        self._snapshots: List[ParameterSnapshot] = []
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def register(
        self,
        name: str,
        default_value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        value_type: Optional[str] = None,
        validator: Optional[callable] = None,
    ) -> None:
        """
        Register a parameter.
        
        Args:
            name: Parameter name
            default_value: Default value
            min_value: Minimum value (for numeric types)
            max_value: Maximum value (for numeric types)
            value_type: Expected type (int, float, str, bool)
            validator: Custom validator function
        """
        self._parameters[name] = {
            "default_value": default_value,
            "min_value": min_value,
            "max_value": max_value,
            "value_type": value_type or type(default_value).__name__,
            "validator": validator,
        }
        self._current_values[name] = default_value
    
    def validate(self, parameters: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate parameters before apply.
        
        Args:
            parameters: Parameters to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        for name, value in parameters.items():
            # Check if parameter is registered
            if name not in self._parameters:
                return False, f"Unknown parameter: {name}"
            
            param_config = self._parameters[name]
            
            # Type validation
            expected_type = param_config["value_type"]
            if expected_type == "int":
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    return False, f"Parameter {name} must be int, got {type(value).__name__}"
                if isinstance(value, float) and not value.is_integer():
                    return False, f"Parameter {name} must be int, got float {value}"
            elif expected_type == "float":
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    return False, f"Parameter {name} must be float, got {type(value).__name__}"
            elif expected_type == "str":
                if not isinstance(value, str):
                    return False, f"Parameter {name} must be str, got {type(value).__name__}"
            elif expected_type == "bool":
                if not isinstance(value, bool):
                    return False, f"Parameter {name} must be bool, got {type(value).__name__}"
            
            # Range validation (for numeric types)
            if expected_type in ("int", "float"):
                if param_config["min_value"] is not None and value < param_config["min_value"]:
                    return False, f"Parameter {name} value {value} below minimum {param_config['min_value']}"
                if param_config["max_value"] is not None and value > param_config["max_value"]:
                    return False, f"Parameter {name} value {value} above maximum {param_config['max_value']}"
            
            # Custom validator
            if param_config["validator"] is not None:
                try:
                    is_valid = param_config["validator"](value)
                    if not is_valid:
                        return False, f"Parameter {name} failed custom validation"
                except Exception as e:
                    return False, f"Parameter {name} validation error: {str(e)}"
        
        return True, None
    
    def apply(
        self,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApplyResult:
        """
        Apply new parameter values.
        
        Args:
            parameters: Parameters to apply
            metadata: Optional metadata for this apply operation
        
        Returns:
            ApplyResult with status and details
        """
        timestamp = datetime.now().isoformat()
        
        # Store previous state for rollback
        previous_state = copy.deepcopy(self._current_values)
        
        # Create snapshot if auto-snapshot enabled
        if self.auto_snapshot:
            self._create_snapshot(previous_state, metadata)
        
        # Validate parameters
        is_valid, error = self.validate(parameters)
        if not is_valid:
            result = ApplyResult(
                timestamp=timestamp,
                status=ApplyStatus.FAILED,
                parameters_applied={},
                previous_state=previous_state,
                error=error,
                rollback_available=True,
                metadata=metadata or {},
            )
            self._apply_history.append(result)
            self._trim_history()
            return result
        
        # Apply parameters atomically
        try:
            for name, value in parameters.items():
                self._current_values[name] = value
            
            result = ApplyResult(
                timestamp=timestamp,
                status=ApplyStatus.SUCCESS,
                parameters_applied=copy.deepcopy(parameters),
                previous_state=previous_state,
                rollback_available=True,
                metadata=metadata or {},
            )
        except Exception as e:
            # Rollback on any error
            self._current_values = copy.deepcopy(previous_state)
            result = ApplyResult(
                timestamp=timestamp,
                status=ApplyStatus.FAILED,
                parameters_applied={},
                previous_state=previous_state,
                error=str(e),
                rollback_available=True,
                metadata=metadata or {},
            )
        
        self._apply_history.append(result)
        self._trim_history()
        return result
    
    def rollback(self, snapshot_id: Optional[str] = None) -> ApplyResult:
        """
        Rollback to previous state.
        
        Args:
            snapshot_id: Optional specific snapshot to rollback to
        
        Returns:
            ApplyResult with rollback status
        """
        timestamp = datetime.now().isoformat()
        current_state = copy.deepcopy(self._current_values)
        
        # Find snapshot to rollback to
        if snapshot_id:
            snapshot = next(
                (s for s in self._snapshots if s.snapshot_id == snapshot_id),
                None
            )
            if snapshot is None:
                return ApplyResult(
                    timestamp=timestamp,
                    status=ApplyStatus.FAILED,
                    parameters_applied={},
                    previous_state=current_state,
                    error=f"Snapshot not found: {snapshot_id}",
                    rollback_available=False,
                    metadata={},
                )
        else:
            # Use most recent snapshot
            if not self._snapshots:
                return ApplyResult(
                    timestamp=timestamp,
                    status=ApplyStatus.FAILED,
                    parameters_applied={},
                    previous_state=current_state,
                    error="No snapshots available for rollback",
                    rollback_available=False,
                    metadata={},
                )
            snapshot = self._snapshots[-1]
        
        # Apply rollback
        try:
            self._current_values = copy.deepcopy(snapshot.parameters)
            result = ApplyResult(
                timestamp=timestamp,
                status=ApplyStatus.ROLLED_BACK,
                parameters_applied=copy.deepcopy(snapshot.parameters),
                previous_state=current_state,
                rollback_available=len(self._snapshots) > 1,
                metadata={
                    "snapshot_id": snapshot.snapshot_id,
                    "snapshot_timestamp": snapshot.timestamp,
                },
            )
        except Exception as e:
            result = ApplyResult(
                timestamp=timestamp,
                status=ApplyStatus.FAILED,
                parameters_applied={},
                previous_state=current_state,
                error=f"Rollback failed: {str(e)}",
                rollback_available=True,
                metadata={},
            )
        
        self._apply_history.append(result)
        self._trim_history()
        return result
    
    def get_current(self) -> Dict[str, Any]:
        """
        Get current parameter values.
        
        Returns:
            Dictionary of current parameter values
        """
        return copy.deepcopy(self._current_values)
    
    def get_parameter(self, name: str) -> Optional[Any]:
        """
        Get current value of a specific parameter.
        
        Args:
            name: Parameter name
        
        Returns:
            Current value or None if not found
        """
        return self._current_values.get(name)
    
    def set_parameter(self, name: str, value: Any) -> ApplyResult:
        """
        Set a single parameter value.
        
        Args:
            name: Parameter name
            value: New value
        
        Returns:
            ApplyResult with status
        """
        return self.apply({name: value})
    
    def reset(self, name: Optional[str] = None) -> ApplyResult:
        """
        Reset parameters to default values.
        
        Args:
            name: Optional specific parameter to reset (all if None)
        
        Returns:
            ApplyResult with status
        """
        if name:
            if name not in self._parameters:
                return ApplyResult(
                    timestamp=datetime.now().isoformat(),
                    status=ApplyStatus.FAILED,
                    parameters_applied={},
                    previous_state=copy.deepcopy(self._current_values),
                    error=f"Unknown parameter: {name}",
                    rollback_available=True,
                    metadata={},
                )
            return self.apply({name: self._parameters[name]["default_value"]})
        else:
            # Reset all parameters
            defaults = {
                name: config["default_value"]
                for name, config in self._parameters.items()
            }
            return self.apply(defaults)
    
    def _create_snapshot(
        self,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ParameterSnapshot:
        """Create a parameter snapshot."""
        snapshot = ParameterSnapshot(
            snapshot_id=f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now().isoformat(),
            parameters=copy.deepcopy(parameters),
            metadata=metadata or {},
        )
        
        self._snapshots.append(snapshot)
        
        # Trim snapshots
        if len(self._snapshots) > self.MAX_SNAPSHOTS:
            self._snapshots.pop(0)
        
        return snapshot
    
    def get_snapshots(self) -> List[ParameterSnapshot]:
        """
        Get all snapshots.
        
        Returns:
            List of snapshots
        """
        return self._snapshots.copy()
    
    def get_history(
        self,
        limit: Optional[int] = None,
    ) -> List[ApplyResult]:
        """
        Get apply history.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of apply results
        """
        if limit:
            return self._apply_history[-limit:]
        return self._apply_history.copy()
    
    def _trim_history(self) -> None:
        """Trim history to maximum size."""
        if len(self._apply_history) > self.MAX_HISTORY_SIZE:
            self._apply_history = self._apply_history[-self.MAX_HISTORY_SIZE:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get applier statistics.
        
        Returns:
            Dictionary with statistics
        """
        success_count = sum(1 for r in self._apply_history if r.status == ApplyStatus.SUCCESS)
        failed_count = sum(1 for r in self._apply_history if r.status == ApplyStatus.FAILED)
        rollback_count = sum(1 for r in self._apply_history if r.status == ApplyStatus.ROLLED_BACK)
        
        return {
            "total_applies": len(self._apply_history),
            "success_count": success_count,
            "failed_count": failed_count,
            "rollback_count": rollback_count,
            "success_rate": success_count / len(self._apply_history) if self._apply_history else 0,
            "snapshots_available": len(self._snapshots),
            "parameters_registered": len(self._parameters),
        }
    
    def save_state(self, path: Optional[str] = None) -> str:
        """
        Save applier state to file.
        
        Args:
            path: Optional path to save to
        
        Returns:
            Path where state was saved
        """
        if path is None:
            path = os.path.join(self.data_dir, "applier_state.json")
        
        state = {
            "parameters": self._parameters,
            "current_values": self._current_values,
            "apply_history": [r.to_dict() for r in self._apply_history[-50:]],  # Last 50
            "snapshots": [s.to_dict() for s in self._snapshots],
        }
        
        # Remove non-serializable validator functions
        for param in state["parameters"].values():
            param.pop("validator", None)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        return path
    
    def load_state(self, path: Optional[str] = None) -> bool:
        """
        Load applier state from file.
        
        Args:
            path: Optional path to load from
        
        Returns:
            True if loaded successfully
        """
        if path is None:
            path = os.path.join(self.data_dir, "applier_state.json")
        
        if not os.path.exists(path):
            return False
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            # Restore parameters (without validators)
            for name, param_data in state.get("parameters", {}).items():
                self._parameters[name] = param_data
            
            # Restore current values
            self._current_values = state.get("current_values", {})
            
            # Restore history
            self._apply_history = [
                ApplyResult(
                    timestamp=r["timestamp"],
                    status=ApplyStatus(r["status"]),
                    parameters_applied=r["parameters_applied"],
                    previous_state=r["previous_state"],
                    error=r.get("error"),
                    rollback_available=r.get("rollback_available", True),
                    metadata=r.get("metadata", {}),
                )
                for r in state.get("apply_history", [])
            ]
            
            # Restore snapshots
            self._snapshots = [
                ParameterSnapshot(
                    snapshot_id=s["snapshot_id"],
                    timestamp=s["timestamp"],
                    parameters=s["parameters"],
                    metadata=s.get("metadata", {}),
                )
                for s in state.get("snapshots", [])
            ]
            
            return True
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return False
    
    def __repr__(self) -> str:
        return (
            f"ParameterApplier(parameters={len(self._parameters)}, "
            f"applies={len(self._apply_history)}, "
            f"snapshots={len(self._snapshots)})"
        )
