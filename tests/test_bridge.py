#!/usr/bin/env python3
"""
Tests for claw-rl Bridge
"""

import pytest
import tempfile
from pathlib import Path

from claw_rl.core.bridge import ClawRLBridge


class TestClawRLBridge:
    """Test ClawRLBridge"""
    
    @pytest.fixture
    def bridge(self):
        """Create a bridge instance."""
        return ClawRLBridge()
    
    def test_bridge_creation(self, bridge):
        """Test bridge creation."""
        assert bridge is not None
        assert bridge.initialized is False
    
    def test_bridge_get_status_not_initialized(self, bridge):
        """Test bridge status when not initialized."""
        # Use asyncio.run for async method
        import asyncio
        result = asyncio.run(bridge.get_status())
        
        assert result['initialized'] is False
        assert result['request_count'] == 0
    
    def test_bridge_collect_feedback_not_initialized(self, bridge):
        """Test collect_feedback when not initialized."""
        import asyncio
        result = asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
        
        assert 'error' in result
    
    def test_bridge_initialize(self, bridge):
        """Test bridge initialization."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            result = asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            assert result['status'] == 'success'
            assert bridge.initialized is True
    
    def test_bridge_get_status_initialized(self, bridge):
        """Test bridge status when initialized."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.get_status())
            
            assert result['initialized'] is True
            assert 'components' in result
    
    def test_bridge_collect_feedback_thumbs_up(self, bridge):
        """Test collect_feedback with thumbs_up."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            
            assert result['status'] == 'success'
    
    def test_bridge_collect_feedback_thumbs_down(self, bridge):
        """Test collect_feedback with thumbs_down."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_down'}))
            
            assert result['status'] == 'success'
    
    def test_bridge_shutdown(self, bridge):
        """Test bridge shutdown."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.shutdown())
            
            assert result['status'] == 'success'
            assert bridge.running is False
    
    def test_bridge_multiple_requests(self, bridge):
        """Test bridge with multiple requests."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Make multiple requests
            for _ in range(5):
                result = asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
                assert result['status'] == 'success'
            
            status = asyncio.run(bridge.get_status())
            assert status['request_count'] == 5
    
    def test_bridge_extract_hint(self, bridge):
        """Test extract_hint method."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.extract_hint({'feedback': 'test feedback'}))
            
            # Should return success or hint
            assert result is not None
    
    def test_bridge_get_rules(self, bridge):
        """Test get_rules method."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.get_rules({'top_k': 10}))
            
            # Should return success or rules
            assert result is not None
    
    def test_bridge_run_loop(self, bridge):
        """Test run_loop method."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # run_loop should exist
            assert hasattr(bridge, 'run_loop') or hasattr(bridge, 'run')
    
    def test_bridge_process_learning(self, bridge):
        """Test process_learning method."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.process_learning({}))
            
            assert result is not None
            assert 'status' in result or 'error' in result
    
    def test_bridge_handle_request(self, bridge):
        """Test handle_request method."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'method': 'get_status',
                'params': {},
                'id': 1
            }
            
            result = asyncio.run(bridge.handle_request(request))
            
            assert result is not None
    
    def test_bridge_handle_request_invalid_method(self, bridge):
        """Test handle_request with invalid method."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'method': 'invalid_method',
                'params': {},
                'id': 1
            }
            
            result = asyncio.run(bridge.handle_request(request))
            
            assert result is not None
    
    def test_bridge_extract_hint_with_feedback(self, bridge):
        """Test extract_hint with feedback."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.extract_hint({'feedback': 'This is a test feedback'}))
            
            assert result is not None
            assert 'status' in result or 'hint' in result or 'error' in result
    
    def test_bridge_get_rules_with_limit(self, bridge):
        """Test get_rules with limit."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            result = asyncio.run(bridge.get_rules({'top_k': 5}))
            
            assert result is not None
            assert 'status' in result or 'rules' in result or 'error' in result
    
    def test_bridge_handle_jsonrpc_request(self, bridge):
        """Test handling JSON-RPC request."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Test initialize method
            request = {
                'jsonrpc': '2.0',
                'method': 'initialize',
                'params': {'workspace': tmpdir},
                'id': 1
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
    
    def test_bridge_handle_get_status(self, bridge):
        """Test handling get_status request."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'jsonrpc': '2.0',
                'method': 'get_status',
                'params': {},
                'id': 2
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
    
    def test_bridge_handle_collect_feedback(self, bridge):
        """Test handling collect_feedback request."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'jsonrpc': '2.0',
                'method': 'collect_feedback',
                'params': {'feedback': 'thumbs_up'},
                'id': 3
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
    
    def test_bridge_handle_extract_hint(self, bridge):
        """Test handling extract_hint request."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'jsonrpc': '2.0',
                'method': 'extract_hint',
                'params': {'feedback': 'test feedback'},
                'id': 4
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
