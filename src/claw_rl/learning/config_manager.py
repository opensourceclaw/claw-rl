"""
Configuration Manager - Version-controlled configuration with hot-reload support

This module manages configuration files with versioning, validation,
hot-reload, and audit logging capabilities.
"""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import copy
import hashlib


class ConfigStatus(Enum):
    """Status of configuration."""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    ROLLED_BACK = "rolled_back"


@dataclass
class ConfigVersion:
    """A version of configuration."""
    version: str
    timestamp: str
    config: Dict[str, Any]
    checksum: str
    author: Optional[str] = None
    message: Optional[str] = None
    status: ConfigStatus = ConfigStatus.VALID
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "config": self.config,
            "checksum": self.checksum,
            "author": self.author,
            "message": self.message,
            "status": self.status.value,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConfigVersion":
        """Create from dictionary."""
        return cls(
            version=data["version"],
            timestamp=data["timestamp"],
            config=data["config"],
            checksum=data["checksum"],
            author=data.get("author"),
            message=data.get("message"),
            status=ConfigStatus(data.get("status", "valid")),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ConfigAuditEntry:
    """An audit log entry for configuration changes."""
    timestamp: str
    action: str
    version: Optional[str]
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "version": self.version,
            "details": self.details,
        }


class ConfigManager:
    """
    Version-controlled configuration manager.
    
    Features:
    - Version control for all configuration changes
    - Configuration validation
    - Hot-reload support with change detection
    - Rollback to any version
    - Audit logging for all operations
    - Atomic writes with checksum verification
    
    Example:
        >>> manager = ConfigManager()
        >>> 
        >>> # Load or create configuration
        >>> manager.load_or_create("config.json", {
        ...     "learning_rate": 0.1,
        ...     "exploration_rate": 0.2,
        ... })
        >>> 
        >>> # Update configuration
        >>> manager.update({"learning_rate": 0.15}, message="Increase learning rate")
        >>> 
        >>> # Get version history
        >>> history = manager.history()
        >>> 
        >>> # Rollback if needed
        >>> manager.rollback("v1.0.0")
    """
    
    MAX_VERSIONS = 50  # Maximum versions to keep
    MAX_AUDIT_ENTRIES = 200  # Maximum audit entries to keep
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        validator: Optional[Callable[[Dict[str, Any]], tuple]] = None,
        auto_version: bool = True,
    ):
        """
        Initialize ConfigManager.
        
        Args:
            config_path: Path to configuration file
            validator: Optional validation function (returns (is_valid, error_message))
            auto_version: Automatically create version on update
        """
        self.config_path = config_path
        self.validator = validator
        self.auto_version = auto_version
        
        # Current configuration
        self._config: Dict[str, Any] = {}
        self._current_version: Optional[str] = None
        
        # Version history
        self._versions: List[ConfigVersion] = []
        
        # Audit log
        self._audit_log: List[ConfigAuditEntry] = []
        
        # Change callbacks for hot-reload
        self._change_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # File modification tracking
        self._last_mtime: Optional[float] = None
        self._last_checksum: Optional[str] = None
    
    def load_or_create(
        self,
        path: Optional[str] = None,
        default_config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Load configuration from file or create with defaults.
        
        Args:
            path: Configuration file path (uses config_path if not provided)
            default_config: Default configuration to use if file doesn't exist
        
        Returns:
            True if loaded successfully
        """
        if path:
            self.config_path = path
        
        if not self.config_path:
            return False
        
        if os.path.exists(self.config_path):
            return self.load()
        elif default_config:
            self._config = copy.deepcopy(default_config)
            self._add_audit_entry("create", None, {"default_config": True})
            if self.auto_version:
                self._create_version("Initial configuration")
            self.save()
            return True
        
        return False
    
    def load(self, path: Optional[str] = None) -> bool:
        """
        Load configuration from file.
        
        Args:
            path: Configuration file path (uses config_path if not provided)
        
        Returns:
            True if loaded successfully
        """
        if path:
            self.config_path = path
        
        if not self.config_path or not os.path.exists(self.config_path):
            return False
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            
            # Update file tracking
            self._last_mtime = os.path.getmtime(self.config_path)
            self._last_checksum = self._compute_checksum(self._config)
            
            self._add_audit_entry("load", None, {"path": self.config_path})
            
            return True
        except (json.JSONDecodeError, IOError):
            return False
    
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            path: Configuration file path (uses config_path if not provided)
        
        Returns:
            True if saved successfully
        """
        if path:
            self.config_path = path
        
        if not self.config_path:
            return False
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path) or ".", exist_ok=True)
            
            # Write atomically using temp file
            temp_path = f"{self.config_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            os.replace(temp_path, self.config_path)
            
            # Update file tracking
            self._last_mtime = os.path.getmtime(self.config_path)
            self._last_checksum = self._compute_checksum(self._config)
            
            self._add_audit_entry("save", self._current_version, {"path": self.config_path})
            
            return True
        except IOError:
            return False
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> tuple:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate (uses current config if None)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        config_to_validate = config if config is not None else self._config
        
        # Basic validation
        if not isinstance(config_to_validate, dict):
            return False, "Configuration must be a dictionary"
        
        # Custom validator
        if self.validator:
            return self.validator(config_to_validate)
        
        return True, None
    
    def update(
        self,
        updates: Dict[str, Any],
        message: Optional[str] = None,
        author: Optional[str] = None,
    ) -> tuple:
        """
        Update configuration with new values.
        
        Args:
            updates: Key-value pairs to update
            message: Optional commit message
            author: Optional author name
        
        Returns:
            Tuple of (success, error_message)
        """
        # Validate updates
        new_config = copy.deepcopy(self._config)
        new_config.update(updates)
        
        is_valid, error = self.validate(new_config)
        if not is_valid:
            return False, error
        
        # Store previous state
        previous_config = copy.deepcopy(self._config)
        previous_version = self._current_version
        
        # Apply updates
        self._config = new_config
        
        # Create version
        if self.auto_version:
            version = self._create_version(message, author)
        else:
            version = None
        
        # Save
        self.save()
        
        # Notify callbacks
        self._notify_callbacks()
        
        self._add_audit_entry(
            "update",
            version,
            {
                "updates": updates,
                "previous_version": previous_version,
                "message": message,
            },
        )
        
        return True, None
    
    def set(
        self,
        key: str,
        value: Any,
        message: Optional[str] = None,
    ) -> tuple:
        """
        Set a single configuration value.
        
        Args:
            key: Configuration key
            value: New value
            message: Optional commit message
        
        Returns:
            Tuple of (success, error_message)
        """
        return self.update({key: value}, message)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
        
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Copy of current configuration
        """
        return copy.deepcopy(self._config)
    
    def delete(
        self,
        key: str,
        message: Optional[str] = None,
    ) -> bool:
        """
        Delete a configuration key.
        
        Args:
            key: Configuration key to delete
            message: Optional commit message
        
        Returns:
            True if key was deleted
        """
        if key not in self._config:
            return False
        
        del self._config[key]
        
        if self.auto_version:
            version = self._create_version(message or f"Delete {key}")
        else:
            version = None
        
        self.save()
        self._notify_callbacks()
        
        self._add_audit_entry("delete", version, {"key": key, "message": message})
        
        return True
    
    def version(self) -> Optional[str]:
        """
        Get current version.
        
        Returns:
            Current version string or None
        """
        return self._current_version
    
    def history(self, limit: Optional[int] = None) -> List[ConfigVersion]:
        """
        Get version history.
        
        Args:
            limit: Maximum number of versions to return
        
        Returns:
            List of ConfigVersion objects
        """
        if limit:
            return self._versions[-limit:]
        return self._versions.copy()
    
    def get_version(self, version: str) -> Optional[ConfigVersion]:
        """
        Get a specific version.
        
        Args:
            version: Version string
        
        Returns:
            ConfigVersion or None if not found
        """
        return next((v for v in self._versions if v.version == version), None)
    
    def rollback(self, version: str) -> tuple:
        """
        Rollback to a specific version.
        
        Args:
            version: Version to rollback to
        
        Returns:
            Tuple of (success, error_message)
        """
        target_version = self.get_version(version)
        if not target_version:
            return False, f"Version not found: {version}"
        
        # Validate target config
        is_valid, error = self.validate(target_version.config)
        if not is_valid:
            return False, f"Target version is invalid: {error}"
        
        # Store current state
        previous_version = self._current_version
        
        # Rollback
        self._config = copy.deepcopy(target_version.config)
        self._current_version = version
        
        # Mark as rolled back
        target_version.status = ConfigStatus.ROLLED_BACK
        
        # Create new version for the rollback
        if self.auto_version:
            new_version = self._create_version(f"Rollback to {version}")
        else:
            new_version = None
        
        self.save()
        self._notify_callbacks()
        
        self._add_audit_entry(
            "rollback",
            new_version,
            {
                "from_version": previous_version,
                "to_version": version,
            },
        )
        
        return True, None
    
    def diff(self, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare two versions.
        
        Args:
            version1: First version
            version2: Second version
        
        Returns:
            Dictionary with differences
        """
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)
        
        if not v1 or not v2:
            return {"error": "One or both versions not found"}
        
        diff_result = {
            "version1": version1,
            "version2": version2,
            "added": {},
            "removed": {},
            "changed": {},
        }
        
        # Find added and changed
        for key, value in v2.config.items():
            if key not in v1.config:
                diff_result["added"][key] = value
            elif v1.config[key] != value:
                diff_result["changed"][key] = {
                    "from": v1.config[key],
                    "to": value,
                }
        
        # Find removed
        for key in v1.config:
            if key not in v2.config:
                diff_result["removed"][key] = v1.config[key]
        
        return diff_result
    
    def check_reload(self) -> bool:
        """
        Check if configuration file has changed and reload if needed.
        
        Returns:
            True if configuration was reloaded
        """
        if not self.config_path or not os.path.exists(self.config_path):
            return False
        
        current_mtime = os.path.getmtime(self.config_path)
        
        if self._last_mtime is None or current_mtime > self._last_mtime:
            # File has been modified, check content
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    new_config = json.load(f)
                
                new_checksum = self._compute_checksum(new_config)
                
                if new_checksum != self._last_checksum:
                    # Content has changed
                    is_valid, error = self.validate(new_config)
                    if is_valid:
                        self._config = new_config
                        self._last_mtime = current_mtime
                        self._last_checksum = new_checksum
                        self._notify_callbacks()
                        self._add_audit_entry("hot_reload", None, {"path": self.config_path})
                        return True
            except (json.JSONDecodeError, IOError):
                pass
        
        return False
    
    def on_change(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback for configuration changes.
        
        Args:
            callback: Function to call when configuration changes
        """
        self._change_callbacks.append(callback)
    
    def off_change(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Unregister a change callback.
        
        Args:
            callback: Callback to remove
        """
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
    
    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks of configuration change."""
        config_copy = copy.deepcopy(self._config)
        for callback in self._change_callbacks:
            try:
                callback(config_copy)
            except Exception:
                pass  # Ignore callback errors
    
    def _compute_checksum(self, config: Dict[str, Any]) -> str:
        """Compute checksum for configuration."""
        config_str = json.dumps(config, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def _create_version(
        self,
        message: Optional[str] = None,
        author: Optional[str] = None,
    ) -> str:
        """
        Create a new version.
        
        Args:
            message: Version message
            author: Version author
        
        Returns:
            Version string
        """
        timestamp = datetime.now()
        version = f"v{timestamp.strftime('%Y%m%d.%H%M%S')}"
        
        # If version exists, add microsecond
        if any(v.version == version for v in self._versions):
            version = f"v{timestamp.strftime('%Y%m%d.%H%M%S.%f')}"
        
        checksum = self._compute_checksum(self._config)
        
        config_version = ConfigVersion(
            version=version,
            timestamp=timestamp.isoformat(),
            config=copy.deepcopy(self._config),
            checksum=checksum,
            author=author,
            message=message,
            status=ConfigStatus.VALID,
        )
        
        self._versions.append(config_version)
        self._current_version = version
        
        # Trim versions
        if len(self._versions) > self.MAX_VERSIONS:
            self._versions = self._versions[-self.MAX_VERSIONS:]
        
        return version
    
    def _add_audit_entry(
        self,
        action: str,
        version: Optional[str],
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an audit log entry."""
        entry = ConfigAuditEntry(
            timestamp=datetime.now().isoformat(),
            action=action,
            version=version,
            details=details or {},
        )
        
        self._audit_log.append(entry)
        
        # Trim audit log
        if len(self._audit_log) > self.MAX_AUDIT_ENTRIES:
            self._audit_log = self._audit_log[-self.MAX_AUDIT_ENTRIES:]
    
    def get_audit_log(self, limit: Optional[int] = None) -> List[ConfigAuditEntry]:
        """
        Get audit log.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of audit entries
        """
        if limit:
            return self._audit_log[-limit:]
        return self._audit_log.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get configuration statistics.
        
        Returns:
            Dictionary with statistics
        """
        action_counts = {}
        for entry in self._audit_log:
            action_counts[entry.action] = action_counts.get(entry.action, 0) + 1
        
        return {
            "current_version": self._current_version,
            "total_versions": len(self._versions),
            "total_audit_entries": len(self._audit_log),
            "action_counts": action_counts,
            "config_keys": len(self._config),
            "has_file": self.config_path is not None and os.path.exists(self.config_path),
        }
    
    def save_state(self, path: Optional[str] = None) -> str:
        """
        Save manager state to file.
        
        Args:
            path: Optional path to save to
        
        Returns:
            Path where state was saved
        """
        if path is None:
            path = os.path.join(
                os.path.dirname(self.config_path) or ".",
                f"{os.path.basename(self.config_path or 'config')}.state.json"
            )
        
        state = {
            "current_version": self._current_version,
            "versions": [v.to_dict() for v in self._versions],
            "audit_log": [e.to_dict() for e in self._audit_log[-50:]],  # Last 50
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        return path
    
    def load_state(self, path: Optional[str] = None) -> bool:
        """
        Load manager state from file.
        
        Args:
            path: Optional path to load from
        
        Returns:
            True if loaded successfully
        """
        if path is None:
            path = os.path.join(
                os.path.dirname(self.config_path) or ".",
                f"{os.path.basename(self.config_path or 'config')}.state.json"
            )
        
        if not os.path.exists(path):
            return False
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            self._current_version = state.get("current_version")
            self._versions = [
                ConfigVersion.from_dict(v) for v in state.get("versions", [])
            ]
            self._audit_log = [
                ConfigAuditEntry(**e) for e in state.get("audit_log", [])
            ]
            
            return True
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
    
    def __repr__(self) -> str:
        return (
            f"ConfigManager(version={self._current_version}, "
            f"versions={len(self._versions)}, "
            f"keys={len(self._config)})"
        )
