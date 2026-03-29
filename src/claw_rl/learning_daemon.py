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
claw-rl Learning Daemon

Background process that periodically runs learning cycles.
"""

import os
import signal
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class LearningDaemon:
    """
    Background Learning Loop
    
    Runs learning cycles periodically to process rewards and hints,
    and trigger learning updates when thresholds are met.
    
    Usage:
        # Start daemon
        daemon = LearningDaemon(interval_seconds=300)
        daemon.start()
        
        # Or run single cycle
        daemon.run_cycle()
    """
    
    def __init__(
        self,
        interval_seconds: int = 300,
        data_dir: Optional[Path] = None
    ):
        """
        Initialize Learning Daemon
        
        Args:
            interval_seconds: Interval between cycles (default 5 minutes)
            data_dir: Optional custom data directory
        """
        self.interval = interval_seconds
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        
        # File paths
        self.pid_file = self.data_dir / 'daemon.pid'
        self.log_file = self.data_dir / 'daemon.log'
        self.rewards_dir = self.data_dir / 'rewards'
        self.hints_dir = self.data_dir / 'hints'
        
        # State
        self.running = False
        self._cycle_count = 0
    
    def start(self) -> None:
        """
        Start the daemon (blocking)
        
        Runs learning cycles at the specified interval until stopped.
        """
        self._write_pid()
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)
        
        self._log("Learning daemon started")
        self._log(f"  Interval: {self.interval} seconds")
        self._log(f"  Data directory: {self.data_dir}")
        
        try:
            while self.running:
                self.run_cycle()
                self._sleep_with_interrupt(self.interval)
        except KeyboardInterrupt:
            self._log("Interrupted by user")
        finally:
            self.stop()
    
    def run_cycle(self) -> Dict:
        """
        Run a single learning cycle
        
        Returns:
            Dict: Cycle results
        """
        self._cycle_count += 1
        start_time = datetime.now()
        
        self._log(f"Cycle {self._cycle_count} started")
        
        results = {
            'cycle': self._cycle_count,
            'timestamp': start_time.isoformat(),
            'rewards_processed': 0,
            'hints_processed': 0,
            'learning_triggered': False,
            'patterns_written': 0
        }
        
        try:
            # 1. Process rewards
            rewards = self._load_recent_rewards()
            results['rewards_processed'] = len(rewards)
            
            # 2. Process hints
            hints = self._load_recent_hints()
            results['hints_processed'] = len(hints)
            
            # 3. Check learning trigger
            if self._should_learn(rewards):
                patterns = self._trigger_learning(rewards, hints)
                results['learning_triggered'] = True
                results['patterns_written'] = len(patterns)
                self._log(f"  Learning triggered: {len(patterns)} patterns written")
            
            # 4. Cleanup old data
            self._cleanup_old_data()
            
        except Exception as e:
            self._log(f"  Error: {str(e)}")
            results['error'] = str(e)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        results['duration_seconds'] = duration
        
        self._log(f"  Cycle completed in {duration:.2f}s")
        self._log(f"  Rewards: {results['rewards_processed']}, Hints: {results['hints_processed']}")
        
        return results
    
    def stop(self) -> None:
        """Stop the daemon"""
        self.running = False
        self._log("Learning daemon stopped")
        
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def _write_pid(self) -> None:
        """Write PID file"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def _log(self, message: str) -> None:
        """Log message to file"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        # Ensure directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Also print to stdout
        print(log_entry.strip())
    
    def _sleep_with_interrupt(self, seconds: int) -> None:
        """Sleep but check for interrupt"""
        for _ in range(seconds):
            if not self.running:
                break
            time.sleep(1)
    
    def _shutdown(self, signum, frame) -> None:
        """Graceful shutdown handler"""
        self._log(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def _load_recent_rewards(self, days: int = 7) -> List[Dict]:
        """Load rewards from recent days"""
        rewards = []
        cutoff = datetime.now() - timedelta(days=days)
        
        if not self.rewards_dir.exists():
            return rewards
        
        for reward_file in sorted(self.rewards_dir.glob('*.jsonl'), reverse=True):
            try:
                # Parse date from filename
                file_date = datetime.strptime(reward_file.stem, '%Y-%m-%d')
                if file_date < cutoff:
                    continue
                
                # Read rewards
                with open(reward_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        rewards.append(data)
                        
            except (ValueError, json.JSONDecodeError):
                continue
        
        return rewards
    
    def _load_recent_hints(self, days: int = 7) -> List[Dict]:
        """Load hints from recent days"""
        hints = []
        cutoff = datetime.now() - timedelta(days=days)
        
        if not self.hints_dir.exists():
            return hints
        
        for hint_file in sorted(self.hints_dir.glob('*.jsonl'), reverse=True):
            try:
                # Parse date from filename
                file_date = datetime.strptime(hint_file.stem, '%Y-%m-%d')
                if file_date < cutoff:
                    continue
                
                # Read hints
                with open(hint_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        hints.append(data)
                        
            except (ValueError, json.JSONDecodeError):
                continue
        
        return hints
    
    def _should_learn(self, rewards: List[Dict]) -> bool:
        """Check if learning should be triggered"""
        # Count negative rewards
        negative_count = sum(1 for r in rewards if r.get('reward', 0) == -1)
        
        # Trigger if >= 3 negative rewards in recent period
        return negative_count >= 3
    
    def _trigger_learning(self, rewards: List[Dict], hints: List[Dict]) -> List[str]:
        """Trigger learning update"""
        from .memory_bridge import ClawMemBridge
        
        bridge = ClawMemBridge()
        patterns = []
        
        # Extract patterns from hints
        for hint_data in hints:
            hint = hint_data.get('hint', '')
            if hint:
                bridge.write_pattern(
                    pattern=hint,
                    confidence=0.85,
                    source='User correction',
                    session_id=hint_data.get('session_id', 'unknown')
                )
                patterns.append(hint)
        
        return patterns
    
    def _cleanup_old_data(self, days: int = 90) -> None:
        """Cleanup data older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Cleanup rewards
        if self.rewards_dir.exists():
            for reward_file in self.rewards_dir.glob('*.jsonl'):
                try:
                    file_date = datetime.strptime(reward_file.stem, '%Y-%m-%d')
                    if file_date < cutoff:
                        reward_file.unlink()
                        self._log(f"  Cleaned up old reward file: {reward_file.name}")
                except ValueError:
                    pass
        
        # Cleanup hints
        if self.hints_dir.exists():
            for hint_file in self.hints_dir.glob('*.jsonl'):
                try:
                    file_date = datetime.strptime(hint_file.stem, '%Y-%m-%d')
                    if file_date < cutoff:
                        hint_file.unlink()
                        self._log(f"  Cleaned up old hint file: {hint_file.name}")
                except ValueError:
                    pass
    
    @classmethod
    def is_running(cls, data_dir: Optional[Path] = None) -> bool:
        """
        Check if daemon is already running
        
        Args:
            data_dir: Optional custom data directory
            
        Returns:
            bool: True if daemon is running
        """
        data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        pid_file = data_dir / 'daemon.pid'
        
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is running
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            # PID file exists but process not running
            pid_file.unlink()
            return False
    
    @classmethod
    def stop_daemon(cls, data_dir: Optional[Path] = None) -> bool:
        """
        Stop running daemon
        
        Args:
            data_dir: Optional custom data directory
            
        Returns:
            bool: True if daemon was stopped
        """
        data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        pid_file = data_dir / 'daemon.pid'
        
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            pid_file.unlink()
            return False
