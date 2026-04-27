"""
Distributed Learning Module for claw-rl v2.4.0

提供多 Agent 学习同步和规则共享机制。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json


class SyncStatus(Enum):
    """同步状态"""
    PENDING = "pending"
    SYNCED = "synced"
    CONFLICT = "conflict"
    ERROR = "error"


@dataclass
class LearningAgent:
    """学习 Agent"""
    agent_id: str
    name: str
    last_sync: Optional[datetime] = None
    rules_shared: int = 0
    rules_received: int = 0


@dataclass
class SharedRule:
    """共享规则"""
    rule_id: str
    content: str
    source_agent: str
    timestamp: datetime
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class LearningSync:
    """
    分布式学习同步器

    支持多 Agent 之间的规则共享和学习同步。
    """

    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self._agents: Dict[str, LearningAgent] = {}
        self._shared_rules: Dict[str, SharedRule] = {}
        self._local_rules: Dict[str, Dict[str, Any]] = {}

        # Register self
        self.register_agent(agent_id, agent_name)

    def register_agent(self, agent_id: str, agent_name: str):
        """注册 Agent"""
        if agent_id not in self._agents:
            self._agents[agent_id] = LearningAgent(
                agent_id=agent_id,
                name=agent_name
            )

    def add_rule(
        self,
        rule_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加本地规则"""
        self._local_rules[rule_id] = {
            'content': content,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'version': 1
        }

    def share_rule(self, rule_id: str) -> Optional[SharedRule]:
        """共享规则到网络"""
        if rule_id not in self._local_rules:
            return None

        rule_data = self._local_rules[rule_id]
        content = rule_data['content']

        # Calculate checksum
        checksum = hashlib.sha256(content.encode()).hexdigest()[:16]

        shared = SharedRule(
            rule_id=rule_id,
            content=content,
            source_agent=self.agent_id,
            timestamp=datetime.now(),
            checksum=checksum,
            metadata=rule_data.get('metadata', {})
        )

        self._shared_rules[rule_id] = shared

        # Update agent stats
        self._agents[self.agent_id].rules_shared += 1
        self._agents[self.agent_id].last_sync = datetime.now()

        return shared

    def receive_rule(self, shared_rule: SharedRule) -> SyncStatus:
        """接收共享规则"""
        rule_id = shared_rule.rule_id

        # Check for conflict
        if rule_id in self._local_rules:
            local = self._local_rules[rule_id]
            local_checksum = hashlib.sha256(local['content'].encode()).hexdigest()[:16]

            if local_checksum != shared_rule.checksum:
                # Conflict detected - keep both with version increment
                self._local_rules[rule_id]['content'] = shared_rule.content
                self._local_rules[rule_id]['version'] = local.get('version', 1) + 1
                return SyncStatus.CONFLICT

        # No conflict - add/update rule
        self._local_rules[rule_id] = {
            'content': shared_rule.content,
            'metadata': shared_rule.metadata,
            'source': shared_rule.source_agent,
            'created_at': shared_rule.timestamp.isoformat(),
            'version': 1
        }

        # Update stats
        self._agents[self.agent_id].rules_received += 1
        self._agents[shared_rule.source_agent].last_sync = datetime.now()

        return SyncStatus.SYNCED

    def get_all_rules(self) -> Dict[str, Dict[str, Any]]:
        """获取所有规则"""
        return self._local_rules.copy()

    def get_shared_rules(self) -> List[SharedRule]:
        """获取已共享的规则"""
        return list(self._shared_rules.values())

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 统计"""
        agent = self._agents.get(agent_id)
        if not agent:
            return None

        return {
            'agent_id': agent.agent_id,
            'name': agent.name,
            'last_sync': agent.last_sync.isoformat() if agent.last_sync else None,
            'rules_shared': agent.rules_shared,
            'rules_received': agent.rules_received
        }

    def get_network_stats(self) -> Dict[str, Any]:
        """获取网络统计"""
        return {
            'total_agents': len(self._agents),
            'total_rules': len(self._local_rules),
            'shared_rules': len(self._shared_rules),
            'agents': [
                self.get_agent_stats(aid)
                for aid in self._agents.keys()
            ]
        }

    def find_similar_rules(self, content: str, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """查找相似规则 (简单文本匹配)"""
        content_lower = content.lower()
        similar = []

        for rule_id, rule_data in self._local_rules.items():
            rule_content = rule_data.get('content', '').lower()

            # Simple word overlap
            content_words = set(content_lower.split())
            rule_words = set(rule_content.split())

            if content_words and rule_words:
                overlap = len(content_words & rule_words) / len(content_words | rule_words)
                if overlap >= threshold:
                    similar.append({
                        'rule_id': rule_id,
                        'similarity': overlap,
                        'content': rule_data.get('content', '')
                    })

        return sorted(similar, key=lambda x: x['similarity'], reverse=True)


# Global instance per agent
_agents: Dict[str, 'LearningSync'] = {}


def get_learning_sync(agent_id: str, agent_name: str = "default") -> LearningSync:
    """获取指定 Agent 的学习同步器"""
    if agent_id not in _agents:
        _agents[agent_id] = LearningSync(agent_id, agent_name)
    return _agents[agent_id]
