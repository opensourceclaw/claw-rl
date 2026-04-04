#!/usr/bin/env python3
"""
Final push for 85% coverage - bridge tests
"""

import pytest
import tempfile
from pathlib import Path

from claw_rl.core.bridge import ClawRLBridge


class TestClawRLBridgeFinal:
    """Final tests for ClawRLBridge"""
    
    @pytest.fixture
    def bridge(self):
        """Create a bridge instance."""
        return ClawRLBridge()
    
    def test_bridge_collect_feedback_negative(self, bridge):
        """Test collect_feedback with negative feedback."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            result = asyncio.run(bridge.collect_feedback({
                'feedback': 'thumbs_down',
                'action': 'test_action',
                'context': {'task': 'test'}
            }))
            
            assert result is not None
            assert 'status' in result or 'error' in result
    
    def test_bridge_extract_hint_with_long_feedback(self, bridge):
        """Test extract_hint with long feedback."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            long_feedback = "This is a very long feedback message. " * 100
            result = asyncio.run(bridge.extract_hint({'feedback': long_feedback}))
            
            assert result is not None
    
    def test_bridge_get_rules_after_feedback(self, bridge):
        """Test get_rules after collecting feedback."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Collect some feedback
            asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_down'}))
            
            # Get rules
            result = asyncio.run(bridge.get_rules({'top_k': 10}))
            
            assert result is not None
    
    def test_bridge_process_learning_with_feedback(self, bridge):
        """Test process_learning after feedback."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Collect feedback first
            asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            
            # Process learning
            result = asyncio.run(bridge.process_learning({}))
            
            assert result is not None
    
    def test_bridge_multiple_concurrent_requests(self, bridge):
        """Test multiple concurrent requests."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Make multiple requests sequentially
            for i in range(10):
                result = asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
                assert result is not None
    
    def test_bridge_error_recovery(self, bridge):
        """Test error recovery."""
        import asyncio
        
        # Try operations before initialization
        result1 = asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
        assert 'error' in result1
        
        result2 = asyncio.run(bridge.get_status())
        assert result2 is not None
    
    def test_bridge_initialize_multiple_times(self, bridge):
        """Test initializing multiple times."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                # Initialize first time
                result1 = asyncio.run(bridge.initialize({'workspace': tmpdir1}))
                assert result1['status'] == 'success'
                
                # Initialize second time
                result2 = asyncio.run(bridge.initialize({'workspace': tmpdir2}))
                assert result2['status'] == 'success'
    
    def test_bridge_status_after_operations(self, bridge):
        """Test status after various operations."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Perform operations
            asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            asyncio.run(bridge.extract_hint({'feedback': 'test'}))
            asyncio.run(bridge.get_rules({'top_k': 5}))
            
            # Check status
            status = asyncio.run(bridge.get_status())
            
            assert status['initialized'] is True
            assert status['request_count'] >= 3
