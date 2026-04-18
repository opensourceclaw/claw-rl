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
Learning Metrics Exporter (v2.1.0)

Exports learning metrics in multiple formats:
- Prometheus (for monitoring systems)
- JSON (for APIs and dashboards)
- Markdown (for reports)

This enables observability of the learning system.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """A single metric data point"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""
    metric_type: str = "gauge"  # gauge, counter, histogram


class LearningMetricsCollector:
    """
    Collects learning metrics from various sources.
    
    Acts as a central hub for all learning-related metrics.
    """
    
    def __init__(self):
        """Initialize the collector"""
        self.metrics: Dict[str, List[MetricPoint]] = {}
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        
        # Learning stats
        self.total_rewards = 0.0
        self.positive_rewards = 0
        self.negative_rewards = 0
        self.neutral_rewards = 0
        
        self.total_hints = 0
        self.opd_hints = 0
        self.binary_rl_evaluations = 0
        
        self.active_rules = 0
        self.rules_added = 0
        self.rules_merged = 0
        self.rules_evolved = 0
        
        # Performance stats
        self.avg_latency_ms = 0.0
        self.llm_calls = 0
        self.llm_cache_hits = 0
        self.llm_fallbacks = 0
        
        # MAB stats
        self.strategy_selections = 0
        self.strategy_switches = 0
        self.exploration_rate = 0.0
    
    def record_reward(self, reward: float):
        """Record a reward observation"""
        self.total_rewards += reward
        self.binary_rl_evaluations += 1
        
        if reward > 0:
            self.positive_rewards += 1
        elif reward < 0:
            self.negative_rewards += 1
        else:
            self.neutral_rewards += 1
    
    def record_hint(self, hint_type: str = "opd"):
        """Record a hint extraction"""
        self.total_hints += 1
        if hint_type == "opd":
            self.opd_hints += 1
    
    def record_rule_change(self, change_type: str):
        """Record a rule change"""
        if change_type == "add":
            self.rules_added += 1
            self.active_rules += 1
        elif change_type == "merge":
            self.rules_merged += 1
        elif change_type == "evolve":
            self.rules_evolved += 1
    
    def record_llm_call(self, cache_hit: bool = False, fallback: bool = False):
        """Record an LLM call"""
        self.llm_calls += 1
        if cache_hit:
            self.llm_cache_hits += 1
        if fallback:
            self.llm_fallbacks += 1
    
    def record_latency(self, latency_ms: float):
        """Record operation latency"""
        # Exponential moving average
        if self.avg_latency_ms == 0:
            self.avg_latency_ms = latency_ms
        else:
            self.avg_latency_ms = 0.9 * self.avg_latency_ms + 0.1 * latency_ms
    
    def record_mab_selection(self, strategy_switch: bool = False):
        """Record MAB strategy selection"""
        self.strategy_selections += 1
        if strategy_switch:
            self.strategy_switches += 1
    
    def set_exploration_rate(self, rate: float):
        """Set current exploration rate"""
        self.exploration_rate = rate
    
    def set_active_rules(self, count: int):
        """Set active rule count"""
        self.active_rules = count
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary"""
        return {
            'rewards': {
                'total': self.total_rewards,
                'positive': self.positive_rewards,
                'negative': self.negative_rewards,
                'neutral': self.neutral_rewards,
                'avg_reward': self.total_rewards / self.binary_rl_evaluations if self.binary_rl_evaluations > 0 else 0,
            },
            'hints': {
                'total': self.total_hints,
                'opd': self.opd_hints,
            },
            'rules': {
                'active': self.active_rules,
                'added': self.rules_added,
                'merged': self.rules_merged,
                'evolved': self.rules_evolved,
            },
            'performance': {
                'avg_latency_ms': round(self.avg_latency_ms, 2),
                'llm_calls': self.llm_calls,
                'llm_cache_hits': self.llm_cache_hits,
                'llm_fallbacks': self.llm_fallbacks,
                'cache_hit_rate': self.llm_cache_hits / self.llm_calls if self.llm_calls > 0 else 0,
            },
            'mab': {
                'selections': self.strategy_selections,
                'switches': self.strategy_switches,
                'exploration_rate': round(self.exploration_rate, 3),
            },
            'timestamp': datetime.now().isoformat(),
        }


class LearningMetricsExporter:
    """
    Exports learning metrics in various formats.
    
    Usage:
        collector = LearningMetricsCollector()
        collector.record_reward(1.0)
        collector.record_hint("opd")
        
        exporter = LearningMetricsExporter(collector)
        
        # Export to different formats
        prometheus_text = exporter.export_prometheus()
        json_data = exporter.export_json()
        markdown_report = exporter.export_markdown()
    """
    
    def __init__(self, collector: Optional[LearningMetricsCollector] = None):
        """
        Initialize exporter.
        
        Args:
            collector: Metrics collector (creates new one if None)
        """
        self.collector = collector or LearningMetricsCollector()
    
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted text
        """
        metrics = self.collector.get_all_metrics()
        lines = []
        
        # Rewards
        lines.append("# HELP clawrl_rewards_total Total rewards collected")
        lines.append("# TYPE clawrl_rewards_total counter")
        lines.append(f"clawrl_rewards_total{{type=\"positive\"}} {metrics['rewards']['positive']}")
        lines.append(f"clawrl_rewards_total{{type=\"negative\"}} {metrics['rewards']['negative']}")
        lines.append(f"clawrl_rewards_total{{type=\"neutral\"}} {metrics['rewards']['neutral']}")
        lines.append("")
        
        lines.append("# HELP clawrl_reward_average Average reward")
        lines.append("# TYPE clawrl_reward_average gauge")
        lines.append(f"clawrl_reward_average {metrics['rewards']['avg_reward']:.3f}")
        lines.append("")
        
        # Hints
        lines.append("# HELP clawrl_hints_total Total hints extracted")
        lines.append("# TYPE clawrl_hints_total counter")
        lines.append(f"clawrl_hints_total{{type=\"opd\"}} {metrics['hints']['opd']}")
        lines.append(f"clawrl_hints_total {metrics['hints']['total']}")
        lines.append("")
        
        # Rules
        lines.append("# HELP clawrl_rules_active Active learning rules")
        lines.append("# TYPE clawrl_rules_active gauge")
        lines.append(f"clawrl_rules_active {metrics['rules']['active']}")
        lines.append("")
        
        lines.append("# HELP clawrl_rules_changes_total Rule changes")
        lines.append("# TYPE clawrl_rules_changes_total counter")
        lines.append(f"clawrl_rules_changes_total{{type=\"added\"}} {metrics['rules']['added']}")
        lines.append(f"clawrl_rules_changes_total{{type=\"merged\"}} {metrics['rules']['merged']}")
        lines.append(f"clawrl_rules_changes_total{{type=\"evolved\"}} {metrics['rules']['evolved']}")
        lines.append("")
        
        # Performance
        lines.append("# HELP clawrl_latency_ms Average operation latency in milliseconds")
        lines.append("# TYPE clawrl_latency_ms gauge")
        lines.append(f"clawrl_latency_ms {metrics['performance']['avg_latency_ms']}")
        lines.append("")
        
        lines.append("# HELP clawrl_llm_calls_total LLM API calls")
        lines.append("# TYPE clawrl_llm_calls_total counter")
        lines.append(f"clawrl_llm_calls_total {metrics['performance']['llm_calls']}")
        lines.append(f"clawrl_llm_cache_hits_total {metrics['performance']['llm_cache_hits']}")
        lines.append(f"clawrl_llm_fallbacks_total {metrics['performance']['llm_fallbacks']}")
        lines.append("")
        
        # MAB
        lines.append("# HELP clawrl_mab_selections_total Strategy selections")
        lines.append("# TYPE clawrl_mab_selections_total counter")
        lines.append(f"clawrl_mab_selections_total {metrics['mab']['selections']}")
        lines.append(f"clawrl_mab_switches_total {metrics['mab']['switches']}")
        lines.append("")
        
        lines.append("# HELP clawrl_exploration_rate Current exploration rate")
        lines.append("# TYPE clawrl_exploration_rate gauge")
        lines.append(f"clawrl_exploration_rate {metrics['mab']['exploration_rate']}")
        lines.append("")
        
        return "\n".join(lines)
    
    def export_json(self, indent: int = 2) -> str:
        """
        Export metrics as JSON.
        
        Args:
            indent: JSON indentation
            
        Returns:
            JSON string
        """
        return json.dumps(self.collector.get_all_metrics(), indent=indent)
    
    def export_markdown(self, title: str = "Learning Metrics Report") -> str:
        """
        Export metrics as Markdown report.
        
        Args:
            title: Report title
            
        Returns:
            Markdown-formatted text
        """
        metrics = self.collector.get_all_metrics()
        
        lines = [
            f"# {title}",
            "",
            f"**Generated:** {metrics['timestamp']}",
            "",
            "## 📊 Rewards",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Rewards | {metrics['rewards']['total']:.2f} |",
            f"| Positive | {metrics['rewards']['positive']} |",
            f"| Negative | {metrics['rewards']['negative']} |",
            f"| Neutral | {metrics['rewards']['neutral']} |",
            f"| Average | {metrics['rewards']['avg_reward']:.3f} |",
            "",
            "## 💡 Hints",
            "",
            f"| Type | Count |",
            f"|------|-------|",
            f"| OPD Hints | {metrics['hints']['opd']} |",
            f"| Total | {metrics['hints']['total']} |",
            "",
            "## 📜 Rules",
            "",
            f"| Metric | Count |",
            f"|--------|-------|",
            f"| Active Rules | {metrics['rules']['active']} |",
            f"| Added | {metrics['rules']['added']} |",
            f"| Merged | {metrics['rules']['merged']} |",
            f"| Evolved | {metrics['rules']['evolved']} |",
            "",
            "## ⚡ Performance",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Avg Latency | {metrics['performance']['avg_latency_ms']:.2f}ms |",
            f"| LLM Calls | {metrics['performance']['llm_calls']} |",
            f"| Cache Hits | {metrics['performance']['llm_cache_hits']} |",
            f"| Cache Hit Rate | {metrics['performance']['cache_hit_rate']:.1%} |",
            f"| Fallbacks | {metrics['performance']['llm_fallbacks']} |",
            "",
            "## 🎰 Multi-Armed Bandit",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Selections | {metrics['mab']['selections']} |",
            f"| Strategy Switches | {metrics['mab']['switches']} |",
            f"| Exploration Rate | {metrics['mab']['exploration_rate']:.1%} |",
            "",
        ]
        
        return "\n".join(lines)
    
    def export_to_file(self, path: Path, format: str = "json"):
        """
        Export metrics to file.
        
        Args:
            path: Output file path
            format: Output format (json, prometheus, markdown)
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            content = self.export_json()
        elif format == "prometheus":
            content = self.export_prometheus()
        elif format == "markdown":
            content = self.export_markdown()
        else:
            raise ValueError(f"Unknown format: {format}")
        
        path.write_text(content)
        logger.info(f"Exported metrics to {path}")


# Global collector instance
_global_collector: Optional[LearningMetricsCollector] = None


def get_collector() -> LearningMetricsCollector:
    """Get or create global metrics collector"""
    global _global_collector
    if _global_collector is None:
        _global_collector = LearningMetricsCollector()
    return _global_collector


def get_exporter() -> LearningMetricsExporter:
    """Get exporter with global collector"""
    return LearningMetricsExporter(get_collector())
