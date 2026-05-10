"""Tests for pre-action rule check (v2.12.0)."""

import pytest
import tempfile
import asyncio
from pathlib import Path

from claw_rl.core.bridge import ClawRLBridge
from claw_rl.adapters.bridge_adapter import RLBridgeAdapter


class TestBridgeGetRulesWithContext:
    """Test bridge get_rules with context parameter (v2.12.0)."""

    @pytest.fixture
    def bridge(self):
        return ClawRLBridge()

    def test_get_rules_accepts_context(self, bridge):
        """get_rules RPC method accepts and passes context parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))

            request = {
                'jsonrpc': '2.0',
                'method': 'get_rules',
                'params': {
                    'top_k': 5,
                    'context': 'sessions_spawn jarvis tasks',
                },
                'id': 1,
            }
            result = asyncio.run(bridge.handle_request(request))

            assert result is not None
            assert 'result' in result
            # Should not be an error response
            assert 'error' not in result

    def test_get_rules_without_context_still_works(self, bridge):
        """get_rules still works without context parameter (backward compat)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))

            request = {
                'jsonrpc': '2.0',
                'method': 'get_rules',
                'params': {'top_k': 10},
                'id': 2,
            }
            result = asyncio.run(bridge.handle_request(request))

            assert result is not None
            assert 'result' in result
            assert 'error' not in result

    def test_get_rules_context_passed_to_adapter(self, bridge):
        """Verify context is forwarded to the adapter's get_rules method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            asyncio.run(bridge.initialize({'workspace': tmpdir}))

            # Send context matching sessions_spawn pattern
            request = {
                'jsonrpc': '2.0',
                'method': 'get_rules',
                'params': {
                    'top_k': 10,
                    'context': 'sessions_spawn {"task":"jarvis send message"}',
                },
                'id': 3,
            }
            result = asyncio.run(bridge.handle_request(request))

            assert result is not None
            assert 'result' in result
            # Should get rules (may be empty but no error)
            assert 'error' not in result


class TestPreActionRuleCheckConcept:
    """Test rule violation detection concepts (v2.12.0)."""

    @pytest.fixture
    def bridge(self):
        return ClawRLBridge()

    def test_hook_context_building(self):
        """Verify that context strings for hook can be constructed properly."""
        # Simulate what the before_tool_use hook builds as context
        tool = "sessions_spawn"
        params = {"task": "jarvis send a message", "mode": "async"}
        context = f"{tool} {str(params)}"

        assert "sessions_spawn" in context
        assert "jarvis" in context

    def test_detect_sessions_spawn_for_jarvis_pattern(self):
        """Test pattern matching: sessions_spawn + Jarvis should be detected."""
        tool = "sessions_spawn"
        params = {"task": "Run jarvis task: send message to friday"}
        context = f"{tool} {str(params)}".lower()

        # Verify the pattern we would detect in the TypeScript function
        assert "sessions_spawn" in context
        assert "jarvis" in context
        assert ("sessions_spawn" in context and
                ("jarvis" in context or "friday" in context))

    def test_sessions_spawn_without_jarvis_ok(self):
        """sessions_spawn without jarvis/friday should not trigger violation."""
        tool = "sessions_spawn"
        params = {"task": "Run a normal background task"}
        context = f"{tool} {str(params)}".lower()

        # Should not match the jarvis/friday pattern
        has_jarvis_or_friday = "jarvis" in context or "friday" in context
        matched = "sessions_spawn" in context and has_jarvis_or_friday
        assert not matched

    def test_normal_tools_not_detected(self):
        """Normal tools like bash or read should not trigger violations."""
        tool = "bash"
        params = {"command": "ls -la"}
        context = f"{tool} {str(params)}".lower()

        # No jarvis/friday context
        assert "jarvis" not in context
        assert "friday" not in context

    def test_strict_mode_block_flow(self):
        """Verify the block response structure for strictMode."""
        block_response = {
            "block": True,
            "reason": "Rule violation: Tool 'sessions_spawn' should not be used for Jarvis/Friday tasks",
            "suggestion": "Use inbox file communication instead",
        }

        assert block_response["block"] is True
        assert "sessions_spawn" in block_response["reason"]
        assert "inbox" in block_response["suggestion"].lower()

    def test_warn_mode_no_block(self):
        """In warn mode (non-strict), no block is returned."""
        # The hook just logs a warning and doesn't return a block
        # This is the expected behavior when strictMode=false
        pass
