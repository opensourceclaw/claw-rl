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
Tests for claw-rl Session Lifecycle Hooks
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import json

from claw_rl.hooks import (
    PreSessionHook,
    PreSessionInput,
    PreSessionOutput,
    PostSessionHook,
    PostSessionInput,
    PostSessionOutput,
    Turn
)


class TestPreSessionHook:
    """Tests for PreSessionHook"""
    
    def test_execute_returns_output(self):
        """Test that execute returns PreSessionOutput"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PreSessionHook(data_dir=Path(tmpdir))
            
            result = hook.execute(PreSessionInput(
                session_id="test_001",
                user_id="peter",
                timestamp="2026-03-29T09:00:00"
            ))
            
            assert isinstance(result, PreSessionOutput)
            assert result.active is True
    
    def test_load_hints_from_files(self):
        """Test loading hints from hint files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            hints_dir = data_dir / 'hints'
            hints_dir.mkdir(parents=True)
            
            # Create hint file
            today = datetime.now().strftime('%Y-%m-%d')
            hint_file = hints_dir / f'{today}.jsonl'
            
            with open(hint_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps({'hint': '操作前先检查文件'}) + '\n')
                f.write(json.dumps({'hint': '避免直接覆盖'}) + '\n')
            
            hook = PreSessionHook(data_dir=data_dir)
            result = hook.execute(PreSessionInput(
                session_id="test_001",
                user_id="peter",
                timestamp="2026-03-29T09:00:00"
            ))
            
            assert len(result.hints) == 2
            assert '操作前先检查文件' in result.hints
            assert '避免直接覆盖' in result.hints
    
    def test_build_memory_with_hints(self):
        """Test building memory with hints"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            hints_dir = data_dir / 'hints'
            hints_dir.mkdir(parents=True)
            
            # Create hint file
            today = datetime.now().strftime('%Y-%m-%d')
            hint_file = hints_dir / f'{today}.jsonl'
            
            with open(hint_file, 'w', encoding='utf-8') as f:
                f.write(json.dumps({'hint': '测试提示'}) + '\n')
            
            hook = PreSessionHook(data_dir=data_dir)
            result = hook.execute(PreSessionInput(
                session_id="test_001",
                user_id="peter",
                timestamp="2026-03-29T09:00:00"
            ))
            
            assert '测试提示' in result.injected_memory
            assert '🧠' in result.injected_memory
    
    def test_empty_when_no_data(self):
        """Test empty output when no data exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create isolated data directories
            data_dir = Path(tmpdir) / 'claw-rl' / 'data'
            data_dir.mkdir(parents=True)
            
            # Also create isolated memory directory
            mem_dir = Path(tmpdir) / 'memory'
            mem_dir.mkdir(parents=True)
            
            hook = PreSessionHook(data_dir=data_dir)
            
            # Override _load_patterns to return empty (avoid reading real claw-mem)
            hook._load_patterns = lambda limit: []
            
            result = hook.execute(PreSessionInput(
                session_id="test_001",
                user_id="peter",
                timestamp="2026-03-29T09:00:00"
            ))
            
            assert result.hints == []
            assert result.patterns == []
            assert result.injected_memory == ""


class TestPostSessionHook:
    """Tests for PostSessionHook"""
    
    def test_execute_returns_output(self):
        """Test that execute returns PostSessionOutput"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            result = hook.execute(PostSessionInput(
                session_id="test_001",
                user_id="peter",
                turns=[]
            ))
            
            assert isinstance(result, PostSessionOutput)
            assert result.rewards_recorded == 0
            assert result.hints_extracted == 0
    
    def test_judge_reward_positive(self):
        """Test judging positive reward"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            # Test positive keywords
            assert hook._judge_reward("action", "谢谢，很好") == +1
            assert hook._judge_reward("action", "好的") == +1
            assert hook._judge_reward("action", "不错的建议") == +1
    
    def test_judge_reward_negative(self):
        """Test judging negative reward"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            # Test negative keywords
            assert hook._judge_reward("action", "不对，应该这样") == -1
            assert hook._judge_reward("action", "错了") == -1
            assert hook._judge_reward("action", "不要这样做") == -1
    
    def test_judge_reward_neutral(self):
        """Test judging neutral reward"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            # Test neutral
            assert hook._judge_reward("action", "这是一段普通回复") == 0
            assert hook._judge_reward("action", "hello world") == 0
    
    def test_extract_hint_from_correction(self):
        """Test extracting hint from correction"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            # Test "应该 X" pattern
            hint = hook._extract_hint("应该先检查文件")
            assert hint == "操作前先检查文件"
            
            # Test "不要 X" pattern
            hint = hook._extract_hint("不要直接覆盖")
            assert hint == "避免直接覆盖"
    
    def test_record_rewards(self):
        """Test recording rewards"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            result = hook.execute(PostSessionInput(
                session_id="test_001",
                user_id="peter",
                turns=[
                    Turn(turn_id=1, action="创建文件", next_state="谢谢"),
                    Turn(turn_id=2, action="编辑文件", next_state="不对，应该放这里")
                ]
            ))
            
            assert result.rewards_recorded == 2
            assert result.hints_extracted == 1
    
    def test_reward_files_created(self):
        """Test that reward files are created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            hook.execute(PostSessionInput(
                session_id="test_001",
                user_id="peter",
                turns=[
                    Turn(turn_id=1, action="创建文件", next_state="谢谢")
                ]
            ))
            
            # Check reward file exists
            today = datetime.now().strftime('%Y-%m-%d')
            rewards_file = Path(tmpdir) / 'rewards' / f'{today}.jsonl'
            assert rewards_file.exists()
    
    def test_hint_files_created(self):
        """Test that hint files are created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            hook.execute(PostSessionInput(
                session_id="test_001",
                user_id="peter",
                turns=[
                    Turn(turn_id=1, action="创建文件", next_state="不对，应该先检查")
                ]
            ))
            
            # Check hint file exists
            today = datetime.now().strftime('%Y-%m-%d')
            hints_file = Path(tmpdir) / 'hints' / f'{today}.jsonl'
            assert hints_file.exists()
    
    def test_learning_trigger_on_negative_accumulation(self):
        """Test learning trigger when negative rewards accumulate"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            # Create 3 negative rewards
            for i in range(3):
                hook.execute(PostSessionInput(
                    session_id=f"test_{i}",
                    user_id="peter",
                    turns=[
                        Turn(turn_id=1, action="action", next_state="不对")
                    ]
                ))
            
            # Next execution should trigger learning
            result = hook.execute(PostSessionInput(
                session_id="test_final",
                user_id="peter",
                turns=[]
            ))
            
            assert result.learning_triggered is True
    
    def test_no_learning_trigger_with_positive_rewards(self):
        """Test no learning trigger with positive rewards"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            result = hook.execute(PostSessionInput(
                session_id="test_001",
                user_id="peter",
                turns=[
                    Turn(turn_id=1, action="action", next_state="谢谢")
                ]
            ))
            
            assert result.learning_triggered is False
    
    def test_empty_session(self):
        """Test empty session"""
        with tempfile.TemporaryDirectory() as tmpdir:
            hook = PostSessionHook(data_dir=Path(tmpdir))
            
            result = hook.execute(PostSessionInput(
                session_id="test_empty",
                user_id="user",
                turns=[]
            ))
            
            assert result.rewards_recorded == 0
            assert result.hints_extracted == 0
    
    def test_long_correction_hint_extraction(self):
        """Test hint extraction from long correction"""
        hook = PostSessionHook()
        
        long_correction = "这是一个非常长的纠正文本" * 20  # > 100 chars
        
        hint = hook._extract_hint(long_correction)
        
        # Long corrections should return None or be truncated
        assert hint is None or len(hint) < 100
