"""
Tests for Parameter Applier
"""

import pytest
import tempfile
import os
from datetime import datetime

from claw_rl.learning.applier import (
    ParameterApplier,
    ApplyStatus,
    ApplyResult,
    ParameterSnapshot,
)


class TestParameterSnapshot:
    """Tests for ParameterSnapshot."""
    
    def test_snapshot_creation(self):
        """Test snapshot creation."""
        snapshot = ParameterSnapshot(
            snapshot_id="snap_001",
            timestamp="2026-04-05T12:00:00",
            parameters={"learning_rate": 0.1},
        )
        
        assert snapshot.snapshot_id == "snap_001"
        assert snapshot.timestamp == "2026-04-05T12:00:00"
        assert snapshot.parameters == {"learning_rate": 0.1}
    
    def test_snapshot_to_dict(self):
        """Test snapshot to dictionary."""
        snapshot = ParameterSnapshot(
            snapshot_id="snap_001",
            timestamp="2026-04-05T12:00:00",
            parameters={"learning_rate": 0.1},
            metadata={"reason": "test"},
        )
        
        result = snapshot.to_dict()
        
        assert result["snapshot_id"] == "snap_001"
        assert result["timestamp"] == "2026-04-05T12:00:00"
        assert result["parameters"] == {"learning_rate": 0.1}
        assert result["metadata"] == {"reason": "test"}


class TestApplyResult:
    """Tests for ApplyResult."""
    
    def test_result_creation_success(self):
        """Test successful result creation."""
        result = ApplyResult(
            timestamp="2026-04-05T12:00:00",
            status=ApplyStatus.SUCCESS,
            parameters_applied={"learning_rate": 0.2},
            previous_state={"learning_rate": 0.1},
        )
        
        assert result.status == ApplyStatus.SUCCESS
        assert result.parameters_applied == {"learning_rate": 0.2}
        assert result.error is None
    
    def test_result_creation_failed(self):
        """Test failed result creation."""
        result = ApplyResult(
            timestamp="2026-04-05T12:00:00",
            status=ApplyStatus.FAILED,
            parameters_applied={},
            previous_state={"learning_rate": 0.1},
            error="Validation failed",
        )
        
        assert result.status == ApplyStatus.FAILED
        assert result.error == "Validation failed"
    
    def test_result_to_dict(self):
        """Test result to dictionary."""
        result = ApplyResult(
            timestamp="2026-04-05T12:00:00",
            status=ApplyStatus.SUCCESS,
            parameters_applied={"learning_rate": 0.2},
            previous_state={"learning_rate": 0.1},
            rollback_available=True,
            metadata={"source": "optimizer"},
        )
        
        d = result.to_dict()
        
        assert d["status"] == "success"
        assert d["parameters_applied"] == {"learning_rate": 0.2}
        assert d["previous_state"] == {"learning_rate": 0.1}
        assert d["rollback_available"] is True
        assert d["metadata"] == {"source": "optimizer"}


class TestParameterApplier:
    """Tests for ParameterApplier."""
    
    def test_applier_creation(self):
        """Test applier creation."""
        applier = ParameterApplier()
        
        assert applier._parameters == {}
        assert applier._current_values == {}
        assert applier._apply_history == []
    
    def test_register_parameter(self):
        """Test parameter registration."""
        applier = ParameterApplier()
        
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        assert "learning_rate" in applier._parameters
        assert applier._parameters["learning_rate"]["default_value"] == 0.1
        assert applier._parameters["learning_rate"]["min_value"] == 0.01
        assert applier._parameters["learning_rate"]["max_value"] == 0.5
        assert applier._current_values["learning_rate"] == 0.1
    
    def test_register_multiple_parameters(self):
        """Test multiple parameter registration."""
        applier = ParameterApplier()
        
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        applier.register("exploration_rate", 0.2, min_value=0.0, max_value=1.0)
        applier.register("batch_size", 32, min_value=1, max_value=128)
        
        assert len(applier._parameters) == 3
        assert applier.get_current()["learning_rate"] == 0.1
        assert applier.get_current()["exploration_rate"] == 0.2
        assert applier.get_current()["batch_size"] == 32
    
    def test_validate_valid_parameters(self):
        """Test validation of valid parameters."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        is_valid, error = applier.validate({"learning_rate": 0.2})
        
        assert is_valid is True
        assert error is None
    
    def test_validate_unknown_parameter(self):
        """Test validation with unknown parameter."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        
        is_valid, error = applier.validate({"unknown_param": 0.1})
        
        assert is_valid is False
        assert "Unknown parameter" in error
    
    def test_validate_out_of_range(self):
        """Test validation with out of range value."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        is_valid, error = applier.validate({"learning_rate": 0.6})
        
        assert is_valid is False
        assert "above maximum" in error
        
        is_valid, error = applier.validate({"learning_rate": 0.005})
        
        assert is_valid is False
        assert "below minimum" in error
    
    def test_validate_type_int(self):
        """Test validation for int type."""
        applier = ParameterApplier()
        applier.register("batch_size", 32, min_value=1, max_value=128, value_type="int")
        
        # Valid int
        is_valid, error = applier.validate({"batch_size": 64})
        assert is_valid is True
        
        # Invalid string
        is_valid, error = applier.validate({"batch_size": "not_an_int"})
        assert is_valid is False
        assert "must be int" in error
    
    def test_validate_type_float(self):
        """Test validation for float type."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, value_type="float")
        
        is_valid, error = applier.validate({"learning_rate": 0.15})
        assert is_valid is True
    
    def test_validate_type_str(self):
        """Test validation for string type."""
        applier = ParameterApplier()
        applier.register("model_name", "default", value_type="str")
        
        is_valid, error = applier.validate({"model_name": "gpt-4"})
        assert is_valid is True
        
        is_valid, error = applier.validate({"model_name": 123})
        assert is_valid is False
        assert "must be str" in error
    
    def test_validate_type_bool(self):
        """Test validation for bool type."""
        applier = ParameterApplier()
        applier.register("enabled", True, value_type="bool")
        
        is_valid, error = applier.validate({"enabled": False})
        assert is_valid is True
        
        is_valid, error = applier.validate({"enabled": 1})
        assert is_valid is False
        assert "must be bool" in error
    
    def test_validate_custom_validator(self):
        """Test custom validator."""
        applier = ParameterApplier()
        applier.register(
            "odd_number",
            1,
            validator=lambda x: x % 2 == 1,
        )
        
        is_valid, error = applier.validate({"odd_number": 3})
        assert is_valid is True
        
        is_valid, error = applier.validate({"odd_number": 2})
        assert is_valid is False
        assert "failed custom validation" in error
    
    def test_apply_success(self):
        """Test successful parameter apply."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        result = applier.apply({"learning_rate": 0.2})
        
        assert result.status == ApplyStatus.SUCCESS
        assert result.parameters_applied == {"learning_rate": 0.2}
        assert result.previous_state == {"learning_rate": 0.1}
        assert applier.get_current()["learning_rate"] == 0.2
    
    def test_apply_multiple_parameters(self):
        """Test applying multiple parameters."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        applier.register("exploration_rate", 0.2, min_value=0.0, max_value=1.0)
        
        result = applier.apply({
            "learning_rate": 0.2,
            "exploration_rate": 0.3,
        })
        
        assert result.status == ApplyStatus.SUCCESS
        assert applier.get_current()["learning_rate"] == 0.2
        assert applier.get_current()["exploration_rate"] == 0.3
    
    def test_apply_invalid_parameter(self):
        """Test apply with invalid parameter."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        result = applier.apply({"learning_rate": 0.6})
        
        assert result.status == ApplyStatus.FAILED
        assert "above maximum" in result.error
        assert applier.get_current()["learning_rate"] == 0.1  # Unchanged
    
    def test_apply_unknown_parameter(self):
        """Test apply with unknown parameter."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        
        result = applier.apply({"unknown_param": 0.1})
        
        assert result.status == ApplyStatus.FAILED
        assert "Unknown parameter" in result.error
    
    def test_rollback_simple(self):
        """Test simple rollback."""
        applier = ParameterApplier(auto_snapshot=True)
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        # Apply change
        applier.apply({"learning_rate": 0.2})
        assert applier.get_current()["learning_rate"] == 0.2
        
        # Rollback
        result = applier.rollback()
        
        assert result.status == ApplyStatus.ROLLED_BACK
        assert applier.get_current()["learning_rate"] == 0.1
    
    def test_rollback_multiple_times(self):
        """Test rollback multiple times."""
        applier = ParameterApplier(auto_snapshot=True)
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=1.0)
        
        # Apply multiple changes
        applier.apply({"learning_rate": 0.2})  # Snapshot 1: 0.1
        applier.apply({"learning_rate": 0.3})  # Snapshot 2: 0.2
        applier.apply({"learning_rate": 0.4})  # Snapshot 3: 0.3
        
        assert applier.get_current()["learning_rate"] == 0.4
        
        # First rollback
        applier.rollback()
        assert applier.get_current()["learning_rate"] == 0.3
    
    def test_rollback_no_snapshots(self):
        """Test rollback when no snapshots available."""
        applier = ParameterApplier(auto_snapshot=False)
        applier.register("learning_rate", 0.1)
        
        result = applier.rollback()
        
        assert result.status == ApplyStatus.FAILED
        assert "No snapshots available" in result.error
    
    def test_get_current(self):
        """Test get current parameters."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        applier.register("exploration_rate", 0.2)
        
        current = applier.get_current()
        
        assert current == {"learning_rate": 0.1, "exploration_rate": 0.2}
    
    def test_get_parameter(self):
        """Test get single parameter."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        
        assert applier.get_parameter("learning_rate") == 0.1
        assert applier.get_parameter("unknown") is None
    
    def test_set_parameter(self):
        """Test set single parameter."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        result = applier.set_parameter("learning_rate", 0.2)
        
        assert result.status == ApplyStatus.SUCCESS
        assert applier.get_parameter("learning_rate") == 0.2
    
    def test_reset_single_parameter(self):
        """Test reset single parameter."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        applier.apply({"learning_rate": 0.3})
        assert applier.get_parameter("learning_rate") == 0.3
        
        result = applier.reset("learning_rate")
        
        assert result.status == ApplyStatus.SUCCESS
        assert applier.get_parameter("learning_rate") == 0.1
    
    def test_reset_all_parameters(self):
        """Test reset all parameters."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        applier.register("exploration_rate", 0.2)
        
        applier.apply({"learning_rate": 0.3, "exploration_rate": 0.4})
        
        result = applier.reset()
        
        assert result.status == ApplyStatus.SUCCESS
        assert applier.get_parameter("learning_rate") == 0.1
        assert applier.get_parameter("exploration_rate") == 0.2
    
    def test_reset_unknown_parameter(self):
        """Test reset unknown parameter."""
        applier = ParameterApplier()
        
        result = applier.reset("unknown")
        
        assert result.status == ApplyStatus.FAILED
        assert "Unknown parameter" in result.error
    
    def test_get_history(self):
        """Test get apply history."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        
        applier.apply({"learning_rate": 0.2})
        applier.apply({"learning_rate": 0.3})
        
        history = applier.get_history()
        
        assert len(history) == 2
        assert history[0].parameters_applied == {"learning_rate": 0.2}
        assert history[1].parameters_applied == {"learning_rate": 0.3}
    
    def test_get_history_limit(self):
        """Test get history with limit."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        
        for i in range(5):
            applier.apply({"learning_rate": 0.1 + i * 0.05})
        
        history = applier.get_history(limit=3)
        
        assert len(history) == 3
    
    def test_get_statistics(self):
        """Test get statistics."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
        
        applier.apply({"learning_rate": 0.2})  # success
        applier.apply({"learning_rate": 0.6})  # fail
        applier.apply({"learning_rate": 0.3})  # success
        
        stats = applier.get_statistics()
        
        assert stats["total_applies"] == 3
        assert stats["success_count"] == 2
        assert stats["failed_count"] == 1
        assert stats["success_rate"] == pytest.approx(2/3)
    
    def test_auto_snapshot_disabled(self):
        """Test with auto snapshot disabled."""
        applier = ParameterApplier(auto_snapshot=False)
        applier.register("learning_rate", 0.1)
        
        applier.apply({"learning_rate": 0.2})
        
        # No snapshot created
        assert len(applier.get_snapshots()) == 0
        
        # Rollback should fail
        result = applier.rollback()
        assert result.status == ApplyStatus.FAILED
    
    def test_get_snapshots(self):
        """Test get snapshots."""
        applier = ParameterApplier(auto_snapshot=True)
        applier.register("learning_rate", 0.1)
        
        applier.apply({"learning_rate": 0.2})
        applier.apply({"learning_rate": 0.3})
        
        snapshots = applier.get_snapshots()
        
        # Should have 2 snapshots
        assert len(snapshots) == 2
        assert snapshots[0].parameters == {"learning_rate": 0.1}
        assert snapshots[1].parameters == {"learning_rate": 0.2}
    
    def test_max_history_size(self):
        """Test history size limit."""
        applier = ParameterApplier()
        applier.MAX_HISTORY_SIZE = 5
        applier.register("learning_rate", 0.1)
        
        for i in range(10):
            applier.apply({"learning_rate": 0.1 + i * 0.01})
        
        history = applier.get_history()
        
        assert len(history) == 5
    
    def test_max_snapshots(self):
        """Test snapshots limit."""
        applier = ParameterApplier(auto_snapshot=True)
        applier.MAX_SNAPSHOTS = 3
        applier.register("learning_rate", 0.1)
        
        for i in range(5):
            applier.apply({"learning_rate": 0.1 + i * 0.01})
        
        snapshots = applier.get_snapshots()
        
        assert len(snapshots) == 3
    
    def test_save_and_load_state(self):
        """Test save and load state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            applier = ParameterApplier(data_dir=tmpdir)
            applier.register("learning_rate", 0.1, min_value=0.01, max_value=0.5)
            applier.apply({"learning_rate": 0.2})
            
            # Save
            path = applier.save_state()
            assert os.path.exists(path)
            
            # Create new applier and load
            new_applier = ParameterApplier(data_dir=tmpdir)
            loaded = new_applier.load_state(path)
            
            assert loaded is True
            assert new_applier.get_parameter("learning_rate") == 0.2
    
    def test_load_nonexistent_state(self):
        """Test load nonexistent state."""
        applier = ParameterApplier()
        
        result = applier.load_state("/nonexistent/path.json")
        
        assert result is False
    
    def test_repr(self):
        """Test string representation."""
        applier = ParameterApplier()
        applier.register("learning_rate", 0.1)
        applier.apply({"learning_rate": 0.2})
        
        repr_str = repr(applier)
        
        assert "ParameterApplier" in repr_str
        assert "parameters=1" in repr_str
        assert "applies=1" in repr_str
