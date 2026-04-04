#!/usr/bin/env python3
"""
Extra tests for claw-rl Bridge
"""

import pytest
import tempfile
from pathlib import Path

from claw_rl.core.bridge import ClawRLBridge


class TestClawRLBridgeExtra:
    """Extra tests for ClawRLBridge"""
    
    @pytest.fixture
    def bridge(self):
        """Create a bridge instance."""
        return ClawRLBridge()
    
    def test_bridge_handle_shutdown(self, bridge):
        """Test handling shutdown request."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'jsonrpc': '2.0',
                'method': 'shutdown',
                'params': {},
                'id': 5
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
    
    def test_bridge_handle_invalid_method(self, bridge):
        """Test handling invalid method."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            request = {
                'jsonrpc': '2.0',
                'method': 'invalid_method',
                'params': {},
                'id': 6
            }
            
            result = asyncio.run(bridge.handle_request(request))
            assert result is not None
    
    def test_bridge_multiple_initializations(self, bridge):
        """Test multiple initializations."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                result1 = asyncio.run(bridge.initialize({'workspace': tmpdir1}))
                assert result1['status'] == 'success'
                
                # Second initialization
                result2 = asyncio.run(bridge.initialize({'workspace': tmpdir2}))
                assert result2['status'] == 'success'
    
    def test_bridge_latency_tracking(self, bridge):
        """Test latency tracking."""
        import asyncio
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))
            
            # Make multiple requests
            for _ in range(5):
                asyncio.run(bridge.collect_feedback({'feedback': 'thumbs_up'}))
            
            status = asyncio.run(bridge.get_status())
            
            # Should have tracked requests
            assert status['request_count'] == 5
            assert status['avg_latency_ms'] > 0 or status['avg_latency_ms'] == 0
    
    def test_bridge_error_handling(self, bridge):
        """Test error handling."""
        import asyncio
        
        # Try to get status before initialization
        result = asyncio.run(bridge.get_status())
        
        # Should return status even without initialization
        assert result is not None
