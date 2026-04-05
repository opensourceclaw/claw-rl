"""
Tests for Configuration Manager
"""

import pytest
import tempfile
import os
import json
import time

from claw_rl.learning.config_manager import (
    ConfigManager,
    ConfigStatus,
    ConfigVersion,
    ConfigAuditEntry,
)


class TestConfigVersion:
    """Tests for ConfigVersion."""
    
    def test_version_creation(self):
        """Test version creation."""
        version = ConfigVersion(
            version="v1.0.0",
            timestamp="2026-04-05T12:00:00",
            config={"key": "value"},
            checksum="abc123",
        )
        
        assert version.version == "v1.0.0"
        assert version.timestamp == "2026-04-05T12:00:00"
        assert version.config == {"key": "value"}
        assert version.checksum == "abc123"
        assert version.status == ConfigStatus.VALID
    
    def test_version_to_dict(self):
        """Test version to dictionary."""
        version = ConfigVersion(
            version="v1.0.0",
            timestamp="2026-04-05T12:00:00",
            config={"key": "value"},
            checksum="abc123",
            author="test",
            message="Initial",
            metadata={"source": "test"},
        )
        
        d = version.to_dict()
        
        assert d["version"] == "v1.0.0"
        assert d["timestamp"] == "2026-04-05T12:00:00"
        assert d["config"] == {"key": "value"}
        assert d["checksum"] == "abc123"
        assert d["author"] == "test"
        assert d["message"] == "Initial"
        assert d["status"] == "valid"
        assert d["metadata"] == {"source": "test"}
    
    def test_version_from_dict(self):
        """Test version from dictionary."""
        d = {
            "version": "v1.0.0",
            "timestamp": "2026-04-05T12:00:00",
            "config": {"key": "value"},
            "checksum": "abc123",
            "author": "test",
            "message": "Initial",
            "status": "valid",
            "metadata": {"source": "test"},
        }
        
        version = ConfigVersion.from_dict(d)
        
        assert version.version == "v1.0.0"
        assert version.timestamp == "2026-04-05T12:00:00"
        assert version.config == {"key": "value"}
        assert version.checksum == "abc123"
        assert version.author == "test"
        assert version.message == "Initial"
        assert version.status == ConfigStatus.VALID


class TestConfigAuditEntry:
    """Tests for ConfigAuditEntry."""
    
    def test_entry_creation(self):
        """Test audit entry creation."""
        entry = ConfigAuditEntry(
            timestamp="2026-04-05T12:00:00",
            action="update",
            version="v1.0.0",
            details={"key": "learning_rate"},
        )
        
        assert entry.timestamp == "2026-04-05T12:00:00"
        assert entry.action == "update"
        assert entry.version == "v1.0.0"
        assert entry.details == {"key": "learning_rate"}
    
    def test_entry_to_dict(self):
        """Test entry to dictionary."""
        entry = ConfigAuditEntry(
            timestamp="2026-04-05T12:00:00",
            action="update",
            version="v1.0.0",
            details={"key": "learning_rate"},
        )
        
        d = entry.to_dict()
        
        assert d["timestamp"] == "2026-04-05T12:00:00"
        assert d["action"] == "update"
        assert d["version"] == "v1.0.0"
        assert d["details"] == {"key": "learning_rate"}


class TestConfigManager:
    """Tests for ConfigManager."""
    
    def test_manager_creation(self):
        """Test manager creation."""
        manager = ConfigManager()
        
        assert manager.config_path is None
        assert manager._config == {}
        assert manager._versions == []
    
    def test_load_or_create_new(self):
        """Test load or create with new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_path)
            
            result = manager.load_or_create(default_config={"key": "value"})
            
            assert result is True
            assert manager.get("key") == "value"
            assert os.path.exists(config_path)
    
    def test_load_or_create_existing(self):
        """Test load or create with existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            
            # Create file first
            with open(config_path, "w") as f:
                json.dump({"existing": "value"}, f)
            
            manager = ConfigManager(config_path)
            result = manager.load_or_create(default_config={"key": "value"})
            
            assert result is True
            assert manager.get("existing") == "value"
            assert manager.get("key") is None  # Default not used
    
    def test_save_and_load(self):
        """Test save and load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_path)
            
            manager._config = {"key": "value"}
            manager.save()
            
            # Create new manager and load
            manager2 = ConfigManager(config_path)
            manager2.load()
            
            assert manager2.get("key") == "value"
    
    def test_validate_valid_config(self):
        """Test validation of valid config."""
        manager = ConfigManager()
        
        is_valid, error = manager.validate({"key": "value"})
        
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_config(self):
        """Test validation with custom validator."""
        def validator(config):
            if "required_key" not in config:
                return False, "Missing required_key"
            return True, None
        
        manager = ConfigManager(validator=validator)
        
        is_valid, error = manager.validate({"key": "value"})
        assert is_valid is False
        assert "required_key" in error
        
        is_valid, error = manager.validate({"required_key": "value"})
        assert is_valid is True
    
    def test_validate_non_dict(self):
        """Test validation of non-dict."""
        manager = ConfigManager()
        
        is_valid, error = manager.validate("not a dict")
        
        assert is_valid is False
        assert "dictionary" in error
    
    def test_update(self):
        """Test configuration update."""
        manager = ConfigManager()
        manager._config = {"key1": "value1"}
        
        success, error = manager.update({"key2": "value2"}, message="Add key2")
        
        assert success is True
        assert manager.get("key1") == "value1"
        assert manager.get("key2") == "value2"
        assert len(manager._versions) == 1
    
    def test_update_with_validation(self):
        """Test update with validation."""
        def validator(config):
            if "learning_rate" in config and config["learning_rate"] > 1.0:
                return False, "learning_rate must be <= 1.0"
            return True, None
        
        manager = ConfigManager(validator=validator)
        manager._config = {}
        
        success, error = manager.update({"learning_rate": 0.5})
        assert success is True
        
        success, error = manager.update({"learning_rate": 1.5})
        assert success is False
        assert "learning_rate" in error
    
    def test_set_single_value(self):
        """Test setting single value."""
        manager = ConfigManager()
        manager._config = {}
        
        success, error = manager.set("key", "value", message="Set key")
        
        assert success is True
        assert manager.get("key") == "value"
    
    def test_get_with_default(self):
        """Test get with default."""
        manager = ConfigManager()
        
        assert manager.get("nonexistent") is None
        assert manager.get("nonexistent", "default") == "default"
    
    def test_get_all(self):
        """Test get all configuration."""
        manager = ConfigManager()
        manager._config = {"key1": "value1", "key2": "value2"}
        
        config = manager.get_all()
        
        assert config == {"key1": "value1", "key2": "value2"}
        
        # Ensure it's a copy
        config["key3"] = "value3"
        assert "key3" not in manager._config
    
    def test_delete(self):
        """Test delete key."""
        manager = ConfigManager()
        manager._config = {"key1": "value1", "key2": "value2"}
        
        result = manager.delete("key1", message="Delete key1")
        
        assert result is True
        assert "key1" not in manager._config
        assert manager.get("key2") == "value2"
    
    def test_delete_nonexistent(self):
        """Test delete nonexistent key."""
        manager = ConfigManager()
        manager._config = {"key": "value"}
        
        result = manager.delete("nonexistent")
        
        assert result is False
    
    def test_version(self):
        """Test version tracking."""
        manager = ConfigManager()
        manager._config = {}
        
        assert manager.version() is None
        
        manager.update({"key": "value"})
        
        assert manager.version() is not None
        assert manager.version().startswith("v")
    
    def test_history(self):
        """Test version history."""
        manager = ConfigManager()
        manager._config = {}
        
        manager.update({"key1": "value1"}, message="First")
        manager.update({"key2": "value2"}, message="Second")
        manager.update({"key3": "value3"}, message="Third")
        
        history = manager.history()
        
        assert len(history) == 3
        assert history[0].message == "First"
        assert history[1].message == "Second"
        assert history[2].message == "Third"
    
    def test_history_limit(self):
        """Test history with limit."""
        manager = ConfigManager()
        manager._config = {}
        
        for i in range(5):
            manager.update({f"key{i}": f"value{i}"})
        
        history = manager.history(limit=3)
        
        assert len(history) == 3
    
    def test_get_version(self):
        """Test get specific version."""
        manager = ConfigManager()
        manager._config = {}
        
        manager.update({"key1": "value1"}, message="First")
        version = manager.version()
        
        manager.update({"key2": "value2"}, message="Second")
        
        v = manager.get_version(version)
        
        assert v is not None
        assert v.config == {"key1": "value1"}
    
    def test_rollback(self):
        """Test rollback to previous version."""
        manager = ConfigManager()
        manager._config = {}
        
        manager.update({"key1": "value1"}, message="First")
        v1 = manager.version()
        
        manager.update({"key1": "value2"}, message="Second")
        assert manager.get("key1") == "value2"
        
        success, error = manager.rollback(v1)
        
        assert success is True
        assert manager.get("key1") == "value1"
    
    def test_rollback_nonexistent_version(self):
        """Test rollback to nonexistent version."""
        manager = ConfigManager()
        manager._config = {}
        
        success, error = manager.rollback("v_nonexistent")
        
        assert success is False
        assert "not found" in error
    
    def test_rollback_invalid_version(self):
        """Test rollback to invalid version."""
        def validator(config):
            if "invalid" in config:
                return False, "Config is invalid"
            return True, None
        
        manager = ConfigManager(validator=validator)
        manager._config = {"valid": "value"}
        manager._create_version("Valid version")
        
        # Create a version with invalid config directly
        bad_version = ConfigVersion(
            version="v_bad",
            timestamp="2026-04-05T12:00:00",
            config={"invalid": "value"},
            checksum="bad",
        )
        manager._versions.append(bad_version)
        
        success, error = manager.rollback("v_bad")
        
        assert success is False
        assert "invalid" in error
    
    def test_diff(self):
        """Test diff between versions."""
        manager = ConfigManager()
        manager._config = {}
        
        manager.update({"key1": "value1", "key2": "value2"}, message="First")
        v1 = manager.version()
        
        manager.update({"key1": "changed", "key3": "new"}, message="Second")
        v2 = manager.version()
        manager.delete("key2", message="Third")
        v3 = manager.version()
        
        diff = manager.diff(v1, v2)
        
        assert diff["changed"]["key1"]["from"] == "value1"
        assert diff["changed"]["key1"]["to"] == "changed"
        assert diff["added"]["key3"] == "new"
        
        diff2 = manager.diff(v2, v3)
        assert diff2["removed"]["key2"] == "value2"
    
    def test_diff_nonexistent_versions(self):
        """Test diff with nonexistent versions."""
        manager = ConfigManager()
        
        diff = manager.diff("v1", "v2")
        
        assert "error" in diff
    
    def test_check_reload_modified(self):
        """Test check reload when file modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_path)
            
            manager.load_or_create(default_config={"key": "value"})
            
            # Modify file externally
            time.sleep(0.01)  # Small delay for mtime
            with open(config_path, "w") as f:
                json.dump({"key": "modified"}, f)
            
            reloaded = manager.check_reload()
            
            assert reloaded is True
            assert manager.get("key") == "modified"
    
    def test_check_reload_not_modified(self):
        """Test check reload when file not modified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_path)
            
            manager.load_or_create(default_config={"key": "value"})
            
            reloaded = manager.check_reload()
            
            assert reloaded is False
    
    def test_change_callback(self):
        """Test change callback."""
        manager = ConfigManager()
        manager._config = {}
        
        changes = []
        
        def on_change(config):
            changes.append(config)
        
        manager.on_change(on_change)
        
        manager.update({"key": "value"})
        
        assert len(changes) == 1
        assert changes[0] == {"key": "value"}
    
    def test_off_change(self):
        """Test removing change callback."""
        manager = ConfigManager()
        manager._config = {}
        
        changes = []
        
        def on_change(config):
            changes.append(config)
        
        manager.on_change(on_change)
        manager.off_change(on_change)
        
        manager.update({"key": "value"})
        
        assert len(changes) == 0
    
    def test_auto_version_disabled(self):
        """Test with auto version disabled."""
        manager = ConfigManager(auto_version=False)
        manager._config = {}
        
        manager.update({"key": "value"})
        
        assert manager.version() is None
        assert len(manager._versions) == 0
    
    def test_get_audit_log(self):
        """Test get audit log."""
        manager = ConfigManager()
        manager._config = {}
        
        manager.update({"key": "value"})  # First update creates version
        manager.set("key", "value2")
        manager.delete("key")
        
        log = manager.get_audit_log()
        
        assert len(log) == 3
        assert log[0].action == "update"
        assert log[1].action == "update"
        assert log[2].action == "delete"
    
    def test_get_audit_log_limit(self):
        """Test get audit log with limit."""
        manager = ConfigManager()
        manager._config = {}
        
        for i in range(5):
            manager.set(f"key{i}", f"value{i}")
        
        log = manager.get_audit_log(limit=3)
        
        assert len(log) == 3
    
    def test_get_statistics(self):
        """Test get statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_path)
            
            manager.load_or_create(default_config={"key1": "value1"})
            manager.update({"key2": "value2"})
            
            stats = manager.get_statistics()
            
            assert stats["current_version"] is not None
            assert stats["total_versions"] == 2
            assert stats["config_keys"] == 2
            assert stats["has_file"] is True
    
    def test_max_versions(self):
        """Test max versions limit."""
        manager = ConfigManager()
        manager.MAX_VERSIONS = 5
        manager._config = {}
        
        for i in range(10):
            manager.set("key", f"value{i}")
        
        assert len(manager._versions) == 5
    
    def test_max_audit_entries(self):
        """Test max audit entries limit."""
        manager = ConfigManager()
        manager.MAX_AUDIT_ENTRIES = 5
        manager._config = {}
        
        for i in range(10):
            manager.set("key", f"value{i}")
        
        assert len(manager._audit_log) == 5
    
    def test_save_and_load_state(self):
        """Test save and load state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_path)
            
            manager.load_or_create(default_config={"key": "value"})
            manager.update({"key": "value2"})
            
            # Save state
            state_path = manager.save_state()
            assert os.path.exists(state_path)
            
            # Create new manager and load state
            manager2 = ConfigManager(config_path)
            manager2.load_state(state_path)
            
            assert manager2.version() == manager.version()
            assert len(manager2._versions) == len(manager._versions)
    
    def test_load_state_nonexistent(self):
        """Test load state from nonexistent file."""
        manager = ConfigManager()
        
        result = manager.load_state("/nonexistent/path.json")
        
        assert result is False
    
    def test_repr(self):
        """Test string representation."""
        manager = ConfigManager()
        manager._config = {"key": "value"}
        manager.update({"key": "value2"})
        
        repr_str = repr(manager)
        
        assert "ConfigManager" in repr_str
        assert "versions=1" in repr_str
        assert "keys=1" in repr_str


class TestConfigManagerIntegration:
    """Integration tests for ConfigManager."""
    
    def test_full_workflow(self):
        """Test full configuration workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            
            # Define validator
            def validator(config):
                if "learning_rate" in config:
                    lr = config["learning_rate"]
                    if not isinstance(lr, (int, float)) or lr <= 0 or lr > 1:
                        return False, "learning_rate must be in (0, 1]"
                return True, None
            
            manager = ConfigManager(config_path, validator=validator)
            
            # Create initial config
            manager.load_or_create(default_config={
                "learning_rate": 0.1,
                "exploration_rate": 0.2,
            })
            
            assert manager.get("learning_rate") == 0.1
            
            # Valid update
            success, _ = manager.update({"learning_rate": 0.15})
            assert success is True
            
            # Invalid update
            success, error = manager.update({"learning_rate": 1.5})
            assert success is False
            assert "learning_rate" in error
            
            # History
            history = manager.history()
            assert len(history) >= 1
            
            # Rollback
            v1 = history[0].version
            success, _ = manager.rollback(v1)
            assert success is True
            assert manager.get("learning_rate") == 0.1
            
            # Statistics
            stats = manager.get_statistics()
            assert stats["has_file"] is True
    
    def test_hot_reload_workflow(self):
        """Test hot reload workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            manager = ConfigManager(config_path)
            
            # Track changes
            changes = []
            manager.on_change(lambda c: changes.append(c))
            
            # Create config
            manager.load_or_create(default_config={"key": "value"})
            
            # Check no reload
            assert manager.check_reload() is False
            
            # External modification
            time.sleep(0.01)
            with open(config_path, "w") as f:
                json.dump({"key": "modified"}, f)
            
            # Check reload
            assert manager.check_reload() is True
            assert manager.get("key") == "modified"
            assert len(changes) == 1
