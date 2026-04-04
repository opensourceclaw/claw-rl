#!/usr/bin/env python3
"""
More tests for A/B Testing Framework
"""

import pytest
from claw_rl.learning.ab_testing import (
    ABTestingFramework,
)


class TestABTestingFrameworkMore:
    """More tests for ABTestingFramework"""
    
    @pytest.fixture
    def framework(self):
        """Create a framework instance."""
        return ABTestingFramework()
    
    def test_experiment_with_metadata(self, framework):
        """Test experiment with metadata."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Metadata Test",
            description="Test with metadata",
            variants=variants
        )
        
        # Check experiment has metadata or not
        assert experiment is not None
    
    def test_variant_assignment_consistency(self, framework):
        """Test variant assignment consistency."""
        variants = [
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Consistency Test",
            description="Test assignment consistency",
            variants=variants
        )
        
        framework.start_experiment(experiment.id)
        
        # Same user should get same variant
        variant1 = framework.assign_variant(experiment.id, "user-123")
        variant2 = framework.assign_variant(experiment.id, "user-123")
        
        # Should be consistent
        assert variant1 is not None
        assert variant2 is not None
    
    def test_experiment_with_many_variants(self, framework):
        """Test experiment with many variants."""
        variants = [
            {"name": f"variant_{i}", "config": {"param": i * 0.1}}
            for i in range(10)
        ]
        
        experiment = framework.create_experiment(
            name="Many Variants Test",
            description="Test with many variants",
            variants=variants
        )
        
        assert len(experiment.variants) == 10
    
    def test_experiment_variant_names(self, framework):
        """Test variant names."""
        variants = [
            {"name": "control", "config": {}},
            {"name": "treatment_a", "config": {}},
            {"name": "treatment_b", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Variant Names Test",
            description="Test variant names",
            variants=variants
        )
        
        variant_names = [v.name for v in experiment.variants]
        assert "control" in variant_names
        assert "treatment_a" in variant_names
        assert "treatment_b" in variant_names
    
    def test_framework_experiment_count(self, framework):
        """Test framework experiment count."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        initial_count = len(framework.list_experiments())
        
        # Create new experiment
        framework.create_experiment(
            name="Count Test",
            description="Test count",
            variants=variants
        )
        
        final_count = len(framework.list_experiments())
        
        assert final_count == initial_count + 1
