# Copyright 2026 Peter Cheng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
claw-rl Agent Signal Collector

Collects learning signals from agent decisions.
Framework-agnostic: Works with any agent system.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime
import json


@dataclass
class AgentSignal:
    """
    Learning signal from an agent decision
    
    Attributes:
        agent_id: Agent identifier (e.g., "tech_agent", "life_agent", or custom)
        pillar: Agent category (work, life, wealth, or custom)
        decision_type: Type of decision (code_generation, advice, analysis, etc.)
        action: Action taken by agent
        outcome: Outcome (user_accepted, user_rejected, partial, timeout)
        satisfaction: User satisfaction score (0.0 - 1.0)
        context: Additional context data
        timestamp: ISO timestamp
        session_id: Session identifier
    """
    agent_id: str
    pillar: str
    decision_type: str
    action: str
    outcome: str
    satisfaction: float
    context: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'agent_id': self.agent_id,
            'pillar': self.pillar,
            'decision_type': self.decision_type,
            'action': self.action,
            'outcome': self.outcome,
            'satisfaction': self.satisfaction,
            'context': self.context,
            'timestamp': self.timestamp,
            'session_id': self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentSignal':
        """Create from dictionary"""
        return cls(
            agent_id=data['agent_id'],
            pillar=data['pillar'],
            decision_type=data['decision_type'],
            action=data['action'],
            outcome=data['outcome'],
            satisfaction=data['satisfaction'],
            context=data.get('context', {}),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            session_id=data.get('session_id', '')
        )
    
    def to_reward(self) -> int:
        """
        Convert signal to reward value
        
        Returns:
            int: Reward (+1, -1, or 0)
        """
        # Map satisfaction to reward
        if self.satisfaction >= 0.7:
            return +1
        elif self.satisfaction <= 0.3:
            return -1
        return 0
    
    def to_hint(self) -> Optional[str]:
        """
        Extract hint from signal
        
        Returns:
            Optional[str]: Hint if applicable, None otherwise
        """
        # Extract hint from rejection or low satisfaction
        if self.outcome == 'user_rejected' or self.satisfaction <= 0.3:
            return f"Agent {self.agent_id} {self.decision_type} was rejected"
        
        # Extract hint from partial outcome
        if self.outcome == 'partial':
            return f"Agent {self.agent_id} {self.decision_type} needs improvement"
        
        return None


class AgentSignalCollector:
    """
    Collects and processes agent signals
    
    Usage:
        collector = AgentSignalCollector()
        
        # Record agent decision
        signal = collector.record(
            agent_id="stark_tech",
            pillar="work",
            decision_type="code_generation",
            action="Generated REST API endpoint",
            outcome="user_accepted",
            satisfaction=0.9,
            context={"task": "Create API"}
        )
        
        # Get statistics
        stats = collector.get_statistics()
    """
    
    # Example pillar definitions (can be customized)
    # Users can override PILLARS for their specific agent system
    PILLARS = {
        'work': ['tech_agent', 'business_agent', 'economic_agent'],
        'life': ['body_agent', 'mind_agent', 'relationship_agent'],
        'wealth': ['asset_agent', 'investment_agent', 'risk_agent']
    }
    
    # Decision types
    DECISION_TYPES = [
        'code_generation',
        'code_review',
        'advice',
        'analysis',
        'planning',
        'research',
        'recommendation',
        'execution',
        'coordination'
    ]
    
    # Outcomes
    OUTCOMES = [
        'user_accepted',
        'user_rejected',
        'partial',
        'timeout',
        'error'
    ]
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Signal Collector
        
        Args:
            data_dir: Optional custom data directory
        """
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        self.signals_dir = self.data_dir / 'agent_signals'
        self.signals_dir.mkdir(parents=True, exist_ok=True)
    
    def record(
        self,
        agent_id: str,
        pillar: str,
        decision_type: str,
        action: str,
        outcome: str,
        satisfaction: float,
        context: Optional[Dict] = None,
        session_id: str = ""
    ) -> AgentSignal:
        """
        Record an agent decision signal
        
        Args:
            agent_id: Agent identifier
            pillar: Agent pillar (work, life, wealth)
            decision_type: Type of decision
            action: Action taken
            outcome: Outcome
            satisfaction: Satisfaction score (0.0 - 1.0)
            context: Additional context
            session_id: Session identifier
            
        Returns:
            AgentSignal: Recorded signal
        """
        signal = AgentSignal(
            agent_id=agent_id,
            pillar=pillar,
            decision_type=decision_type,
            action=action,
            outcome=outcome,
            satisfaction=satisfaction,
            context=context or {},
            session_id=session_id
        )
        
        # Save signal
        self._save_signal(signal)
        
        return signal
    
    def _save_signal(self, signal: AgentSignal) -> None:
        """Save signal to file"""
        today = datetime.now().strftime('%Y-%m-%d')
        signals_file = self.signals_dir / f'{today}.jsonl'
        
        with open(signals_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(signal.to_dict(), ensure_ascii=False) + '\n')
    
    def get_signals(
        self,
        agent_id: Optional[str] = None,
        pillar: Optional[str] = None,
        decision_type: Optional[str] = None,
        days: int = 7,
        limit: int = 100
    ) -> List[AgentSignal]:
        """
        Get signals with optional filters
        
        Args:
            agent_id: Filter by agent ID
            pillar: Filter by pillar
            decision_type: Filter by decision type
            days: Number of days to look back
            limit: Maximum signals to return
            
        Returns:
            List[AgentSignal]: Filtered signals
        """
        signals = []
        cutoff = datetime.now() - timedelta(days=days) if 'timedelta' in dir() else None
        
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        # Read signals from files
        for signals_file in sorted(self.signals_dir.glob('*.jsonl'), reverse=True):
            try:
                # Parse date from filename
                file_date = datetime.strptime(signals_file.stem, '%Y-%m-%d')
                if file_date < cutoff:
                    continue
                
                # Read signals
                with open(signals_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if len(signals) >= limit:
                            break
                        
                        data = json.loads(line)
                        signal = AgentSignal.from_dict(data)
                        
                        # Apply filters
                        if agent_id and signal.agent_id != agent_id:
                            continue
                        if pillar and signal.pillar != pillar:
                            continue
                        if decision_type and signal.decision_type != decision_type:
                            continue
                        
                        signals.append(signal)
                
                if len(signals) >= limit:
                    break
                    
            except (ValueError, json.JSONDecodeError):
                continue
        
        return signals
    
    def get_statistics(self, days: int = 7) -> Dict:
        """
        Get signal statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict: Statistics
        """
        signals = self.get_signals(days=days, limit=10000)
        
        if not signals:
            return {
                'total_signals': 0,
                'by_agent': {},
                'by_pillar': {},
                'by_decision_type': {},
                'by_outcome': {},
                'avg_satisfaction': 0.0,
                'acceptance_rate': 0.0
            }
        
        stats = {
            'total_signals': len(signals),
            'by_agent': {},
            'by_pillar': {},
            'by_decision_type': {},
            'by_outcome': {},
            'avg_satisfaction': 0.0,
            'acceptance_rate': 0.0
        }
        
        # Count by dimensions
        for signal in signals:
            stats['by_agent'][signal.agent_id] = stats['by_agent'].get(signal.agent_id, 0) + 1
            stats['by_pillar'][signal.pillar] = stats['by_pillar'].get(signal.pillar, 0) + 1
            stats['by_decision_type'][signal.decision_type] = stats['by_decision_type'].get(signal.decision_type, 0) + 1
            stats['by_outcome'][signal.outcome] = stats['by_outcome'].get(signal.outcome, 0) + 1
        
        # Calculate averages
        stats['avg_satisfaction'] = sum(s.satisfaction for s in signals) / len(signals)
        stats['acceptance_rate'] = stats['by_outcome'].get('user_accepted', 0) / len(signals)
        
        return stats
    
    def get_top_agents(self, days: int = 7, limit: int = 5) -> List[Dict]:
        """
        Get top performing agents
        
        Args:
            days: Number of days to analyze
            limit: Maximum agents to return
            
        Returns:
            List[Dict]: Top agents with stats
        """
        signals = self.get_signals(days=days, limit=10000)
        
        # Group by agent
        agent_signals = {}
        for signal in signals:
            if signal.agent_id not in agent_signals:
                agent_signals[signal.agent_id] = []
            agent_signals[signal.agent_id].append(signal)
        
        # Calculate stats per agent
        agent_stats = []
        for agent_id, agent_signal_list in agent_signals.items():
            avg_satisfaction = sum(s.satisfaction for s in agent_signal_list) / len(agent_signal_list)
            acceptance_rate = sum(1 for s in agent_signal_list if s.outcome == 'user_accepted') / len(agent_signal_list)
            
            agent_stats.append({
                'agent_id': agent_id,
                'total_decisions': len(agent_signal_list),
                'avg_satisfaction': avg_satisfaction,
                'acceptance_rate': acceptance_rate
            })
        
        # Sort by satisfaction
        agent_stats.sort(key=lambda x: x['avg_satisfaction'], reverse=True)
        
        return agent_stats[:limit]
    
    def export_to_learning(self, days: int = 7) -> Dict:
        """
        Export signals to learning format
        
        Args:
            days: Number of days to export
            
        Returns:
            Dict: Learning data
        """
        signals = self.get_signals(days=days, limit=10000)
        
        rewards = []
        hints = []
        
        for signal in signals:
            # Convert to reward
            reward = signal.to_reward()
            if reward != 0:
                rewards.append({
                    'timestamp': signal.timestamp,
                    'source': 'agent',
                    'agent_id': signal.agent_id,
                    'action': signal.action,
                    'reward': reward
                })
            
            # Extract hint
            hint = signal.to_hint()
            if hint:
                hints.append({
                    'timestamp': signal.timestamp,
                    'source': 'agent',
                    'agent_id': signal.agent_id,
                    'hint': hint
                })
        
        return {
            'rewards': rewards,
            'hints': hints,
            'total_signals': len(signals),
            'period_days': days
        }
