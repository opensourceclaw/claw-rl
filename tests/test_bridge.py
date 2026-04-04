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
