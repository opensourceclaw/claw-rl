"""
Tests for claw-rl Distributed Learning Module (v2.4.0)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from datetime import datetime


class TestSyncStatus:
    """Test SyncStatus enum"""

    def test_status_values(self):
        from claw_rl.distributed import SyncStatus
        assert SyncStatus.PENDING.value == "pending"
        assert SyncStatus.SYNCED.value == "synced"
        assert SyncStatus.CONFLICT.value == "conflict"
        assert SyncStatus.ERROR.value == "error"


class TestLearningAgent:
    """Test LearningAgent dataclass"""

    def test_creation(self):
        from claw_rl.distributed import LearningAgent
        agent = LearningAgent(agent_id="agent-1", name="Test Agent")
        assert agent.agent_id == "agent-1"
        assert agent.name == "Test Agent"


class TestSharedRule:
    """Test SharedRule dataclass"""

    def test_creation(self):
        from claw_rl.distributed import SharedRule
        rule = SharedRule(
            rule_id="rule-1",
            content="Test rule",
            source_agent="agent-1",
            timestamp=datetime.now(),
            checksum="abc123"
        )
        assert rule.rule_id == "rule-1"
        assert rule.content == "Test rule"


class TestLearningSync:
    """Test LearningSync"""

    @pytest.fixture
    def sync(self):
        import claw_rl.distributed as dist_module
        dist_module._agents = {}
        from claw_rl.distributed import get_learning_sync
        return get_learning_sync("agent-1", "Test Agent")

    def test_register_agent(self, sync):
        """Test agent registration"""
        sync.register_agent("agent-2", "Agent Two")
        stats = sync.get_agent_stats("agent-2")
        assert stats is not None
        assert stats["agent_id"] == "agent-2"

    def test_add_rule(self, sync):
        """Test adding local rule"""
        sync.add_rule("rule-1", "Test rule content")
        rules = sync.get_all_rules()
        assert "rule-1" in rules

    def test_share_rule(self, sync):
        """Test sharing rule"""
        sync.add_rule("rule-1", "Test rule")
        shared = sync.share_rule("rule-1")
        assert shared is not None
        assert shared.rule_id == "rule-1"
        assert shared.source_agent == "agent-1"

    def test_receive_rule(self, sync):
        """Test receiving shared rule"""
        # Create a shared rule
        from claw_rl.distributed import SharedRule
        shared = SharedRule(
            rule_id="rule-2",
            content="Received rule",
            source_agent="agent-2",
            timestamp=datetime.now(),
            checksum="def456"
        )

        sync.register_agent("agent-2", "Agent Two")
        status = sync.receive_rule(shared)
        assert status.value == "synced"

        rules = sync.get_all_rules()
        assert "rule-2" in rules

    def test_network_stats(self, sync):
        """Test network statistics"""
        sync.register_agent("agent-2", "Agent Two")
        stats = sync.get_network_stats()

        assert stats["total_agents"] >= 1
        assert "total_rules" in stats

    def test_find_similar_rules(self, sync):
        """Test finding similar rules"""
        sync.add_rule("rule-1", "Use defensive programming patterns")
        sync.add_rule("rule-2", "Always validate input")

        similar = sync.find_similar_rules("Defensive coding is important", threshold=0.3)
        assert len(similar) > 0
