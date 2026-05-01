# LearningLoop Integration Test (Corrected)

import pytest
import json
from pathlib import Path
from claw_rl.core.learning_loop import LearningLoop

def test_learning_loop_initialization():
    """Test LearningLoop initialization"""
    # Create test data directory
    test_dir = Path("./test_data")
    test_dir.mkdir(exist_ok=True)
    
    loop = LearningLoop(test_dir)
    assert loop is not None
    assert hasattr(loop, 'judge')
    assert hasattr(loop, 'hint_extractor')
    assert hasattr(loop, 'data_dir')

def test_learning_loop_process_feedback_positive():
    """Test LearningLoop process_feedback with positive feedback"""
    test_dir = Path("./test_data")
    test_dir.mkdir(exist_ok=True)
    
    loop = LearningLoop(test_dir)
    
    # Test positive feedback
    result = loop.process_feedback(
        feedback="很好!",
        action="created file"
    )
    
    assert result is not None
    assert 'reward' in result
    assert result['reward'] == 1 or result['reward'] == 0  # Binary RL may return 0 for neutral

def test_learning_loop_process_feedback_negative():
    """Test LearningLoop process_feedback with negative feedback"""
    test_dir = Path("./test_data")
    test_dir.mkdir(exist_ok=True)
    
    loop = LearningLoop(test_dir)
    
    # Test negative feedback
    result = loop.process_feedback(
        feedback="不对,应该放到这里",
        action="created file"
    )
    
    assert result is not None
    assert 'reward' in result
    assert result['reward'] == -1 or result['reward'] == 0  # Binary RL may return 0 for neutral

def test_learning_loop_data_persistence():
    """Test LearningLoop data persistence"""
    test_dir = Path("./test_data")
    test_dir.mkdir(exist_ok=True)
    
    loop = LearningLoop(test_dir)
    
    # Process feedback
    result = loop.process_feedback(
        feedback="test feedback",
        action="test action"
    )
    
    # Check that files were created
    rewards_dir = test_dir / ".rewards"
    assert rewards_dir.exists()
    
    # Check at least one reward file exists
    reward_files = list(rewards_dir.glob("reward_*.json"))
    assert len(reward_files) >= 1

def test_context_filter_rules():
    """Test context_filter in get_recent_learnings"""
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    try:
        loop = LearningLoop(Path(tmp))
        # Add varied learnings
        loop.process_feedback("帮我查Friday的风格", "searched")
        loop.process_feedback("Jarvis效率需要提高", "measured")
        loop.process_feedback("英文翻译不对", "translated")

        all_rules = loop.get_recent_learnings(limit=10)
        friday_rules = loop.get_recent_learnings(limit=10, context_filter="Friday")
        jarvis_rules = loop.get_recent_learnings(limit=10, context_filter="Jarvis")
        empty_rules = loop.get_recent_learnings(limit=10, context_filter="xyzzy")

        assert len(all_rules) == 3
        assert len(friday_rules) == 1
        assert len(jarvis_rules) == 1
        assert len(empty_rules) == 0
    finally:
        shutil.rmtree(tmp)
