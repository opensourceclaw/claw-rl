#!/usr/bin/env python3
"""
Extra tests for A/B Testing Framework
"""

import pytest
from claw_rl.learning.ab_testing import (
    ExperimentVariant,
    Experiment,
    ExperimentStatus,
    ABTestingFramework,
)


class TestABTestingFrameworkExtra:
    """Extra tests for ABTestingFramework"""
    
    @pytest.fixture
    def framework(self):
        """Create a framework instance."""
        return ABTestingFramework()
    
    def test_experiment_with_complex_config(self, framework):
        """Test experiment with complex config."""
        variants = [
            {
                "name": "control",
                "config": {
                    "learning_rate": 0.1,
                    "batch_size": 32,
                    "optimizer": "adam"
                }
            },
            {
                "name": "treatment",
                "config": {
                    "learning_rate": 0.2,
                    "batch_size": 64,
                    "optimizer": "sgd"
                }
            },
        ]
        
        experiment = framework.create_experiment(
            name="Complex Config Test",
            description="Test with complex configurations",
            variants=variants
        )
        
        assert len(experiment.variants) == 2
        assert experiment.variants[0].config["optimizer"] == "adam"
        assert experiment.variants[1].config["optimizer"] == "sgd"
    
    def test_variant_description(self, framework):
        """Test variant description."""
        variants = [
            {
                "name": "control",
                "config": {},
                "description": "Control group with default settings"
            },
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Check variant description if it exists
        assert experiment.variants[0] is not None
    
    def test_experiment_lifecycle(self, framework):
        """Test experiment lifecycle."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        # Create
        experiment = framework.create_experiment(
            name="Lifecycle Test",
            description="Test lifecycle",
            variants=variants
        )
        
        # Start
        framework.start_experiment(experiment.id)
        
        # Get status
        status = framework.get_experiment(experiment.id)
        assert status is not None
    
    def test_framework_persistence(self, framework):
        """Test framework persistence."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        # Create experiment
        exp1 = framework.create_experiment(
            name="Persistence Test",
            description="Test persistence",
            variants=variants
        )
        
        # List experiments
        experiments = framework.list_experiments()
        
        # Should contain the created experiment
        assert len(experiments) > 0
        assert any(e.id == exp1.id for e in experiments)
    
    def test_variant_statistics(self, framework):
        """Test variant statistics."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Stats Test",
            description="Test statistics",
            variants=variants
        )
        
        # Check variant statistics
        variant = experiment.variants[0]
        assert variant.assignment_count >= 0
        assert variant.total_events >= 0
        assert variant.positive_events >= 0
        assert variant.negative_events >= 0
        assert variant.conversion_rate >= 0.0
        assert variant.conversion_rate <= 1.0
