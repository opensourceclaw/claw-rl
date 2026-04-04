#!/usr/bin/env python3
"""
Quick push tests for 85% coverage
"""

import pytest
import tempfile
from pathlib import Path

from claw_rl.core.bridge import ClawRLBridge


class TestClawRLBridgeQuickPush:
    """Quick push tests for bridge"""
    
    @pytest.fixture
    def bridge(self):
        """Create a bridge instance."""
        return ClawRLBridge()
    
    def test_bridge_config_initialization(self, bridge):
        """Test bridge initialization with config."""
        config = {"workspace": "/tmp/test"}
        bridge_with_config = ClawRLBridge(config=config)
        
        assert bridge_with_config.config == config
    
    def test_bridge_request_count_tracking(self, bridge):
        """Test request count tracking."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Make requests
            for i in range(5):
                asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            
            status = asyncio.run(bridge.get_status())
            
            assert status['request_count'] == 5
    
    def test_bridge_total_latency_tracking(self, bridge):
        """Test total latency tracking."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Make a request
            asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            
            status = asyncio.run(bridge.get_status())
            
            assert status['avg_latency_ms'] >= 0
    
    def test_bridge_initialized_flag(self, bridge):
        """Test initialized flag."""
        assert bridge.initialized is False
        
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            assert bridge.initialized is True
    
    def test_bridge_workspace_storage(self, bridge):
        """Test workspace storage."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            assert bridge.workspace == tmpdir


class TestABTestingQuickPush:
    """Quick push tests for ab_testing"""
    
    @pytest.fixture
    def framework(self):
        """Create a framework instance."""
        from claw_rl.learning.ab_testing import ABTestingFramework
        return ABTestingFramework()
    
    def test_experiment_id_generation(self, framework):
        """Test experiment ID generation."""
        from claw_rl.learning.ab_testing import ExperimentVariant
        variants = [ExperimentVariant(name="control", config={})]
        
        exp1 = framework.create_experiment("Test1", [v.__dict__ for v in variants])
        exp2 = framework.create_experiment("Test2", [v.__dict__ for v in variants])
        
        assert exp1.id != exp2.id
        assert len(exp1.id) > 0
        assert len(exp2.id) > 0
    
    def test_variant_conversion_rate_calculation(self, framework):
        """Test variant conversion rate calculation."""
        variants = [{"name": "control", "config": {}}]
        
        exp = framework.create_experiment("Test", variants)
        
        # Initial conversion rate should be 0
        assert exp.variants[0].conversion_rate == 0.0
    
    def test_experiment_to_dict_structure(self, framework):
        """Test experiment to_dict structure."""
        variants = [{"name": "control", "config": {}}]
        
        exp = framework.create_experiment("Test", variants)
        
        d = exp.to_dict()
        
        assert "id" in d
        assert "name" in d
        assert "description" in d
        assert "variants" in d
        assert "status" in d
    
    def test_framework_experiment_uniqueness(self, framework):
        """Test that experiments are unique."""
        experiments = []
        for i in range(5):
            variants = [{"name": f"control_{i}", "config": {}}]
            exp = framework.create_experiment(f"Test{i}", variants)
            experiments.append(exp)
        
        # All IDs should be unique
        ids = [e.id for e in experiments]
        assert len(ids) == len(set(ids))
    
    def test_variant_initial_counts(self, framework):
        """Test variant initial counts."""
        variants = [{"name": "control", "config": {}}]
        
        exp = framework.create_experiment("Test", variants)
        
        assert exp.variants[0].assignment_count == 0
        assert exp.variants[0].total_events == 0
        assert exp.variants[0].positive_events == 0
        assert exp.variants[0].negative_events == 0
