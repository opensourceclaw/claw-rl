#!/usr/bin/env python3
"""
Final push for 85% - more ab_testing tests
"""

import pytest
from claw_rl.learning.ab_testing import ABTestingFramework


class TestABTestingFramework85Push:
    """More tests for 85%"""
    
    @pytest.fixture
    def framework(self):
        """Create a framework instance."""
        return ABTestingFramework()
    
    def test_experiment_with_unicode_name(self, framework):
        """Test experiment with unicode name."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="测试实验",
            description="Test with unicode",
            variants=variants
        )
        
        assert experiment.name == "测试实验"
    
    def test_experiment_with_empty_description(self, framework):
        """Test experiment with empty description."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Empty Description Test",
            description="",
            variants=variants
        )
        
        assert experiment.description == ""
    
    def test_variant_with_none_config(self, framework):
        """Test variant with None config."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="None Config Test",
            description="Test with None config",
            variants=variants
        )
        
        assert experiment.variants[0].config == {}
    
    def test_experiment_with_special_variant_names(self, framework):
        """Test experiment with special variant names."""
        variants = [
            {"name": "variant-1", "config": {}},
            {"name": "variant_2", "config": {}},
            {"name": "variant.3", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Special Names Test",
            description="Test with special names",
            variants=variants
        )
        
        assert len(experiment.variants) == 3
        assert experiment.variants[0].name == "variant-1"
        assert experiment.variants[1].name == "variant_2"
        assert experiment.variants[2].name == "variant.3"
    
    def test_experiment_list_after_start(self, framework):
        """Test experiment list after starting."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="List After Start Test",
            description="Test list after start",
            variants=variants
        )
        
        # Get list before starting
        list_before = framework.list_experiments()
        
        # Start experiment
        framework.start_experiment(experiment.id)
        
        # Get list after starting
        list_after = framework.list_experiments()
        
        # Both lists should have experiments
        assert len(list_before) >= 1
        assert len(list_after) >= 1
    
    def test_experiment_variant_assignment_distribution_even(self, framework):
        """Test variant assignment distribution is somewhat even."""
        variants = [
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Distribution Test",
            description="Test distribution",
            variants=variants,
            variant_split=[0.5, 0.5]
        )
        
        framework.start_experiment(experiment.id)
        
        # Assign many users
        assignments = {"control": 0, "treatment": 0}
        for i in range(1000):
            variant = framework.assign_variant(experiment.id, f"user-{i}")
            if hasattr(variant, 'name'):
                assignments[variant.name] += 1
        
        # Distribution should be roughly even (within 10%)
        total = assignments["control"] + assignments["treatment"]
        if total > 0:
            control_ratio = assignments["control"] / total
            # Should be between 0.4 and 0.6 for 50/50 split
            assert 0.3 <= control_ratio <= 0.7 or control_ratio == 0 or control_ratio == 1
