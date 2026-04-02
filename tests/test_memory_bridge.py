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
Tests for claw-rl Memory Bridge
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import json

from claw_rl.core.memory_bridge import ClawMemBridge


class TestClawMemBridge:
    """Tests for ClawMemBridge"""
    
    def test_init_creates_directories(self):
        """Test that initialization creates directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            assert claw_mem_dir.exists()
            assert (claw_rl_dir / 'learnings').exists()
    
    def test_write_pattern(self):
        """Test writing a pattern"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            bridge.write_pattern(
                pattern="操作前先检查文件",
                confidence=0.85,
                source="User correction",
                session_id="session_001"
            )
            
            # Check learnings file
            learnings_file = claw_mem_dir / 'claw-rl-learnings.md'
            assert learnings_file.exists()
            
            content = learnings_file.read_text()
            assert '操作前先检查文件' in content
            assert '85%' in content
            assert 'User correction' in content
    
    def test_write_pattern_to_memory_file(self):
        """Test writing pattern to MEMORY.md"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            # Create memory directory first
            claw_mem_dir.mkdir(parents=True, exist_ok=True)
            
            # Create MEMORY.md
            memory_file = claw_mem_dir / 'MEMORY.md'
            memory_file.write_text('# MEMORY\n')
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            bridge.write_pattern(
                pattern="测试模式",
                confidence=0.9,
                source="Test",
                session_id="session_002"
            )
            
            # Check MEMORY.md
            content = memory_file.read_text()
            assert '测试模式' in content
    
    def test_read_patterns(self):
        """Test reading patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            # Write patterns
            bridge.write_pattern("模式1", 0.8, "Test", "s001")
            bridge.write_pattern("模式2", 0.9, "Test", "s002")
            
            # Read patterns
            patterns = bridge.read_patterns(limit=10)
            
            assert len(patterns) == 2
            # Most recent first
            assert patterns[0]['pattern'] == "模式2"
            assert patterns[1]['pattern'] == "模式1"
    
    def test_read_patterns_limit(self):
        """Test reading patterns with limit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            # Write 5 patterns
            for i in range(5):
                bridge.write_pattern(f"模式{i}", 0.8, "Test", f"s{i}")
            
            # Read with limit
            patterns = bridge.read_patterns(limit=3)
            
            assert len(patterns) == 3
    
    def test_read_hints(self):
        """Test reading hints"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            hints_dir = claw_rl_dir / 'hints'
            hints_dir.mkdir(parents=True)
            
            # Create hint file
            today = datetime.now().strftime('%Y-%m-%d')
            hint_file = hints_dir / f'{today}.jsonl'
            
            with open(hint_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps({'hint': '提示1'}) + '\n')
                f.write(json.dumps({'hint': '提示2'}) + '\n')
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            hints = bridge.read_hints(limit=10)
            
            assert len(hints) == 2
            assert '提示1' in hints
            assert '提示2' in hints
    
    def test_get_statistics(self):
        """Test getting statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            # Write patterns
            bridge.write_pattern("模式1", 0.8, "Correction", "s001")
            bridge.write_pattern("模式2", 0.9, "Accumulation", "s002")
            
            stats = bridge.get_statistics()
            
            assert stats['total_patterns'] == 2
            assert 0.8 <= stats['avg_confidence'] <= 0.9
            assert 'Correction' in stats['sources']
            assert 'Accumulation' in stats['sources']
    
    def test_clear_old_patterns(self):
        """Test clearing old patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            # Write patterns
            bridge.write_pattern("模式1", 0.8, "Test", "s001")
            bridge.write_pattern("模式2", 0.9, "Test", "s002")
            
            # Clear old patterns (should clear none since they're recent)
            cleared = bridge.clear_old_patterns(days=90)
            
            assert cleared == 0
            
            # Patterns should still exist
            patterns = bridge.read_patterns()
            assert len(patterns) == 2
    
    def test_pattern_jsonl_created(self):
        """Test that patterns.jsonl is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            bridge.write_pattern("测试", 0.8, "Test", "s001")
            
            patterns_file = claw_rl_dir / 'learnings' / 'patterns.jsonl'
            assert patterns_file.exists()
            
            # Verify content
            with open(patterns_file, 'r') as f:
                data = json.loads(f.readline())
                assert data['pattern'] == "测试"
                assert data['confidence'] == 0.8
    
    def test_empty_patterns_when_no_data(self):
        """Test empty patterns when no data exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            claw_mem_dir = Path(tmpdir) / 'memory'
            claw_rl_dir = Path(tmpdir) / 'claw-rl' / 'data'
            
            bridge = ClawMemBridge(
                claw_mem_dir=claw_mem_dir,
                claw_rl_dir=claw_rl_dir
            )
            
            patterns = bridge.read_patterns()
            assert patterns == []
            
            hints = bridge.read_hints()
            assert hints == []
