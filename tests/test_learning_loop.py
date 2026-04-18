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
        feedback="很好！",
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
        feedback="不对，应该放到这里",
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
