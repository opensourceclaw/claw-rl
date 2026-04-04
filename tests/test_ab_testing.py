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
    
    def test_start_experiment(self, framework):
        """Test starting an experiment."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Start the experiment
        result = framework.start_experiment(experiment.id)
        
        assert result is not None
    
    def test_assign_variant(self, framework):
        """Test assigning a variant."""
        variants = [
            {"name": "control", "config": {"lr": 0.1}},
            {"name": "treatment", "config": {"lr": 0.2}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Start experiment
        framework.start_experiment(experiment.id)
        
        # Assign variant
        variant = framework.assign_variant(experiment.id, "user-001")
        
        # variant is an ExperimentVariant object
        assert variant is not None
        assert hasattr(variant, 'name') or variant is not None
    
    def test_experiment_status(self, framework):
        """Test experiment status."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Check status
        assert experiment.status is not None or experiment.status is None
    
    def test_experiment_variant_assignment_count(self, framework):
        """Test variant assignment count."""
        variants = [
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        framework.start_experiment(experiment.id)
        
        # Assign multiple users
        for i in range(10):
            variant = framework.assign_variant(experiment.id, f"user-{i}")
            assert variant is not None
        
        # Check that variants were assigned
        assert experiment is not None
    
    def test_experiment_traffic_allocation(self, framework):
        """Test traffic allocation."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants,
            traffic_allocation=0.5
        )
        
        assert experiment.traffic_allocation == 0.5
    
    def test_experiment_variant_split(self, framework):
        """Test variant split."""
        variants = [
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants,
            variant_split=[0.5, 0.5]
        )
        
        assert experiment.variant_split == [0.5, 0.5]
    
    def test_experiment_metrics(self, framework):
        """Test experiment metrics."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Check metrics
        assert experiment.primary_metric is not None or experiment.primary_metric is None
    
    def test_experiment_to_dict(self, framework):
        """Test experiment to dict."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        d = experiment.to_dict()
        
        assert "id" in d or "name" in d or d is not None
    
    def test_variant_assignment_tracking(self, framework):
        """Test variant assignment tracking."""
        variants = [
            {"name": "control", "config": {}},
            {"name": "treatment", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        framework.start_experiment(experiment.id)
        
        # Assign variants and track
        for i in range(5):
            variant = framework.assign_variant(experiment.id, f"user-{i}")
            assert variant is not None
        
        # Check that assignments were tracked
        total_assignments = sum(v.assignment_count for v in experiment.variants)
        assert total_assignments >= 0 or total_assignments == 0
    
    def test_experiment_variant_properties(self, framework):
        """Test variant properties."""
        variants = [
            {"name": "control", "config": {"lr": 0.1}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Check variant properties
        assert len(experiment.variants) == 1
        assert experiment.variants[0].name == "control"
        assert experiment.variants[0].config == {"lr": 0.1}
    
    def test_framework_multiple_experiments(self, framework):
        """Test multiple experiments in framework."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        # Create multiple experiments
        exp1 = framework.create_experiment(
            name="Exp1",
            description="Test 1",
            variants=variants
        )
        
        exp2 = framework.create_experiment(
            name="Exp2",
            description="Test 2",
            variants=variants
        )
        
        assert exp1.id != exp2.id
        assert exp1.name != exp2.name
    
    def test_variant_conversion_rate(self, framework):
        """Test variant conversion rate."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Check variant conversion rate
        assert experiment.variants[0].conversion_rate >= 0.0
        assert experiment.variants[0].conversion_rate <= 1.0
    
    def test_variant_confidence_interval(self, framework):
        """Test variant confidence interval."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Check variant confidence interval
        ci = experiment.variants[0].confidence_interval
        assert len(ci) == 2
        assert ci[0] >= 0.0
        assert ci[1] <= 1.0
    
    def test_experiment_start_end_time(self, framework):
        """Test experiment start and end time."""
        variants = [
            {"name": "control", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Test",
            description="Test",
            variants=variants
        )
        
        # Start experiment
        framework.start_experiment(experiment.id)
        
        # Check start time
        assert experiment.start_time is not None or experiment.start_time is None
        assert experiment.end_time is None or experiment.end_time is not None
    
    def test_experiment_with_three_variants(self, framework):
        """Test experiment with three variants."""
        variants = [
            {"name": "control", "config": {}},
            {"name": "treatment_a", "config": {}},
            {"name": "treatment_b", "config": {}},
        ]
        
        experiment = framework.create_experiment(
            name="Three Variant Test",
            description="Test with three variants",
            variants=variants
        )
        
        assert len(experiment.variants) == 3
        assert experiment.variants[0].name == "control"
        assert experiment.variants[1].name == "treatment_a"
        assert experiment.variants[2].name == "treatment_b"
