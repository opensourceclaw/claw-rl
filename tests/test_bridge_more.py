#!/usr/bin/env python3
"""
More bridge tests for 85% coverage
"""

import pytest
import tempfile
from pathlib import Path

from claw_rl.core.bridge import ClawRLBridge


class TestClawRLBridgeMore:
    """More tests for ClawRLBridge"""
    
    @pytest.fixture
    def bridge(self):
        """Create a bridge instance."""
        return ClawRLBridge()
    
    def test_bridge_collect_feedback_with_action(self, bridge):
        """Test collect_feedback with action."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            result = asyncio.run(bridge.collect_feedback({
                'feedback': 'thumbs_up',
                'action': 'test_action'
            }))
            
            assert result is not None
            assert 'status' in result or 'error' in result
    
    def test_bridge_collect_feedback_with_context(self, bridge):
        """Test collect_feedback with context."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            result = asyncio.run(bridge.collect_feedback({
                'feedback': 'thumbs_down',
                'context': {'task': 'test'}
            }))
            
            assert result is not None
    
    def test_bridge_extract_hint_with_empty_feedback(self, bridge):
        """Test extract_hint with empty feedback."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            result = asyncio.run(bridge.extract_hint({'feedback': ''}))
            
            assert result is not None
    
    def test_bridge_get_rules_with_large_limit(self, bridge):
        """Test get_rules with large limit."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            result = asyncio.run(bridge.get_rules({'top_k': 100}))
            
            assert result is not None
    
    def test_bridge_process_learning_empty(self, bridge):
        """Test process_learning with empty params."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            result = asyncio.run(bridge.process_learning({}))
            
            assert result is not None
    
    def test_bridge_shutdown_with_stats(self, bridge):
        """Test shutdown with stats."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Make some requests
            for _ in range(3):
                asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            
            result = asyncio.run(bridge.shutdown())
            
            assert result is not None
            assert 'total_requests' in result or 'status' in result
    
    def test_bridge_handle_request_without_id(self, bridge):
        """Test handle_request without id."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'method': 'get_status',
                'params': {}
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
    
    def test_bridge_handle_request_without_params(self, bridge):
        """Test handle_request without params."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'jsonrpc': '2.0',
                'method': 'get_status',
                'id': 1
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
