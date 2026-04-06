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
Tests for claw-rl Agent Signal Collector
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import json

from claw_rl.agents.signal_collector import AgentSignal, AgentSignalCollector


class TestAgentSignal:
    """Tests for AgentSignal"""
    
    def test_create_signal(self):
        """Test creating an agent signal"""
        signal = AgentSignal(
            agent_id="stark_tech",
            pillar="work",
            decision_type="code_generation",
            action="Generated REST API endpoint",
            outcome="user_accepted",
            satisfaction=0.9
        )
        
        assert signal.agent_id == "stark_tech"
        assert signal.pillar == "work"
        assert signal.decision_type == "code_generation"
        assert signal.action == "Generated REST API endpoint"
        assert signal.outcome == "user_accepted"
        assert signal.satisfaction == 0.9
    
    def test_signal_to_dict(self):
        """Test converting signal to dict"""
        signal = AgentSignal(
            agent_id="pepper_life",
            pillar="life",
            decision_type="advice",
            action="Provided health recommendation",
            outcome="user_accepted",
            satisfaction=0.85,
            context={"task": "health_check"},
            session_id="session_001"
        )
        
        result = signal.to_dict()
        
        assert result['agent_id'] == "pepper_life"
        assert result['pillar'] == "life"
        assert result['decision_type'] == "advice"
        assert result['satisfaction'] == 0.85
        assert result['context'] == {"task": "health_check"}
        assert result['session_id'] == "session_001"
    
    def test_signal_from_dict(self):
        """Test creating signal from dict"""
        data = {
            'agent_id': 'happy_wealth',
            'pillar': 'wealth',
            'decision_type': 'analysis',
            'action': 'Analyzed portfolio',
            'outcome': 'partial',
            'satisfaction': 0.6,
            'context': {'stocks': ['AAPL', 'GOOGL']},
            'timestamp': '2026-03-29T10:00:00',
            'session_id': 'session_002'
        }
        
        signal = AgentSignal.from_dict(data)
        
        assert signal.agent_id == "happy_wealth"
        assert signal.pillar == "wealth"
        assert signal.satisfaction == 0.6
        assert signal.context == {'stocks': ['AAPL', 'GOOGL']}
    
    def test_to_reward_high_satisfaction(self):
        """Test converting high satisfaction to reward"""
        signal = AgentSignal(
            agent_id="stark_tech",
            pillar="work",
            decision_type="code_generation",
            action="Test",
            outcome="user_accepted",
            satisfaction=0.9
        )
        
        assert signal.to_reward() == +1
    
    def test_to_reward_low_satisfaction(self):
        """Test converting low satisfaction to reward"""
        signal = AgentSignal(
            agent_id="stark_tech",
            pillar="work",
            decision_type="code_generation",
            action="Test",
            outcome="user_rejected",
            satisfaction=0.2
        )
        
        assert signal.to_reward() == -1
    
    def test_to_reward_neutral(self):
        """Test converting neutral satisfaction to reward"""
        signal = AgentSignal(
            agent_id="stark_tech",
            pillar="work",
            decision_type="code_generation",
            action="Test",
            outcome="partial",
            satisfaction=0.5
        )
        
        assert signal.to_reward() == 0
    
    def test_to_hint_rejected(self):
        """Test extracting hint from rejection"""
        signal = AgentSignal(
            agent_id="stark_tech",
            pillar="work",
            decision_type="code_generation",
            action="Test",
            outcome="user_rejected",
            satisfaction=0.2
        )
        
        hint = signal.to_hint()
        assert hint is not None
        assert "rejected" in hint.lower()
    
    def test_to_hint_partial(self):
        """Test extracting hint from partial outcome"""
        signal = AgentSignal(
            agent_id="pepper_life",
            pillar="life",
            decision_type="advice",
            action="Test",
            outcome="partial",
            satisfaction=0.5
        )
        
        hint = signal.to_hint()
        assert hint is not None
        assert "improvement" in hint.lower()
    
    def test_to_hint_accepted(self):
        """Test no hint from accepted outcome"""
        signal = AgentSignal(
            agent_id="happy_wealth",
            pillar="wealth",
            decision_type="analysis",
            action="Test",
            outcome="user_accepted",
            satisfaction=0.9
        )
        
        hint = signal.to_hint()
        assert hint is None


class TestAgentSignalCollector:
    """Tests for AgentSignalCollector"""
    
    def test_record_signal(self):
        """Test recording a signal"""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = AgentSignalCollector(data_dir=Path(tmpdir))
            
            signal = collector.record(
                agent_id="stark_tech",
                pillar="work",
                decision_type="code_generation",
                action="Generated API",
                outcome="user_accepted",
                satisfaction=0.9
            )
            
            assert signal.agent_id == "stark_tech"
            assert signal.satisfaction == 0.9
    
    def test_get_signals(self):
        """Test getting signals"""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = AgentSignalCollector(data_dir=Path(tmpdir))
            
            # Record multiple signals
            collector.record("stark_tech", "work", "code_generation", "A1", "user_accepted", 0.9)
            collector.record("pepper_life", "life", "advice", "A2", "partial", 0.5)
            collector.record("happy_wealth", "wealth", "analysis", "A3", "user_rejected", 0.2)
            
            signals = collector.get_signals()
            
            assert len(signals) == 3
    
    def test_get_signals_filter_by_agent(self):
        """Test filtering signals by agent"""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = AgentSignalCollector(data_dir=Path(tmpdir))
            
            collector.record("stark_tech", "work", "code_generation", "A1", "user_accepted", 0.9)
            collector.record("pepper_life", "life", "advice", "A2", "partial", 0.5)
            collector.record("stark_tech", "work", "code_review", "A3", "user_accepted", 0.85)
            
            signals = collector.get_signals(agent_id="stark_tech")
            
            assert len(signals) == 2
            assert all(s.agent_id == "stark_tech" for s in signals)
    
    def test_get_signals_filter_by_pillar(self):
        """Test filtering signals by pillar"""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = AgentSignalCollector(data_dir=Path(tmpdir))
            
            collector.record("stark_tech", "work", "code_generation", "A1", "user_accepted", 0.9)
            collector.record("pepper_life", "life", "advice", "A2", "partial", 0.5)
            collector.record("happy_wealth", "wealth", "analysis", "A3", "user_rejected", 0.2)
            
            signals = collector.get_signals(pillar="work")
            
            assert len(signals) == 1
            assert signals[0].pillar == "work"
    
    def test_get_statistics(self):
        """Test getting statistics"""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = AgentSignalCollector(data_dir=Path(tmpdir))
            
            collector.record("stark_tech", "work", "code_generation", "A1", "user_accepted", 0.9)
            collector.record("pepper_life", "life", "advice", "A2", "partial", 0.5)
            collector.record("happy_wealth", "wealth", "analysis", "A3", "user_rejected", 0.2)
            
            stats = collector.get_statistics()
            
            assert stats['total_signals'] == 3
            assert stats['by_agent']['stark_tech'] == 1
            assert stats['by_pillar']['work'] == 1
            assert 0.5 <= stats['avg_satisfaction'] <= 0.6
            assert stats['acceptance_rate'] == 1/3
    
    def test_get_top_agents(self):
        """Test getting top agents"""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = AgentSignalCollector(data_dir=Path(tmpdir))
            
            # Stark: high satisfaction
            collector.record("stark_tech", "work", "code_generation", "A1", "user_accepted", 0.9)
            collector.record("stark_tech", "work", "code_review", "A2", "user_accepted", 0.85)
            
            # Pepper: medium satisfaction
            collector.record("pepper_life", "life", "advice", "A3", "partial", 0.6)
            
            top = collector.get_top_agents()
            
            assert len(top) >= 1
            assert top[0]['agent_id'] == "stark_tech"
            assert top[0]['avg_satisfaction'] > 0.8
    
    def test_export_to_learning(self):
        """Test exporting to learning format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = AgentSignalCollector(data_dir=Path(tmpdir))
            
            collector.record("stark_tech", "work", "code_generation", "A1", "user_accepted", 0.9)
            collector.record("pepper_life", "life", "advice", "A2", "user_rejected", 0.2)
            
            result = collector.export_to_learning()
            
            assert result['total_signals'] == 2
            assert len(result['rewards']) == 2  # Both have non-zero reward
            assert len(result['hints']) >= 1  # Rejection generates hint
    
    def test_pillars_defined(self):
        """Test that pillars are defined"""
        # PILLARS is now a customizable example, just verify structure exists
        assert hasattr(AgentSignalCollector, 'PILLARS')
        assert isinstance(AgentSignalCollector.PILLARS, dict)
        # Verify it has some default pillars
        assert 'work' in AgentSignalCollector.PILLARS
        assert 'life' in AgentSignalCollector.PILLARS
        assert 'wealth' in AgentSignalCollector.PILLARS
        # Note: Specific agent IDs can be customized by users
    
    def test_decision_types_defined(self):
        """Test that decision types are defined"""
        assert 'code_generation' in AgentSignalCollector.DECISION_TYPES
        assert 'advice' in AgentSignalCollector.DECISION_TYPES
        assert 'analysis' in AgentSignalCollector.DECISION_TYPES
    
    def test_outcomes_defined(self):
        """Test that outcomes are defined"""
        assert 'user_accepted' in AgentSignalCollector.OUTCOMES
        assert 'user_rejected' in AgentSignalCollector.OUTCOMES
        assert 'partial' in AgentSignalCollector.OUTCOMES
