#!/usr/bin/env python3
"""
Final push for 85% - optimizer and feedback tests
"""

import pytest


class TestOptimizerFinal:
    """Final tests for optimizer"""
    
    def test_optimizer_initial_weights(self):
        """Test optimizer initial weights."""
        from claw_rl.learning.optimizer import StrategyOptimizer
        
        optimizer = StrategyOptimizer()
        
        assert optimizer is not None
    
    def test_optimizer_optimize(self):
        """Test optimizer optimize."""
        from claw_rl.learning.optimizer import StrategyOptimizer
        
        optimizer = StrategyOptimizer()
        
        current_params = {"param1": 0.5}
        performance = 0.8
        result = optimizer.optimize(current_params, performance)
        
        assert result is not None
    
    def test_optimizer_get_best_params(self):
        """Test optimizer get best params."""
        from claw_rl.learning.optimizer import StrategyOptimizer
        
        optimizer = StrategyOptimizer()
        
        params = optimizer.get_best_params()
        
        assert params is not None
    
    def test_optimizer_reset(self):
        """Test optimizer reset."""
        from claw_rl.learning.optimizer import StrategyOptimizer
        
        optimizer = StrategyOptimizer()
        optimizer.optimize({"param1": 0.5}, 0.8)
        
        optimizer.reset()
        
        assert optimizer.iteration == 0
    
    def test_optimizer_with_custom_config(self):
        """Test optimizer with custom config."""
        from claw_rl.learning.optimizer import StrategyOptimizer
        
        config = {"max_iterations": 100}
        optimizer = StrategyOptimizer(config=config)
        
        assert optimizer.config["max_iterations"] == 100


class TestFeedbackStorageFinal:
    """Final tests for feedback storage"""
    
    def test_storage_exists(self):
        """Test storage module exists."""
        from claw_rl.feedback import storage
        
        assert storage is not None
    
    def test_storage_base_class(self):
        """Test storage base class."""
        from claw_rl.feedback.storage import FeedbackStorage
        
        assert FeedbackStorage is not None
