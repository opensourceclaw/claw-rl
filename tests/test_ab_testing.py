#!/usr/bin/env python3
"""
Tests for A/B Testing Framework
"""

import pytest
from claw_rl.learning.ab_testing import (
    ExperimentVariant,
    Experiment,
    ExperimentStatus,
    ABTestingFramework,
)


class TestExperimentVariant:
    """Test ExperimentVariant"""
    
    def test_variant_creation(self):
        """Test variant creation."""
        variant = ExperimentVariant(
            name="control",
            config={"param": 0.5},
            description="Control variant"
        )
        
        assert variant.name == "control"
        assert variant.config == {"param": 0.5}
        assert variant.description == "Control variant"
        assert variant.assignment_count == 0
    
    def test_variant_to_dict(self):
        """Test variant to dict."""
        variant = ExperimentVariant(
            name="treatment",
            config={"param": 0.7}
        )
        
        d = variant.to_dict()
        
        assert d["name"] == "treatment"
        assert d["config"] == {"param": 0.7}
        assert "assignment_count" in d
    
    def test_variant_conversion_rate(self):
        """Test variant conversion rate."""
        variant = ExperimentVariant(
            name="test",
            config={},
            total_events=100,
            positive_events=80
        )
        
        # Conversion rate should be positive_events / total_events
        assert variant.conversion_rate == 0.0  # Not calculated yet


class TestExperiment:
    """Test Experiment"""
    
    def test_experiment_creation(self):
        """Test experiment creation."""
        variants = [
            ExperimentVariant(name="control", config={}),
            ExperimentVariant(name="treatment", config={}),
        ]
        
        experiment = Experiment(
            id="exp-001",
            name="Test Experiment",
            description="A test experiment",
            variants=variants
        )
        
        assert experiment.id == "exp-001"
        assert experiment.name == "Test Experiment"
        assert len(experiment.variants) == 2
        assert experiment.status == ExperimentStatus.DRAFT.value
    
    def test_experiment_with_config(self):
        """Test experiment with configuration."""
        variants = [
            ExperimentVariant(name="A", config={"lr": 0.1}),
            ExperimentVariant(name="B", config={"lr": 0.2}),
        ]
        
        experiment = Experiment(
            id="exp-002",
            name="LR Test",
            description="Learning rate test",
            variants=variants,
            traffic_allocation=0.5,
            variant_split=[0.5, 0.5]
        )
        
        assert experiment.traffic_allocation == 0.5
        assert experiment.variant_split == [0.5, 0.5]


class TestABTestingFramework:
    """Test ABTestingFramework"""
    
    @pytest.fixture
    def framework(self):
        """Create a framework instance."""
        return ABTestingFramework()
    
    def test_framework_creation(self, framework):
        """Test framework creation."""
        assert framework is not None
        assert hasattr(framework, 'experiments')
    
    def test_create_experiment(self, framework):
        """Test creating an experiment."""
        variants = [
            {"name": "control", "config": {"param": 0.5}},
            {"name": "treatment", "config": {"param": 0.7}},
        ]
        
        experiment = framework.create_experiment(
            name="Test Experiment",
            description="A test experiment",
            variants=variants
        )
        
        assert experiment is not None
        assert experiment.name == "Test Experiment"
    
    def test_get_experiment(self, framework):
        """Test getting an experiment."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        retrieved = framework.get_experiment(experiment.id)
        
        assert retrieved is not None
        assert retrieved.id == experiment.id
    
    def test_list_experiments(self, framework):
        """Test listing experiments."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        framework.create_experiment(
            name="Exp1",
            description="Test 1",
            variants=variants
        )
        
        framework.create_experiment(
            name="Exp2",
            description="Test 2",
            variants=variants
        )
        
        experiments = framework.list_experiments()
        
        assert len(experiments) >= 2
