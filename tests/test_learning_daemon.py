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
Tests for claw-rl Learning Daemon
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import json
import os
import signal

from claw_rl.learning_daemon import LearningDaemon


class TestLearningDaemon:
    """Tests for LearningDaemon"""
    
    def test_init(self):
        """Test daemon initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = LearningDaemon(
                interval_seconds=60,
                data_dir=Path(tmpdir)
            )
            
            assert daemon.interval == 60
            assert daemon.data_dir == Path(tmpdir)
            assert daemon.running is False
    
    def test_run_cycle(self):
        """Test running a single cycle"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            rewards_dir = data_dir / 'rewards'
            hints_dir = data_dir / 'hints'
            rewards_dir.mkdir(parents=True)
            hints_dir.mkdir(parents=True)
            
            # Create test rewards
            today = datetime.now().strftime('%Y-%m-%d')
            reward_file = rewards_dir / f'{today}.jsonl'
            with open(reward_file, 'w') as f:
                f.write(json.dumps({'reward': 1, 'session_id': 's001'}) + '\n')
                f.write(json.dumps({'reward': -1, 'session_id': 's002'}) + '\n')
            
            # Create test hints
            hint_file = hints_dir / f'{today}.jsonl'
            with open(hint_file, 'w') as f:
                f.write(json.dumps({'hint': '测试提示', 'session_id': 's001'}) + '\n')
            
            daemon = LearningDaemon(data_dir=data_dir)
            results = daemon.run_cycle()
            
            assert results['rewards_processed'] == 2
            assert results['hints_processed'] == 1
    
    def test_learning_trigger(self):
        """Test learning trigger with negative rewards"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            rewards_dir = data_dir / 'rewards'
            hints_dir = data_dir / 'hints'
            rewards_dir.mkdir(parents=True)
            hints_dir.mkdir(parents=True)
            
            # Create 3 negative rewards
            today = datetime.now().strftime('%Y-%m-%d')
            reward_file = rewards_dir / f'{today}.jsonl'
            with open(reward_file, 'w') as f:
                for i in range(3):
                    f.write(json.dumps({'reward': -1, 'session_id': f's{i}'}) + '\n')
            
            # Create test hint
            hint_file = hints_dir / f'{today}.jsonl'
            with open(hint_file, 'w') as f:
                f.write(json.dumps({'hint': '学习模式', 'session_id': 's001'}) + '\n')
            
            daemon = LearningDaemon(data_dir=data_dir)
            results = daemon.run_cycle()
            
            assert results['learning_triggered'] is True
            assert results['patterns_written'] == 1
    
    def test_no_learning_trigger_with_positive_rewards(self):
        """Test no learning trigger with positive rewards"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            rewards_dir = data_dir / 'rewards'
            rewards_dir.mkdir(parents=True)
            
            # Create positive rewards
            today = datetime.now().strftime('%Y-%m-%d')
            reward_file = rewards_dir / f'{today}.jsonl'
            with open(reward_file, 'w') as f:
                for i in range(5):
                    f.write(json.dumps({'reward': 1, 'session_id': f's{i}'}) + '\n')
            
            daemon = LearningDaemon(data_dir=data_dir)
            results = daemon.run_cycle()
            
            assert results['learning_triggered'] is False
    
    def test_load_recent_rewards(self):
        """Test loading recent rewards"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            rewards_dir = data_dir / 'rewards'
            rewards_dir.mkdir(parents=True)
            
            # Create rewards for today and yesterday
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            with open(rewards_dir / f'{today}.jsonl', 'w') as f:
                f.write(json.dumps({'reward': 1}) + '\n')
            
            with open(rewards_dir / f'{yesterday}.jsonl', 'w') as f:
                f.write(json.dumps({'reward': -1}) + '\n')
            
            daemon = LearningDaemon(data_dir=data_dir)
            rewards = daemon._load_recent_rewards(days=7)
            
            assert len(rewards) == 2
    
    def test_load_recent_hints(self):
        """Test loading recent hints"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            hints_dir = data_dir / 'hints'
            hints_dir.mkdir(parents=True)
            
            today = datetime.now().strftime('%Y-%m-%d')
            with open(hints_dir / f'{today}.jsonl', 'w') as f:
                f.write(json.dumps({'hint': '提示1'}) + '\n')
                f.write(json.dumps({'hint': '提示2'}) + '\n')
            
            daemon = LearningDaemon(data_dir=data_dir)
            hints = daemon._load_recent_hints(days=7)
            
            assert len(hints) == 2
    
    def test_pid_file_created(self):
        """Test PID file is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = LearningDaemon(data_dir=Path(tmpdir))
            daemon._write_pid()
            
            assert daemon.pid_file.exists()
            
            with open(daemon.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            assert pid == os.getpid()
    
    def test_log_file_created(self):
        """Test log file is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = LearningDaemon(data_dir=Path(tmpdir))
            daemon._log("Test message")
            
            assert daemon.log_file.exists()
            
            with open(daemon.log_file, 'r') as f:
                content = f.read()
            
            assert "Test message" in content
    
    def test_cleanup_old_data(self):
        """Test cleanup of old data files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            rewards_dir = data_dir / 'rewards'
            hints_dir = data_dir / 'hints'
            rewards_dir.mkdir(parents=True)
            hints_dir.mkdir(parents=True)
            
            # Create old file (100 days ago)
            old_date = (datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d')
            old_reward = rewards_dir / f'{old_date}.jsonl'
            old_hint = hints_dir / f'{old_date}.jsonl'
            old_reward.write_text('{}')
            old_hint.write_text('{}')
            
            # Create recent file
            today = datetime.now().strftime('%Y-%m-%d')
            new_reward = rewards_dir / f'{today}.jsonl'
            new_hint = hints_dir / f'{today}.jsonl'
            new_reward.write_text('{}')
            new_hint.write_text('{}')
            
            daemon = LearningDaemon(data_dir=data_dir)
            daemon._cleanup_old_data(days=90)
            
            # Old files should be deleted
            assert not old_reward.exists()
            assert not old_hint.exists()
            
            # New files should remain
            assert new_reward.exists()
            assert new_hint.exists()
    
    def test_is_running(self):
        """Test is_running class method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Not running initially
            assert LearningDaemon.is_running(data_dir=Path(tmpdir)) is False
            
            # Write PID file
            daemon = LearningDaemon(data_dir=Path(tmpdir))
            daemon._write_pid()
            
            # Should be running now
            assert LearningDaemon.is_running(data_dir=Path(tmpdir)) is True
    
    def test_stop_daemon(self):
        """Test stop_daemon class method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write PID file (use a fake PID to avoid terminating ourselves)
            pid_file = Path(tmpdir) / 'daemon.pid'
            pid_file.write_text('999999999')  # Non-existent PID
            
            # Stop daemon should remove PID file
            result = LearningDaemon.stop_daemon(data_dir=Path(tmpdir))
            
            # Should return False (process doesn't exist)
            assert result is False
            # PID file should be cleaned up
            assert not pid_file.exists()
    
    def test_should_learn(self):
        """Test learning trigger logic"""
        with tempfile.TemporaryDirectory() as tmpdir:
            daemon = LearningDaemon(data_dir=Path(tmpdir))
            
            # 3 negative rewards -> should learn
            rewards = [
                {'reward': -1},
                {'reward': -1},
                {'reward': -1}
            ]
            assert daemon._should_learn(rewards) is True
            
            # 2 negative rewards -> should not learn
            rewards = [
                {'reward': -1},
                {'reward': -1}
            ]
            assert daemon._should_learn(rewards) is False
            
            # All positive -> should not learn
            rewards = [
                {'reward': 1},
                {'reward': 1},
                {'reward': 1}
            ]
            assert daemon._should_learn(rewards) is False
