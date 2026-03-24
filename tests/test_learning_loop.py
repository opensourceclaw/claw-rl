"""
Tests for Learning Loop

Run with: pytest tests/test_learning_loop.py -v
"""

import pytest
from pathlib import Path
import tempfile
from claw_rl.learning_loop import LearningLoop


class TestLearningLoop:
    """Test suite for LearningLoop."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def loop(self, temp_data_dir):
        """Create a LearningLoop instance for testing."""
        return LearningLoop(temp_data_dir)
    
    def test_init_creates_directories(self, temp_data_dir):
        """Test that initialization creates required directories."""
        loop = LearningLoop(temp_data_dir)
        assert loop.rewards_dir.exists()
        assert loop.hints_dir.exists()
        assert loop.learnings_dir.exists()
    
    def test_process_feedback_positive(self, loop):
        """Test processing positive feedback."""
        result = loop.process_feedback("谢谢", "test action", "test context")
        assert result['reward'] == 1
        assert result['feedback'] == "谢谢"
        assert result['action'] == "test action"
    
    def test_process_feedback_negative_with_hint(self, loop):
        """Test processing negative feedback with hint extraction."""
        result = loop.process_feedback("应该这样", "test action", "test context")
        assert result['reward'] == -1
        assert len(result['hints']) > 0
    
    def test_process_feedback_neutral(self, loop):
        """Test processing neutral feedback."""
        result = loop.process_feedback("嗯", "test action")
        assert result['reward'] == 0
        assert len(result['hints']) == 0
    
    def test_process_feedback_without_context(self, loop):
        """Test processing feedback without context."""
        result = loop.process_feedback("谢谢", "test action")
        assert result['context'] == ''
    
    def test_process_batch(self, loop):
        """Test batch processing."""
        feedbacks = [
            {'feedback': '谢谢', 'action': 'action1'},
            {'feedback': '应该这样', 'action': 'action2'},
            {'feedback': '很好', 'action': 'action3'},
        ]
        results = loop.process_batch(feedbacks)
        assert len(results) == 3
        assert results[0]['reward'] == 1
        assert results[1]['reward'] == -1
        assert results[2]['reward'] == 1
    
    def test_get_recent_learnings(self, loop):
        """Test getting recent learnings."""
        for i in range(10):
            loop.process_feedback("谢谢", f"action {i}")
        recent = loop.get_recent_learnings(limit=5)
        assert len(recent) == 5
    
    def test_get_recent_learnings_with_filter(self, loop):
        """Test getting recent learnings with reward filter."""
        loop.process_feedback("谢谢", "positive")
        loop.process_feedback("应该这样", "negative")
        loop.process_feedback("很好", "positive2")
        
        positive = loop.get_recent_learnings(reward_filter=1)
        assert len(positive) == 2
        assert all(r['reward'] == 1 for r in positive)
        
        negative = loop.get_recent_learnings(reward_filter=-1)
        assert len(negative) == 1
        assert negative[0]['reward'] == -1
    
    def test_get_statistics_empty(self, loop):
        """Test statistics with no learnings."""
        stats = loop.get_statistics()
        assert stats['total_learnings'] == 0
        assert stats['total_hints'] == 0
    
    def test_get_statistics_with_data(self, loop):
        """Test statistics with learnings."""
        loop.process_feedback("谢谢", "action1")
        loop.process_feedback("应该这样", "action2")
        loop.process_feedback("嗯", "action3")
        
        stats = loop.get_statistics()
        assert stats['total_learnings'] == 3
        assert stats['positive_rewards'] == 1
        assert stats['neutral_rewards'] == 1
        assert stats['negative_rewards'] == 1
        assert stats['total_hints'] >= 1
    
    def test_full_workflow(self, loop):
        """Test complete learning workflow."""
        result = loop.process_feedback("应该先检查文件", "created file", "context")
        assert result['reward'] == -1
        assert len(result['hints']) > 0
        assert result['hints'][0]['hint_type'] == 'should'
        
        recent = loop.get_recent_learnings(limit=1)
        assert len(recent) == 1
        assert recent[0]['feedback'] == "应该先检查文件"
    
    def test_persistence_across_instances(self, temp_data_dir):
        """Test that learnings persist across instances."""
        loop1 = LearningLoop(temp_data_dir)
        loop1.process_feedback("谢谢", "action1")
        
        loop2 = LearningLoop(temp_data_dir)
        stats = loop2.get_statistics()
        assert stats['total_learnings'] == 1
    
    def test_empty_feedback(self, loop):
        """Test handling empty feedback."""
        result = loop.process_feedback("", "action")
        assert result['reward'] == 0
    
    def test_whitespace_feedback(self, loop):
        """Test handling whitespace-only feedback."""
        result = loop.process_feedback("   ", "action")
        assert result['reward'] == 0
    
    def test_unicode_feedback(self, loop):
        """Test handling Unicode feedback."""
        result = loop.process_feedback("👍 很好！", "action")
        assert result['reward'] == 1
    
    def test_long_feedback(self, loop):
        """Test handling long feedback."""
        long_text = "谢谢" + "非常" * 100 + "感谢"
        result = loop.process_feedback(long_text, "action")
        assert result['reward'] == 1
    
    def test_batch_performance(self, loop):
        """Test batch processing performance."""
        import time
        feedbacks = [{'feedback': '谢谢', 'action': f'action{i}'} for i in range(100)]
        start = time.perf_counter()
        results = loop.process_batch(feedbacks)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        assert len(results) == 100
        assert elapsed_ms < 1000
    
    def test_concurrent_access(self, loop):
        """Test concurrent access safety."""
        import threading
        errors = []
        
        def add_learning(i):
            try:
                loop.process_feedback("谢谢", f"action{i}")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=add_learning, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        stats = loop.get_statistics()
        assert stats['total_learnings'] == 10
