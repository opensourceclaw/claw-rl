# Copyright 2026 Peter Cheng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
claw-rl Auto-Activation Module

Automatically activates claw-rl when CLAWRL_ENABLED=1 environment variable is set.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class AutoActivator:
    """
    Auto-activate claw-rl when CLAWRL_ENABLED=1
    
    Usage:
        # In ~/.zshrc or ~/.bashrc
        export CLAWRL_ENABLED=1
        
        # In Python code
        from claw_rl.auto_activate import AutoActivator
        activator = AutoActivator()
        
        if activator.is_active():
            print("claw-rl is active!")
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Auto-Activator
        
        Args:
            data_dir: Optional custom data directory
        """
        self.enabled = os.getenv('CLAWRL_ENABLED', '0') == '1'
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        self._activation_time: Optional[str] = None
        self._activation_status: str = "not_activated"
        
        if self.enabled:
            self._activate()
    
    def _activate(self) -> bool:
        """
        Initialize claw-rl on activation
        
        Returns:
            bool: True if activation successful
        """
        try:
            # Create data directories
            self._create_directories()
            
            # Create activation marker
            self._activation_time = datetime.now().isoformat()
            self._activation_status = "active"
            
            # Write activation log
            self._log_activation()
            
            return True
            
        except Exception as e:
            self._activation_status = f"error: {str(e)}"
            return False
    
    def _create_directories(self) -> None:
        """Create required data directories"""
        directories = [
            self.data_dir,
            self.data_dir / 'rewards',
            self.data_dir / 'hints',
            self.data_dir / 'learnings',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _log_activation(self) -> None:
        """Log activation event"""
        log_file = self.data_dir / 'activation.log'
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{self._activation_time}] claw-rl activated\n")
            f.write(f"  data_dir: {self.data_dir}\n")
            f.write(f"  status: {self._activation_status}\n")
    
    def is_active(self) -> bool:
        """
        Check if claw-rl is active
        
        Returns:
            bool: True if claw-rl is active
        """
        return self.enabled and self._activation_status == "active"
    
    def get_status(self) -> dict:
        """
        Get activation status
        
        Returns:
            dict: Status information
        """
        return {
            "enabled": self.enabled,
            "active": self.is_active(),
            "status": self._activation_status,
            "activation_time": self._activation_time,
            "data_dir": str(self.data_dir) if self.enabled else None,
        }
    
    def get_data_dir(self) -> Optional[Path]:
        """
        Get data directory path
        
        Returns:
            Optional[Path]: Data directory if active, None otherwise
        """
        return self.data_dir if self.is_active() else None


# Global activator instance (auto-activated on import if CLAWRL_ENABLED=1)
_activator: Optional[AutoActivator] = None


def get_activator() -> AutoActivator:
    """
    Get or create global activator instance
    
    Returns:
        AutoActivator: Global activator instance
    """
    global _activator
    
    if _activator is None:
        _activator = AutoActivator()
    
    return _activator


def is_active() -> bool:
    """
    Check if claw-rl is active
    
    Returns:
        bool: True if claw-rl is active
    """
    return get_activator().is_active()


def get_status() -> dict:
    """
    Get activation status
    
    Returns:
        dict: Status information
    """
    return get_activator().get_status()


def get_data_dir() -> Optional[Path]:
    """
    Get data directory path
    
    Returns:
        Optional[Path]: Data directory if active, None otherwise
    """
    return get_activator().get_data_dir()


# Auto-activate on import if CLAWRL_ENABLED=1
_activator = AutoActivator()
