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
Tests for claw-rl Auto-Activation Module
"""

import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime

from claw_rl.auto_activate import (
    AutoActivator,
    get_activator,
    is_active,
    get_status,
    get_data_dir
)


class TestAutoActivator:
    """Tests for AutoActivator class"""
    
    def test_not_active_without_env(self):
        """Test that claw-rl is not active without CLAWRL_ENABLED"""
        # Save original env
        original = os.environ.get('CLAWRL_ENABLED')
        
        # Remove env var
        if 'CLAWRL_ENABLED' in os.environ:
            del os.environ['CLAWRL_ENABLED']
        
        try:
            activator = AutoActivator()
            assert not activator.is_active()
            assert not activator.enabled
        finally:
            # Restore original env
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
    
    def test_active_with_env(self):
        """Test that claw-rl is active with CLAWRL_ENABLED=1"""
        # Save original env
        original = os.environ.get('CLAWRL_ENABLED')
        
        # Set env var
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                activator = AutoActivator(data_dir=data_dir)
                
                assert activator.is_active()
                assert activator.enabled
                assert activator._activation_status == "active"
                assert activator._activation_time is not None
        finally:
            # Restore original env
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']
    
    def test_directories_created(self):
        """Test that data directories are created on activation"""
        original = os.environ.get('CLAWRL_ENABLED')
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                activator = AutoActivator(data_dir=data_dir)
                
                # Check directories exist
                assert data_dir.exists()
                assert (data_dir / 'rewards').exists()
                assert (data_dir / 'hints').exists()
                assert (data_dir / 'learnings').exists()
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']
    
    def test_activation_log_created(self):
        """Test that activation log is created"""
        original = os.environ.get('CLAWRL_ENABLED')
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                activator = AutoActivator(data_dir=data_dir)
                
                # Check log file exists
                log_file = data_dir / 'activation.log'
                assert log_file.exists()
                
                # Check log content
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert 'claw-rl activated' in content
                    assert str(data_dir) in content
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']
    
    def test_get_status(self):
        """Test get_status method"""
        original = os.environ.get('CLAWRL_ENABLED')
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                activator = AutoActivator(data_dir=data_dir)
                
                status = activator.get_status()
                
                assert status['enabled'] is True
                assert status['active'] is True
                assert status['status'] == 'active'
                assert status['activation_time'] is not None
                assert status['data_dir'] == str(data_dir)
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']
    
    def test_get_data_dir(self):
        """Test get_data_dir method"""
        original = os.environ.get('CLAWRL_ENABLED')
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                activator = AutoActivator(data_dir=data_dir)
                
                result = activator.get_data_dir()
                assert result == data_dir
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']
    
    def test_get_data_dir_returns_none_when_inactive(self):
        """Test get_data_dir returns None when not active"""
        original = os.environ.get('CLAWRL_ENABLED')
        
        if 'CLAWRL_ENABLED' in os.environ:
            del os.environ['CLAWRL_ENABLED']
        
        try:
            activator = AutoActivator()
            result = activator.get_data_dir()
            assert result is None
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
    
    def test_multiple_activations(self):
        """Test multiple activations don't fail"""
        original = os.environ.get('CLAWRL_ENABLED')
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                
                # First activation
                activator1 = AutoActivator(data_dir=data_dir)
                assert activator1.is_active()
                
                # Second activation (should not fail)
                activator2 = AutoActivator(data_dir=data_dir)
                assert activator2.is_active()
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']


class TestModuleFunctions:
    """Tests for module-level functions"""
    
    def test_get_activator(self):
        """Test get_activator returns AutoActivator instance"""
        activator = get_activator()
        assert isinstance(activator, AutoActivator)
    
    def test_is_active_function(self):
        """Test is_active function"""
        original = os.environ.get('CLAWRL_ENABLED')
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            # Create new activator with env set
            from claw_rl.auto_activate import AutoActivator
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                activator = AutoActivator(data_dir=data_dir)
                assert activator.is_active() is True
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']
    
    def test_get_status_function(self):
        """Test get_status function"""
        status = get_status()
        assert isinstance(status, dict)
        assert 'enabled' in status
        assert 'active' in status
    
    def test_get_data_dir_function(self):
        """Test get_data_dir function"""
        original = os.environ.get('CLAWRL_ENABLED')
        os.environ['CLAWRL_ENABLED'] = '1'
        
        try:
            from claw_rl.auto_activate import AutoActivator
            with tempfile.TemporaryDirectory() as tmpdir:
                data_dir = Path(tmpdir) / 'claw-rl' / 'data'
                activator = AutoActivator(data_dir=data_dir)
                result = activator.get_data_dir()
                assert result == data_dir
        finally:
            if original is not None:
                os.environ['CLAWRL_ENABLED'] = original
            else:
                del os.environ['CLAWRL_ENABLED']
