"""
Learning Effectiveness Evaluation

This module evaluates the effectiveness of learning strategies
and calculates ROI (Return on Investment) metrics.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os


class MetricType(Enum):
    """Types of metrics."""
    CONVERSION = "conversion"       # Conversion rate
    SATISFACTION = "satisfaction"   # User satisfaction
    EFFICIENCY = "efficiency"       # Time/resource efficiency
    ACCURACY = "accuracy"           # Prediction accuracy
    ENGAGEMENT = "engagement"       # User engagement


@dataclass
class MetricDataPoint:
    """A single metric data point."""
    timestamp: str
    value: float
    metric_type: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "value": self.value,
            "metric_type": self.metric_type,
            "context": self.context,
        }


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    metric_type: str
    count: int
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    trend: str  # "up", "down", "stable"
    improvement_rate: float  # % change over period
    
    def to_dict(self) -> dict:
        return {
            "metric_type": self.metric_type,
            "count": self.count,
            "mean": self.mean,
            "std_dev": self.std_dev,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "trend": self.trend,
            "improvement_rate": self.improvement_rate,
        }


@dataclass
class EvaluationResult:
    """Result of a learning evaluation."""
    evaluation_id: str
    evaluated_at: str
    period_start: str
    period_end: str
    
    # Metric summaries
    metrics: Dict[str, MetricSummary]
    
    # Overall assessment
    overall_score: float  # 0.0 to 1.0
    overall_trend: str    # "improving", "declining", "stable"
    
    # ROI metrics
    roi_percentage: float
    cost_savings: float
    time_savings_hours: float
    
    # Recommendations
    recommendations: List[str]
    
    def to_dict(self) -> dict:
        return {
            "evaluation_id": self.evaluation_id,
            "evaluated_at": self.evaluated_at,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "overall_score": self.overall_score,
            "overall_trend": self.overall_trend,
            "roi_percentage": self.roi_percentage,
            "cost_savings": self.cost_savings,
            "time_savings_hours": self.time_savings_hours,
            "recommendations": self.recommendations,
        }


class LearningEvaluation:
    """
    Learning Effectiveness Evaluation System.
    
    Evaluates:
    - Metric trends and improvements
    - ROI calculations
    - Cost/time savings
    - Strategy effectiveness
    
    Example:
        >>> evaluation = LearningEvaluation()
        >>> 
        >>> # Record metrics
        >>> evaluation.record_metric("satisfaction", 0.85)
        >>> evaluation.record_metric("accuracy", 0.92)
        >>> 
        >>> # Evaluate
        >>> result = evaluation.evaluate(period_days=7)
        >>> print(f"Overall score: {result.overall_score:.2f}")
        >>> print(f"ROI: {result.roi_percentage:.1f}%")
    """
    
    # Default metric weights for overall score
    DEFAULT_WEIGHTS = {
        "conversion": 0.25,
        "satisfaction": 0.30,
        "efficiency": 0.20,
        "accuracy": 0.15,
        "engagement": 0.10,
    }
    
    # Baseline values for ROI calculation
    BASELINE_SATISFACTION = 0.70      # 70% baseline satisfaction
    BASELINE_EFFICIENCY = 0.50        # 50% baseline efficiency
    COST_PER_INTERACTION = 0.10       # $0.10 per AI interaction
    TIME_SAVED_PER_IMPROVEMENT = 0.05  # 3 minutes per 1% improvement
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize LearningEvaluation.
        
        Args:
            data_dir: Directory for storing evaluation data
        """
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data")
        
        # Metric storage
        self._metrics: Dict[str, List[MetricDataPoint]] = {}
        
        # Evaluation history
        self._evaluations: List[EvaluationResult] = []
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def record_metric(
        self,
        metric_type: str,
        value: float,
        context: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> None:
        """
        Record a metric data point.
        
        Args:
            metric_type: Type of metric (e.g., "satisfaction", "accuracy")
            value: Metric value (0.0 to 1.0 recommended)
            context: Additional context
            timestamp: Timestamp (defaults to now)
        """
        if metric_type not in self._metrics:
            self._metrics[metric_type] = []
        
        self._metrics[metric_type].append(MetricDataPoint(
            timestamp=timestamp or datetime.now().isoformat(),
            value=value,
            metric_type=metric_type,
            context=context or {},
        ))
    
    def record_metrics_batch(
        self,
        metrics: Dict[str, float],
        context: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> None:
        """
        Record multiple metrics at once.
        
        Args:
            metrics: Dictionary of metric_type -> value
            context: Additional context for all metrics
            timestamp: Timestamp (defaults to now)
        """
        ts = timestamp or datetime.now().isoformat()
        for metric_type, value in metrics.items():
            self.record_metric(metric_type, value, context, ts)
    
    def evaluate(
        self,
        period_days: int = 7,
        evaluation_id: Optional[str] = None,
    ) -> EvaluationResult:
        """
        Evaluate learning effectiveness for a period.
        
        Args:
            period_days: Number of days to evaluate
            evaluation_id: Optional evaluation ID
        
        Returns:
            EvaluationResult
        """
        now = datetime.now()
        period_start = (now - timedelta(days=period_days)).isoformat()
        period_end = now.isoformat()
        
        # Generate evaluation ID
        if evaluation_id is None:
            evaluation_id = f"eval_{now.strftime('%Y%m%d%H%M%S')}"
        
        # Calculate metric summaries
        metric_summaries = {}
        for metric_type, data_points in self._metrics.items():
            summary = self._calculate_metric_summary(
                metric_type, data_points, period_start, period_end
            )
            if summary:
                metric_summaries[metric_type] = summary
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metric_summaries)
        
        # Determine overall trend
        overall_trend = self._determine_overall_trend(metric_summaries)
        
        # Calculate ROI
        roi, cost_savings, time_savings = self._calculate_roi(
            metric_summaries, period_days
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            metric_summaries, overall_score, overall_trend
        )
        
        result = EvaluationResult(
            evaluation_id=evaluation_id,
            evaluated_at=now.isoformat(),
            period_start=period_start,
            period_end=period_end,
            metrics=metric_summaries,
            overall_score=overall_score,
            overall_trend=overall_trend,
            roi_percentage=roi,
            cost_savings=cost_savings,
            time_savings=time_savings,
            recommendations=recommendations,
        )
        
        self._evaluations.append(result)
        
        return result
    
    def _calculate_metric_summary(
        self,
        metric_type: str,
        data_points: List[MetricDataPoint],
        period_start: str,
        period_end: str,
    ) -> Optional[MetricSummary]:
        """
        Calculate summary statistics for a metric.
        
        Args:
            metric_type: Type of metric
            data_points: List of data points
            period_start: Period start time
            period_end: Period end time
        
        Returns:
            MetricSummary or None if no data in period
        """
        import math
        
        # Filter data points in period
        start_dt = datetime.fromisoformat(period_start)
        end_dt = datetime.fromisoformat(period_end)
        
        period_points = [
            dp for dp in data_points
            if start_dt <= datetime.fromisoformat(dp.timestamp) <= end_dt
        ]
        
        if not period_points:
            return None
        
        values = [dp.value for dp in period_points]
        count = len(values)
        mean = sum(values) / count
        
        # Standard deviation
        if count > 1:
            variance = sum((v - mean) ** 2 for v in values) / (count - 1)
            std_dev = math.sqrt(variance)
        else:
            std_dev = 0.0
        
        min_value = min(values)
        max_value = max(values)
        
        # Calculate trend
        if count >= 2:
            first_half = values[:count//2]
            second_half = values[count//2:]
            first_mean = sum(first_half) / len(first_half)
            second_mean = sum(second_half) / len(second_half)
            
            if second_mean > first_mean * 1.05:
                trend = "up"
            elif second_mean < first_mean * 0.95:
                trend = "down"
            else:
                trend = "stable"
            
            # Improvement rate
            if first_mean > 0:
                improvement_rate = (second_mean - first_mean) / first_mean * 100
            else:
                improvement_rate = 0.0
        else:
            trend = "stable"
            improvement_rate = 0.0
        
        return MetricSummary(
            metric_type=metric_type,
            count=count,
            mean=mean,
            std_dev=std_dev,
            min_value=min_value,
            max_value=max_value,
            trend=trend,
            improvement_rate=improvement_rate,
        )
    
    def _calculate_overall_score(
        self,
        metric_summaries: Dict[str, MetricSummary],
    ) -> float:
        """
        Calculate overall effectiveness score.
        
        Args:
            metric_summaries: Dictionary of metric summaries
        
        Returns:
            Overall score (0.0 to 1.0)
        """
        if not metric_summaries:
            return 0.0
        
        weighted_sum = 0.0
        weight_total = 0.0
        
        for metric_type, summary in metric_summaries.items():
            weight = self.DEFAULT_WEIGHTS.get(metric_type, 0.1)
            weighted_sum += summary.mean * weight
            weight_total += weight
        
        if weight_total > 0:
            return weighted_sum / weight_total
        return 0.0
    
    def _determine_overall_trend(
        self,
        metric_summaries: Dict[str, MetricSummary],
    ) -> str:
        """
        Determine overall trend from metric summaries.
        
        Args:
            metric_summaries: Dictionary of metric summaries
        
        Returns:
            "improving", "declining", or "stable"
        """
        if not metric_summaries:
            return "stable"
        
        up_count = sum(1 for s in metric_summaries.values() if s.trend == "up")
        down_count = sum(1 for s in metric_summaries.values() if s.trend == "down")
        
        if up_count > down_count:
            return "improving"
        elif down_count > up_count:
            return "declining"
        return "stable"
    
    def _calculate_roi(
        self,
        metric_summaries: Dict[str, MetricSummary],
        period_days: int,
    ) -> tuple:
        """
        Calculate ROI metrics.
        
        Args:
            metric_summaries: Dictionary of metric summaries
            period_days: Number of days in period
        
        Returns:
            (roi_percentage, cost_savings, time_savings_hours)
        """
        cost_savings = 0.0
        time_savings_hours = 0.0
        
        # Calculate savings from satisfaction improvement
        if "satisfaction" in metric_summaries:
            satisfaction = metric_summaries["satisfaction"]
            improvement = satisfaction.mean - self.BASELINE_SATISFACTION
            if improvement > 0:
                # Assume 100 interactions per day
                interactions = 100 * period_days
                cost_savings += improvement * interactions * self.COST_PER_INTERACTION
        
        # Calculate savings from efficiency improvement
        if "efficiency" in metric_summaries:
            efficiency = metric_summaries["efficiency"]
            improvement = efficiency.mean - self.BASELINE_EFFICIENCY
            if improvement > 0:
                # Time saved per interaction
                time_savings_hours = improvement * period_days * 8  # 8 hours/day
        
        # Calculate ROI percentage
        # Assume baseline cost is $100/day
        baseline_cost = 100 * period_days
        if baseline_cost > 0:
            roi = (cost_savings / baseline_cost) * 100
        else:
            roi = 0.0
        
        return (roi, cost_savings, time_savings_hours)
    
    def _generate_recommendations(
        self,
        metric_summaries: Dict[str, MetricSummary],
        overall_score: float,
        overall_trend: str,
    ) -> List[str]:
        """
        Generate recommendations based on metrics.
        
        Args:
            metric_summaries: Dictionary of metric summaries
            overall_score: Overall effectiveness score
            overall_trend: Overall trend
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Overall assessment
        if overall_trend == "improving":
            recommendations.append("Learning strategy is improving. Continue current approach.")
        elif overall_trend == "declining":
            recommendations.append("Learning strategy is declining. Review recent changes.")
        else:
            recommendations.append("Learning strategy is stable. Consider optimization experiments.")
        
        # Metric-specific recommendations
        for metric_type, summary in metric_summaries.items():
            if summary.trend == "down":
                recommendations.append(
                    f"{metric_type.capitalize()} is declining ({summary.improvement_rate:.1f}%). "
                    f"Investigate potential causes."
                )
            elif summary.trend == "up" and summary.improvement_rate > 10:
                recommendations.append(
                    f"{metric_type.capitalize()} improved significantly ({summary.improvement_rate:.1f}%). "
                    f"Document successful approach."
                )
        
        # Score-based recommendations
        if overall_score < 0.6:
            recommendations.append(
                "Overall score is below 60%. Consider fundamental strategy changes."
            )
        elif overall_score > 0.8:
            recommendations.append(
                "Overall score is above 80%. Strategy is performing well."
            )
        
        return recommendations
    
    def get_metric_history(
        self,
        metric_type: str,
        period_days: Optional[int] = None,
    ) -> List[MetricDataPoint]:
        """
        Get history for a specific metric.
        
        Args:
            metric_type: Type of metric
            period_days: Number of days to include (optional)
        
        Returns:
            List of metric data points
        """
        data_points = self._metrics.get(metric_type, [])
        
        if period_days is None:
            return data_points.copy()
        
        cutoff = datetime.now() - timedelta(days=period_days)
        return [
            dp for dp in data_points
            if datetime.fromisoformat(dp.timestamp) >= cutoff
        ]
    
    def get_evaluation_history(
        self,
        limit: Optional[int] = None,
    ) -> List[EvaluationResult]:
        """
        Get evaluation history.
        
        Args:
            limit: Maximum number of results
        
        Returns:
            List of evaluation results
        """
        if limit:
            return self._evaluations[-limit:]
        return self._evaluations.copy()
    
    def generate_report(
        self,
        period_days: int = 7,
        format: str = "markdown",
    ) -> str:
        """
        Generate a formatted evaluation report.
        
        Args:
            period_days: Number of days to evaluate
            format: Output format ("markdown" or "json")
        
        Returns:
            Formatted report
        """
        result = self.evaluate(period_days)
        
        if format == "json":
            return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        
        # Markdown format
        lines = [
            f"# Learning Effectiveness Report",
            f"",
            f"**Evaluation ID:** {result.evaluation_id}",
            f"**Period:** {result.period_start} to {result.period_end}",
            f"",
            f"## Overall Assessment",
            f"",
            f"- **Overall Score:** {result.overall_score:.1%}",
            f"- **Trend:** {result.overall_trend}",
            f"- **ROI:** {result.roi_percentage:.1f}%",
            f"",
            f"## Metrics Summary",
            f"",
        ]
        
        for metric_type, summary in result.metrics.items():
            lines.extend([
                f"### {metric_type.capitalize()}",
                f"",
                f"- **Mean:** {summary.mean:.2f}",
                f"- **Std Dev:** {summary.std_dev:.2f}",
                f"- **Range:** {summary.min_value:.2f} - {summary.max_value:.2f}",
                f"- **Trend:** {summary.trend} ({summary.improvement_rate:+.1f}%)",
                f"- **Data Points:** {summary.count}",
                f"",
            ])
        
        lines.extend([
            f"## ROI Metrics",
            f"",
            f"- **Cost Savings:** ${result.cost_savings:.2f}",
            f"- **Time Savings:** {result.time_savings_hours:.1f} hours",
            f"",
            f"## Recommendations",
            f"",
        ])
        
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {rec}")
        
        return "\n".join(lines)
    
    def clear_metrics(self, metric_type: Optional[str] = None) -> None:
        """
        Clear recorded metrics.
        
        Args:
            metric_type: Specific metric to clear, or None for all
        """
        if metric_type:
            self._metrics.pop(metric_type, None)
        else:
            self._metrics.clear()
