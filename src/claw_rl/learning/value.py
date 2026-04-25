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
claw-rl Value Preference Learning

Learns user value preferences from decision feedback.
Updates value priorities based on outcomes.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class ValuePreference:
    """User value preference"""
    name: str
    category: str  # family, wealth, health, career, etc.
    priority: float  # 0.0-10.0
    learned_from: List[str] = field(default_factory=list)  # decision IDs
    confidence: float = 0.5  # 0.0-1.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category,
            "priority": self.priority,
            "learned_from": self.learned_from,
            "confidence": self.confidence,
            "last_updated": self.last_updated
        }


@dataclass
class DecisionRecord:
    """Decision record for learning"""
    id: str
    context: str
    options: List[str]
    chosen_option: str
    outcome: str  # success, failure, partial
    satisfaction: float  # 0.0-1.0
    value_alignment: Dict[str, float] = field(default_factory=dict)  # value -> alignment score
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "context": self.context,
            "options": self.options,
            "chosen_option": self.chosen_option,
            "outcome": self.outcome,
            "satisfaction": self.satisfaction,
            "value_alignment": self.value_alignment,
            "timestamp": self.timestamp
        }


class ValuePreferenceLearner:
    """
    Value Preference Learner
    
    Learns user value preferences from:
    - Decision outcomes
    - User feedback
    - Satisfaction ratings
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize Value Preference Learner
        
        Args:
            data_dir: Directory for storing learning data
        """
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data")
        self.preferences: Dict[str, ValuePreference] = {}
        self.decision_history: List[DecisionRecord] = []
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing preferences
        self._load_preferences()
    
    def _load_preferences(self) -> None:
        """Load preferences from disk"""
        prefs_file = os.path.join(self.data_dir, "value_preferences.json")
        
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for name, pref_data in data.items():
                    self.preferences[name] = ValuePreference(
                        name=pref_data['name'],
                        category=pref_data['category'],
                        priority=pref_data['priority'],
                        learned_from=pref_data.get('learned_from', []),
                        confidence=pref_data.get('confidence', 0.5),
                        last_updated=pref_data.get('last_updated', datetime.now().isoformat())
                    )
                
                print(f"✅ Loaded {len(self.preferences)} value preferences")
            except Exception as e:
                print(f"⚠️  Could not load preferences: {e}")
                self._initialize_default_preferences()
        else:
            self._initialize_default_preferences()
    
    def _initialize_default_preferences(self) -> None:
        """Initialize default value preferences"""
        default_values = [
            ValuePreference(name="family", category="family", priority=8.0),
            ValuePreference(name="wealth", category="wealth", priority=7.0),
            ValuePreference(name="health", category="health", priority=9.0),
            ValuePreference(name="career", category="career", priority=7.0),
        ]
        
        for pref in default_values:
            self.preferences[pref.name] = pref
        
        self._save_preferences()
    
    def _save_preferences(self) -> None:
        """Save preferences to disk"""
        prefs_file = os.path.join(self.data_dir, "value_preferences.json")
        
        data = {name: pref.to_dict() for name, pref in self.preferences.items()}
        
        with open(prefs_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(self.preferences)} value preferences")
    
    def record_decision(self, decision: DecisionRecord) -> None:
        """
        Record a decision for learning
        
        Args:
            decision: Decision record
        """
        self.decision_history.append(decision)
        
        # Limit history size
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
        
        # Save decision
        self._save_decision(decision)
        
        # Learn from decision
        self._learn_from_decision(decision)
    
    def _save_decision(self, decision: DecisionRecord) -> None:
        """Save decision to disk"""
        decisions_file = os.path.join(self.data_dir, "decisions.jsonl")
        
        with open(decisions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(decision.to_dict(), ensure_ascii=False) + '\n')
    
    def _learn_from_decision(self, decision: DecisionRecord) -> None:
        """
        Learn from a decision
        
        Args:
            decision: Decision record
        """
        # Update value priorities based on outcome
        if decision.outcome == "success" and decision.satisfaction > 0.7:
            # Positive outcome: reinforce values that were aligned
            for value_name, alignment in decision.value_alignment.items():
                if alignment > 0.5:
                    self._reinforce_value(value_name, decision.satisfaction)
        elif decision.outcome == "failure" or decision.satisfaction < 0.3:
            # Negative outcome: adjust values that were misaligned
            for value_name, alignment in decision.value_alignment.items():
                if alignment < 0.5:
                    self._adjust_value(value_name, decision.satisfaction)
    
    def _reinforce_value(self, value_name: str, satisfaction: float) -> None:
        """
        Reinforce a value based on positive outcome
        
        Args:
            value_name: Value name
            satisfaction: Satisfaction score (0.0-1.0)
        """
        if value_name not in self.preferences:
            self.preferences[value_name] = ValuePreference(
                name=value_name,
                category="general",
                priority=5.0
            )
        
        pref = self.preferences[value_name]
        
        # Increase priority (max 10.0)
        adjustment = satisfaction * 0.5
        pref.priority = min(pref.priority + adjustment, 10.0)
        
        # Increase confidence
        pref.confidence = min(pref.confidence + 0.1, 1.0)
        
        # Update timestamp
        pref.last_updated = datetime.now().isoformat()
        
        print(f"✅ Reinforced value '{value_name}': priority {pref.priority:.1f}")
        
        self._save_preferences()
    
    def _adjust_value(self, value_name: str, satisfaction: float) -> None:
        """
        Adjust a value based on negative outcome
        
        Args:
            value_name: Value name
            satisfaction: Satisfaction score (0.0-1.0)
        """
        if value_name not in self.preferences:
            return  # Don't create new values from negative outcomes
        
        pref = self.preferences[value_name]
        
        # Decrease priority (min 0.0)
        adjustment = (1.0 - satisfaction) * 0.3
        pref.priority = max(pref.priority - adjustment, 0.0)
        
        # Decrease confidence
        pref.confidence = max(pref.confidence - 0.1, 0.0)
        
        # Update timestamp
        pref.last_updated = datetime.now().isoformat()
        
        print(f"⚠️  Adjusted value '{value_name}': priority {pref.priority:.1f}")
        
        self._save_preferences()
    
    def get_priorities(self) -> Dict[str, float]:
        """
        Get current value priorities
        
        Returns:
            Dict[str, float]: Value priorities
        """
        return {name: pref.priority for name, pref in self.preferences.items()}
    
    def get_ranked_values(self) -> List[Tuple[str, float]]:
        """
        Get values ranked by priority
        
        Returns:
            List[Tuple[str, float]]: Ranked values
        """
        ranked = sorted(
            self.preferences.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        return [(name, pref.priority) for name, pref in ranked]
    
    def get_value_alignment(self, decision_context: str) -> Dict[str, float]:
        """
        Get value alignment for a decision context
        
        Args:
            decision_context: Decision context
            
        Returns:
            Dict[str, float]: Value alignment scores
        """
        # Simple keyword-based alignment (can be enhanced with ML)
        context_lower = decision_context.lower()
        
        alignment = {}
        for name, pref in self.preferences.items():
            # Check if value keywords appear in context
            score = 0.0
            if pref.category in context_lower or name in context_lower:
                score = pref.priority / 10.0
            alignment[name] = score
        
        return alignment
    
    def get_learning_statistics(self) -> Dict:
        """
        Get learning statistics
        
        Returns:
            Dict: Learning statistics
        """
        return {
            "total_values": len(self.preferences),
            "total_decisions": len(self.decision_history),
            "top_values": self.get_ranked_values()[:3],
            "average_confidence": sum(p.confidence for p in self.preferences.values()) / len(self.preferences) if self.preferences else 0.0
        }
