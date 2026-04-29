"""
Rule Visualization Module for claw-rl v2.4.0

提供规则学习过程可视化和质量评估.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RuleQuality(Enum):
    """规则质量等级"""
    HIGH = "high"      # 高质量
    MEDIUM = "medium"  # 中等质量
    LOW = "low"        # 低质量
    UNKNOWN = "unknown"


@dataclass
class RuleMetrics:
    """规则指标"""
    rule_id: str
    confidence: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    last_used: Optional[datetime] = None
    quality: RuleQuality = RuleQuality.UNKNOWN
    evolution_score: float = 0.0  # 演化分数


@dataclass
class RuleEvolution:
    """规则演化记录"""
    rule_id: str
    timestamp: datetime
    event: str  # created, updated, merged, evolved
    old_value: Any = None
    new_value: Any = None
    reason: str = ""


class RuleVisualizer:
    """
    规则可视化器

    展示规则学习过程和质量评估.
    """

    def __init__(self):
        self._metrics: Dict[str, RuleMetrics] = {}
        self._evolution: Dict[str, List[RuleEvolution]] = {}

    def register_rule(self, rule_id: str, initial_confidence: float = 0.5):
        """注册规则"""
        if rule_id not in self._metrics:
            self._metrics[rule_id] = RuleMetrics(
                rule_id=rule_id,
                confidence=initial_confidence
            )
            self._add_evolution(rule_id, "created", None, initial_confidence)

    def update_metrics(
        self,
        rule_id: str,
        success: bool,
        confidence_delta: float = 0.01
    ):
        """更新规则指标"""
        if rule_id not in self._metrics:
            self.register_rule(rule_id)

        metrics = self._metrics[rule_id]
        metrics.usage_count += 1

        # Update success rate
        total = metrics.usage_count
        if success:
            metrics.success_rate = (metrics.success_rate * (total - 1) + 1) / total
        else:
            metrics.success_rate = (metrics.success_rate * (total - 1)) / total

        # Update confidence
        old_conf = metrics.confidence
        if success:
            metrics.confidence = min(1.0, metrics.confidence + confidence_delta)
        else:
            metrics.confidence = max(0.0, metrics.confidence - confidence_delta * 0.5)

        # Update quality
        metrics.quality = self._calculate_quality(metrics)

        # Update evolution
        metrics.evolution_score = self._calculate_evolution_score(metrics)
        self._add_evolution(rule_id, "updated", old_conf, metrics.confidence)

    def _calculate_quality(self, metrics: RuleMetrics) -> RuleQuality:
        """计算规则质量"""
        if metrics.usage_count < 5:
            return RuleQuality.UNKNOWN

        score = metrics.confidence * 0.4 + metrics.success_rate * 0.6

        if score >= 0.8:
            return RuleQuality.HIGH
        elif score >= 0.5:
            return RuleQuality.MEDIUM
        else:
            return RuleQuality.LOW

    def _calculate_evolution_score(self, metrics: RuleMetrics) -> float:
        """计算演化分数"""
        if metrics.usage_count == 0:
            return 0.0

        # Higher usage + consistent success = higher evolution
        return min(1.0, metrics.usage_count / 100) * metrics.success_rate

    def _add_evolution(self, rule_id: str, event: str, old_value: Any, new_value: Any):
        """添加演化记录"""
        if rule_id not in self._evolution:
            self._evolution[rule_id] = []

        self._evolution[rule_id].append(RuleEvolution(
            rule_id=rule_id,
            timestamp=datetime.now(),
            event=event,
            old_value=old_value,
            new_value=new_value
        ))

    def get_rule_metrics(self, rule_id: str) -> Optional[RuleMetrics]:
        """获取规则指标"""
        return self._metrics.get(rule_id)

    def get_all_metrics(self) -> List[RuleMetrics]:
        """获取所有规则指标"""
        return list(self._metrics.values())

    def get_quality_summary(self) -> Dict[str, int]:
        """获取质量摘要"""
        summary = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "unknown": 0
        }
        for metrics in self._metrics.values():
            summary[metrics.quality.value] += 1
        return summary

    def get_top_rules(self, top_k: int = 10, by: str = "confidence") -> List[RuleMetrics]:
        """获取顶级规则"""
        rules = list(self._metrics.values())

        if by == "confidence":
            rules.sort(key=lambda x: x.confidence, reverse=True)
        elif by == "usage":
            rules.sort(key=lambda x: x.usage_count, reverse=True)
        elif by == "evolution":
            rules.sort(key=lambda x: x.evolution_score, reverse=True)

        return rules[:top_k]

    def get_evolution_history(self, rule_id: str) -> List[RuleEvolution]:
        """获取规则演化历史"""
        return self._evolution.get(rule_id, [])

    def render_text_report(self) -> str:
        """渲染文本报告"""
        lines = [
            "=" * 50,
            "claw-rl Rule Visualization Report",
            "=" * 50,
        ]

        # Quality summary
        summary = self.get_quality_summary()
        lines.append(f"\nQuality Summary:")
        lines.append(f"  High:   {summary['high']}")
        lines.append(f"  Medium: {summary['medium']}")
        lines.append(f"  Low:    {summary['low']}")
        lines.append(f"  Unknown: {summary['unknown']}")

        # Top rules
        top_rules = self.get_top_rules(5)
        lines.append(f"\nTop 5 Rules by Confidence:")
        for i, rule in enumerate(top_rules, 1):
            lines.append(f"  {i}. {rule.rule_id}")
            lines.append(f"     Confidence: {rule.confidence:.2f}")
            lines.append(f"     Success Rate: {rule.success_rate:.2f}")
            lines.append(f"     Usage: {rule.usage_count}")

        lines.append("\n" + "=" * 50)
        return "\n".join(lines)


# Global visualizer
_visualizer: Optional[RuleVisualizer] = None


def get_visualizer() -> RuleVisualizer:
    """获取全局可视化器"""
    global _visualizer
    if _visualizer is None:
        _visualizer = RuleVisualizer()
    return _visualizer
