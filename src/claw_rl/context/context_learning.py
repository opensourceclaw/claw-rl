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
claw-rl Contextual Learning

Learns from decision context (time, emotion, situation, etc.).
Enables pattern recognition based on context.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class DecisionContext:
    """Decision context"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    time_of_day: str = ""  # morning, afternoon, evening, night
    day_of_week: str = ""  # Monday, Tuesday, etc.
    emotion: str = ""  # anxious, happy, calm, etc.
    situation: str = ""  # work, family, health, etc.
    urgency: str = "normal"  # low, normal, high
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "time_of_day": self.time_of_day,
            "day_of_week": self.day_of_week,
            "emotion": self.emotion,
            "situation": self.situation,
            "urgency": self.urgency,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DecisionContext':
        return cls(**data)


@dataclass
class ContextualDecision:
    """Decision with context"""
    decision_id: str
    context: DecisionContext
    decision_type: str
    options: List[str]
    chosen_option: str
    outcome: str
    satisfaction: float
    learned_pattern: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "context": self.context.to_dict(),
            "decision_type": self.decision_type,
            "options": self.options,
            "chosen_option": self.chosen_option,
            "outcome": self.outcome,
            "satisfaction": self.satisfaction,
            "learned_pattern": self.learned_pattern
        }


class ContextLearner:
    """
    Context Learner
    
    Learns patterns from decision contexts.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize Context Learner
        
        Args:
            data_dir: Directory for storing learning data
        """
        self.data_dir = data_dir or os.path.expanduser(
            "~/.openclaw/workspace/claw-rl/data"
        )
        self.decisions: List[ContextualDecision] = []
        self.patterns: Dict[str, List[Dict]] = {}  # pattern_type -> patterns
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data from disk"""
        decisions_file = os.path.join(self.data_dir, "contextual_decisions.jsonl")
        
        if os.path.exists(decisions_file):
            try:
                with open(decisions_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        decision = self._dict_to_decision(data)
                        self.decisions.append(decision)
                
                print(f"✅ Loaded {len(self.decisions)} contextual decisions")
            except Exception as e:
                print(f"⚠️  Could not load data: {e}")
        
        # Load patterns
        patterns_file = os.path.join(self.data_dir, "context_patterns.json")
        if os.path.exists(patterns_file):
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
                
                print(f"✅ Loaded {sum(len(p) for p in self.patterns.values())} patterns")
            except Exception as e:
                print(f"⚠️  Could not load patterns: {e}")
    
    def _dict_to_decision(self, data: Dict) -> ContextualDecision:
        """Convert dict to decision"""
        context = DecisionContext.from_dict(data['context'])
        return ContextualDecision(
            decision_id=data['decision_id'],
            context=context,
            decision_type=data['decision_type'],
            options=data['options'],
            chosen_option=data['chosen_option'],
            outcome=data['outcome'],
            satisfaction=data['satisfaction'],
            learned_pattern=data.get('learned_pattern')
        )
    
    def _save_data(self) -> None:
        """Save data to disk"""
        # Save decisions
        decisions_file = os.path.join(self.data_dir, "contextual_decisions.jsonl")
        with open(decisions_file, 'a', encoding='utf-8') as f:
            for decision in self.decisions[-1:]:  # Only save new decisions
                f.write(json.dumps(decision.to_dict(), ensure_ascii=False) + '\n')
        
        # Save patterns
        patterns_file = os.path.join(self.data_dir, "context_patterns.json")
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(self.decisions)} decisions and patterns")
    
    def record_decision(
        self,
        decision_id: str,
        decision_type: str,
        options: List[str],
        chosen_option: str,
        outcome: str,
        satisfaction: float,
        context_data: Dict[str, Any] = None
    ) -> ContextualDecision:
        """
        Record a decision with context
        
        Args:
            decision_id: Unique decision ID
            decision_type: Type of decision (investment, career, health, etc.)
            options: Available options
            chosen_option: Chosen option
            outcome: Outcome (success/failure/partial)
            satisfaction: Satisfaction score (0.0-1.0)
            context_data: Context data (emotion, time, situation, etc.)
            
        Returns:
            ContextualDecision: Recorded decision
        """
        # Create context
        context = self._create_context(context_data)
        
        # Create decision
        decision = ContextualDecision(
            decision_id=decision_id,
            context=context,
            decision_type=decision_type,
            options=options,
            chosen_option=chosen_option,
            outcome=outcome,
            satisfaction=satisfaction
        )
        
        # Store decision
        self.decisions.append(decision)
        
        # Learn pattern
        pattern = self._learn_pattern(decision)
        if pattern:
            decision.learned_pattern = pattern
        
        # Save
        self._save_data()
        
        return decision
    
    def _create_context(self, context_data: Dict[str, Any] = None) -> DecisionContext:
        """Create context from data"""
        context_data = context_data or {}
        
        # Auto-detect time of day
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        elif 18 <= hour < 23:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Auto-detect day of week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                "Friday", "Saturday", "Sunday"]
        day_of_week = days[datetime.now().weekday()]
        
        return DecisionContext(
            time_of_day=context_data.get('time_of_day', time_of_day),
            day_of_week=context_data.get('day_of_week', day_of_week),
            emotion=context_data.get('emotion', ''),
            situation=context_data.get('situation', ''),
            urgency=context_data.get('urgency', 'normal'),
            metadata=context_data.get('metadata', {})
        )
    
    def _learn_pattern(self, decision: ContextualDecision) -> Optional[str]:
        """
        Learn pattern from decision
        
        Args:
            decision: Decision to learn from
            
        Returns:
            Optional[str]: Learned pattern description
        """
        # Simple pattern learning
        # In production, this would use more sophisticated ML
        
        context = decision.context
        decision_type = decision.decision_type
        
        # Pattern: emotion -> decision type
        if context.emotion:
            pattern_key = f"{context.emotion}_{decision_type}"
            
            if pattern_key not in self.patterns:
                self.patterns[pattern_key] = []
            
            self.patterns[pattern_key].append({
                "chosen_option": decision.chosen_option,
                "satisfaction": decision.satisfaction,
                "outcome": decision.outcome
            })
            
            # If high satisfaction, reinforce pattern
            if decision.satisfaction >= 0.8:
                return f"当{context.emotion}时，您倾向于选择{decision.chosen_option}（满意度{decision.satisfaction:.0%}）"
        
        return None
    
    def get_patterns_for_context(
        self,
        emotion: str = None,
        decision_type: str = None,
        situation: str = None
    ) -> List[Dict]:
        """
        Get patterns for a context
        
        Args:
            emotion: Emotion filter
            decision_type: Decision type filter
            situation: Situation filter
            
        Returns:
            List[Dict]: Matching patterns
        """
        patterns = []
        
        # Search patterns
        for pattern_key, pattern_list in self.patterns.items():
            match = True
            
            if emotion and emotion not in pattern_key:
                match = False
            if decision_type and decision_type not in pattern_key:
                match = False
            
            if match:
                patterns.extend(pattern_list)
        
        return patterns
    
    def get_decision_history(
        self,
        decision_type: str = None,
        limit: int = 10
    ) -> List[ContextualDecision]:
        """
        Get decision history
        
        Args:
            decision_type: Filter by decision type
            limit: Result limit
            
        Returns:
            List[ContextualDecision]: Decisions
        """
        decisions = self.decisions
        
        if decision_type:
            decisions = [d for d in decisions if d.decision_type == decision_type]
        
        # Sort by timestamp (newest first)
        decisions.sort(
            key=lambda d: d.context.timestamp,
            reverse=True
        )
        
        return decisions[:limit]
    
    def get_statistics(self) -> Dict:
        """
        Get learning statistics
        
        Returns:
            Dict: Statistics
        """
        # Count by decision type
        by_type = {}
        for decision in self.decisions:
            decision_type = decision.decision_type
            by_type[decision_type] = by_type.get(decision_type, 0) + 1
        
        # Average satisfaction
        avg_satisfaction = (
            sum(d.satisfaction for d in self.decisions) / len(self.decisions)
            if self.decisions else 0.0
        )
        
        # Pattern count
        total_patterns = sum(len(p) for p in self.patterns.values())
        
        return {
            "total_decisions": len(self.decisions),
            "by_decision_type": by_type,
            "avg_satisfaction": avg_satisfaction,
            "total_patterns": total_patterns,
            "pattern_types": list(self.patterns.keys())
        }
