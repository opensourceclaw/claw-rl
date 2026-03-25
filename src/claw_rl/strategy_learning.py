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
claw-rl Conflict Resolution Strategy Learning

Learns effective conflict resolution strategies from outcomes.
Optimizes strategy selection over time.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class StrategyRecord:
    """Conflict resolution strategy record"""
    id: str
    conflict_type: str  # contradictory, value_based, goal_conflict, etc.
    strategy_used: str  # priority_based, user_decision, compromise, etc.
    success: bool
    satisfaction: float  # 0.0-1.0
    context: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "conflict_type": self.conflict_type,
            "strategy_used": self.strategy_used,
            "success": self.success,
            "satisfaction": self.satisfaction,
            "context": self.context,
            "timestamp": self.timestamp
        }


@dataclass
class StrategyEffectiveness:
    """Effectiveness data for a strategy"""
    strategy: str
    conflict_type: str
    total_uses: int = 0
    successful_uses: int = 0
    avg_satisfaction: float = 0.0
    effectiveness_score: float = 0.0  # 0.0-1.0
    recommended: bool = False
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy,
            "conflict_type": self.conflict_type,
            "total_uses": self.total_uses,
            "successful_uses": self.successful_uses,
            "avg_satisfaction": self.avg_satisfaction,
            "effectiveness_score": self.effectiveness_score,
            "recommended": self.recommended,
            "last_updated": self.last_updated
        }


class StrategyLearner:
    """
    Conflict Resolution Strategy Learner
    
    Learns which strategies work best for:
    - Different conflict types
    - Different domains
    - Different contexts
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize Strategy Learner
        
        Args:
            data_dir: Directory for storing learning data
        """
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data")
        self.strategies: Dict[str, Dict[str, StrategyEffectiveness]] = {}  # conflict_type -> strategy -> effectiveness
        self.strategy_history: List[StrategyRecord] = []
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing strategies
        self._load_strategies()
    
    def _load_strategies(self) -> None:
        """Load strategies from disk"""
        strat_file = os.path.join(self.data_dir, "strategy_effectiveness.json")
        
        if os.path.exists(strat_file):
            try:
                with open(strat_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for conflict_type, strategies in data.items():
                    self.strategies[conflict_type] = {}
                    for strategy, eff_data in strategies.items():
                        self.strategies[conflict_type][strategy] = StrategyEffectiveness(
                            strategy=eff_data['strategy'],
                            conflict_type=eff_data['conflict_type'],
                            total_uses=eff_data['total_uses'],
                            successful_uses=eff_data['successful_uses'],
                            avg_satisfaction=eff_data['avg_satisfaction'],
                            effectiveness_score=eff_data['effectiveness_score'],
                            recommended=eff_data['recommended'],
                            last_updated=eff_data.get('last_updated', datetime.now().isoformat())
                        )
                
                print(f"✅ Loaded {sum(len(s) for s in self.strategies.values())} strategy effectiveness records")
            except Exception as e:
                print(f"⚠️  Could not load strategies: {e}")
                self._initialize_default_strategies()
        else:
            self._initialize_default_strategies()
    
    def _initialize_default_strategies(self) -> None:
        """Initialize default strategies"""
        conflict_types = ["contradictory", "value_based", "goal_conflict", "competing_resources", "timing"]
        strategies = ["priority_based", "user_decision", "compromise", "integration", "sequencing", "expert_consultation"]
        
        for conflict_type in conflict_types:
            self.strategies[conflict_type] = {}
            for strategy in strategies:
                self.strategies[conflict_type][strategy] = StrategyEffectiveness(
                    strategy=strategy,
                    conflict_type=conflict_type
                )
        
        self._save_strategies()
    
    def _save_strategies(self) -> None:
        """Save strategies to disk"""
        strat_file = os.path.join(self.data_dir, "strategy_effectiveness.json")
        
        data = {
            conflict_type: {
                strategy: eff.to_dict()
                for strategy, eff in strategies.items()
            }
            for conflict_type, strategies in self.strategies.items()
        }
        
        with open(strat_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {sum(len(s) for s in self.strategies.values())} strategy effectiveness records")
    
    def record_strategy(self, record: StrategyRecord) -> None:
        """
        Record a strategy usage
        
        Args:
            record: Strategy record
        """
        self.strategy_history.append(record)
        
        # Limit history size
        if len(self.strategy_history) > 1000:
            self.strategy_history = self.strategy_history[-1000:]
        
        # Save record
        self._save_record(record)
        
        # Update effectiveness
        self._update_effectiveness(record)
    
    def _save_record(self, record: StrategyRecord) -> None:
        """Save strategy record to disk"""
        records_file = os.path.join(self.data_dir, "strategy_records.jsonl")
        
        with open(records_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + '\n')
    
    def _update_effectiveness(self, record: StrategyRecord) -> None:
        """
        Update strategy effectiveness based on record
        
        Args:
            record: Strategy record
        """
        if record.conflict_type not in self.strategies:
            self.strategies[record.conflict_type] = {}
        
        if record.strategy_used not in self.strategies[record.conflict_type]:
            self.strategies[record.conflict_type][record.strategy_used] = StrategyEffectiveness(
                strategy=record.strategy_used,
                conflict_type=record.conflict_type
            )
        
        eff = self.strategies[record.conflict_type][record.strategy_used]
        
        # Update counts
        eff.total_uses += 1
        if record.success:
            eff.successful_uses += 1
        
        # Update average satisfaction (running average)
        n = eff.total_uses
        old_avg = eff.avg_satisfaction
        eff.avg_satisfaction = old_avg + (record.satisfaction - old_avg) / n
        
        # Calculate effectiveness score
        eff.effectiveness_score = self._calculate_effectiveness(eff)
        
        # Update recommendation
        eff.recommended = self._is_recommended(eff)
        
        # Update timestamp
        eff.last_updated = datetime.now().isoformat()
        
        print(f"✅ Updated effectiveness for '{record.strategy_used}' ({record.conflict_type}): score={eff.effectiveness_score:.2f}")
        
        self._save_strategies()
    
    def _calculate_effectiveness(self, eff: StrategyEffectiveness) -> float:
        """
        Calculate effectiveness score
        
        Args:
            eff: Strategy effectiveness
            
        Returns:
            float: Effectiveness score (0.0-1.0)
        """
        if eff.total_uses < 3:
            return 0.5  # Not enough data
        
        # Success rate component (50%)
        success_rate = eff.successful_uses / eff.total_uses
        
        # Satisfaction component (50%)
        satisfaction_component = eff.avg_satisfaction
        
        # Combined score
        return (success_rate * 0.5 + satisfaction_component * 0.5)
    
    def _is_recommended(self, eff: StrategyEffectiveness) -> bool:
        """
        Determine if strategy should be recommended
        
        Args:
            eff: Strategy effectiveness
            
        Returns:
            bool: Whether to recommend
        """
        if eff.total_uses < 5:
            return False  # Not enough data
        
        return eff.effectiveness_score >= 0.7
    
    def get_recommended_strategy(self, conflict_type: str) -> Optional[str]:
        """
        Get recommended strategy for a conflict type
        
        Args:
            conflict_type: Conflict type
            
        Returns:
            Optional[str]: Recommended strategy or None
        """
        if conflict_type not in self.strategies:
            return None
        
        strategies = self.strategies[conflict_type]
        
        # Find best recommended strategy
        recommended = [
            (strategy, eff.effectiveness_score)
            for strategy, eff in strategies.items()
            if eff.recommended
        ]
        
        if not recommended:
            # No recommended strategies, return best overall
            best = max(strategies.items(), key=lambda x: x[1].effectiveness_score)
            return best[0] if best[1].effectiveness_score > 0.5 else None
        
        # Return best recommended
        return max(recommended, key=lambda x: x[1])[0]
    
    def get_strategy_ranking(self, conflict_type: str) -> List[Tuple[str, float]]:
        """
        Get strategy ranking for a conflict type
        
        Args:
            conflict_type: Conflict type
            
        Returns:
            List[Tuple[str, float]]: Ranked strategies
        """
        if conflict_type not in self.strategies:
            return []
        
        strategies = self.strategies[conflict_type]
        
        ranked = sorted(
            strategies.items(),
            key=lambda x: x[1].effectiveness_score,
            reverse=True
        )
        
        return [(strategy, eff.effectiveness_score) for strategy, eff in ranked]
    
    def get_learning_statistics(self) -> Dict:
        """
        Get learning statistics
        
        Returns:
            Dict: Learning statistics
        """
        total_strategies = sum(len(s) for s in self.strategies.values())
        recommended_count = sum(
            sum(1 for eff in strategies.values() if eff.recommended)
            for strategies in self.strategies.values()
        )
        
        avg_effectiveness = 0.0
        count = 0
        for strategies in self.strategies.values():
            for eff in strategies.values():
                avg_effectiveness += eff.effectiveness_score
                count += 1
        
        if count > 0:
            avg_effectiveness /= count
        
        return {
            "total_conflict_types": len(self.strategies),
            "total_strategies": total_strategies,
            "recommended_strategies": recommended_count,
            "avg_effectiveness": avg_effectiveness,
            "total_records": len(self.strategy_history)
        }
