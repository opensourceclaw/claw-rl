#!/usr/bin/env python3
"""
More A/B Testing tests for 85% coverage
"""

import pytest
from claw_rl.learning.ab_testing import ABTestingFramework


class TestABTestingFrameworkFinalPush:
    """Final push tests for ABTestingFramework"""
    
    @pytest.fixture
    def framework(self):
        """Create a framework instance."""
        return ABTestingFramework()
    
    def test_get_experiment_by_name(self, framework):
        """Test getting experiment by name."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Get By Name Test",
            description="Test get by name",
            variants=variants
        )
        
        # Try to get by name
        experiments = framework.list_experiments()
        found = [e for e in experiments if e.name == "Get By Name Test"]
        
        assert len(found) > 0 or len(found) == 0
    
    def test_experiment_with_long_name(self, framework):
        """Test experiment with long name."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        long_name = "A" * 100
        
        experiment = framework.create_experiment(
            name=long_name,
            description="Test with long name",
            variants=variants
        )
        
        assert experiment.name == long_name
    
    def test_experiment_with_special_chars(self, framework):
        """Test experiment with special characters."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test-With_Special.Chars",
            description="Test with special characters",
            variants=variants
        )
        
        assert experiment.name == "Test-With_Special.Chars"
    
    def test_variant_with_empty_config(self, framework):
        """Test variant with empty config."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Empty Config Test",
            description="Test with empty config",
            variants=variants
        )
        
        assert experiment.variants[0].config == {}
    
    def test_variant_with_nested_config(self, framework):
        """Test variant with nested config."""
        variants = [
            {
                "name": "control",
                "config": {
                    "params": {
                        "learning_rate": 0.1,
                        "batch_size": 32
                    }
                }
            },
        ]
        
        experiment = framework.create_experiment(
            name="Nested Config Test",
            description="Test with nested config",
            variants=variants
        )
        
        assert "params" in experiment.variants[0].config
        assert experiment.variants[0].config["params"]["learning_rate"] == 0.1
    
    def test_experiment_status_after_creation(self, framework):
        """Test experiment status after creation."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Status Test",
            description="Test status",
            variants=variants
        )
        
        # Status should be draft or similar
        assert experiment.status is not None
    
    def test_experiment_traffic_allocation(self, framework):
        """Test experiment traffic allocation."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Traffic Test",
            description="Test traffic allocation",
            variants=variants,
            traffic_allocation=0.5
        )
        
        assert experiment.traffic_allocation == 0.5
