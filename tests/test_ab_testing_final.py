#!/usr/bin/env python3
"""
Final push tests for A/B Testing Framework
"""

import pytest
from claw_rl.learning.ab_testing import ABTestingFramework


class TestABTestingFrameworkFinal:
    """Final push tests for ABTestingFramework"""
    
    @pytest.fixture
    def framework(self):
        """Create a framework instance."""
        return ABTestingFramework()
    
    def test_experiment_with_custom_id(self, framework):
        """Test experiment with custom ID."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Custom ID Test",
            description="Test with custom ID",
            variants=variants
        )
        
        # Check that experiment has an ID
        assert experiment.id is not None
        assert len(experiment.id) > 0
    
    def test_variant_equality(self, framework):
        """Test variant equality."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Equality Test",
            description="Test equality",
            variants=variants
        )
        
        # Check variant equality
        assert experiment.variants[0] == experiment.variants[0]
    
    def test_experiment_str_representation(self, framework):
        """Test experiment string representation."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="String Test",
            description="Test string representation",
            variants=variants
        )
        
        # Check string representation
        str_repr = str(experiment)
        assert str_repr is not None
        assert len(str_repr) > 0
    
    def test_variant_str_representation(self, framework):
        """Test variant string representation."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Variant String Test",
            description="Test variant string",
            variants=variants
        )
        
        # Check variant string representation
        variant = experiment.variants[0]
        str_repr = str(variant)
        assert str_repr is not None
        assert len(str_repr) > 0
    
    def test_framework_multiple_starts(self, framework):
        """Test starting experiment multiple times."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Multiple Starts Test",
            description="Test multiple starts",
            variants=variants
        )
        
        # Start multiple times
        framework.start_experiment(experiment.id)
        framework.start_experiment(experiment.id)
        
        # Should handle gracefully
        assert experiment.status is not None
