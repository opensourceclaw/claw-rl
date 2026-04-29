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
Learning Observability Dashboard
Web-based dashboard for visualizing claw-rl learning metrics
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Optional Flask import
try:
    from flask import Flask, render_template_string, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class LearningDashboard:
    """Learning Observability Dashboard

    Features:
    - Real-time metrics display
    - Rule effectiveness visualization
    - Reward distribution charts
    - Learning progress tracking
    - Static HTML report generation
    """

    def __init__(self, port: int = 5000, host: str = "0.0.0.0"):
        """Initialize dashboard

        Args:
            port: Server port
            host: Server host
        """
        self.port = port
        self.host = host
        self.app = None
        self.metrics = {
            "rewards": [],
            "rules": [],
            "hints": [],
            "llm_calls": [],
            "latencies": [],
            "mab_selections": []
        }

        # HTML template
        self.html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>claw-rl Learning Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #333;
        }
        h1 { font-size: 2em; background: linear-gradient(90deg, #00d4ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .timestamp { color: #888; font-size: 0.9em; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 {
            font-size: 1.1em;
            color: #00d4ff;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .stat:last-child { border-bottom: none; }
        .stat-label { color: #888; }
        .stat-value { font-weight: bold; color: #00ff88; }
        .stat-value.warning { color: #ffaa00; }
        .stat-value.error { color: #ff4444; }
        .chart-container { height: 200px; position: relative; }
        .progress-bar {
            height: 8px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            transition: width 0.5s ease;
        }
        .rule-list { max-height: 300px; overflow-y: auto; }
        .rule-item {
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .rule-id { color: #00d4ff; font-size: 0.9em; }
        .rule-confidence {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
        }
        .high { background: rgba(0,255,136,0.2); color: #00ff88; }
        .medium { background: rgba(255,170,0,0.2); color: #ffaa00; }
        .low { background: rgba(255,68,68,0.2); color: #ff4444; }
        .refresh-btn {
            background: linear-gradient(90deg, #00d4ff, #7b2ff7);
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }
        .refresh-btn:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>claw-rl Learning Dashboard</h1>
                <p class="timestamp">Last updated: {{ timestamp }}</p>
            </div>
            <button class="refresh-btn" onclick="location.reload()">Refresh</button>
        </header>

        <div class="grid">
            <div class="card">
                <h2>📊 Learning Progress</h2>
                <div class="stat">
                    <span class="stat-label">Total Episodes</span>
                    <span class="stat-value">{{ stats.total_episodes }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Avg Reward</span>
                    <span class="stat-value">{{ "%.3f"|format(stats.avg_reward) }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Reward Trend</span>
                    <span class="stat-value {% if stats.reward_trend > 0 %}warning{% endif %}">
                        {% if stats.reward_trend > 0 %}↑{% else %}↓{% endif %} {{ "%.1f"|format(stats.reward_trend) }}%
                    </span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ stats.learning_progress }}%"></div>
                </div>
                <p style="margin-top:10px;font-size:0.85em;color:#888">Learning Progress: {{ "%.0f"|format(stats.learning_progress) }}%</p>
            </div>

            <div class="card">
                <h2>🎯 Rule Performance</h2>
                <div class="stat">
                    <span class="stat-label">Active Rules</span>
                    <span class="stat-value">{{ stats.active_rules }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Avg Confidence</span>
                    <span class="stat-value">{{ "%.1f"|format(stats.avg_confidence) }}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Rules Updated</span>
                    <span class="stat-value">{{ stats.rules_updated }}</span>
                </div>
                <div class="chart-container">
                    <canvas id="rulesChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>🤖 LLM Performance</h2>
                <div class="stat">
                    <span class="stat-label">Total Calls</span>
                    <span class="stat-value">{{ stats.llm_calls }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Cache Hit Rate</span>
                    <span class="stat-value">{{ "%.1f"|format(stats.cache_hit_rate) }}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Avg Latency</span>
                    <span class="stat-value">{{ "%.1f"|format(stats.avg_latency) }}ms</span>
                </div>
                <div class="chart-container">
                    <canvas id="latencyChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>🎰 MAB Strategy</h2>
                <div class="stat">
                    <span class="stat-label">Current Strategy</span>
                    <span class="stat-value">{{ stats.mab_strategy }}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Exploration Rate</span>
                    <span class="stat-value">{{ "%.1f"|format(stats.exploration_rate) }}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Strategy Switches</span>
                    <span class="stat-value">{{ stats.strategy_switches }}</span>
                </div>
                <div class="chart-container">
                    <canvas id="mabChart"></canvas>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📋 Top Rules</h2>
            <div class="rule-list">
                {% for rule in top_rules %}
                <div class="rule-item">
                    <span class="rule-id">{{ rule.id }}</span>
                    <span class="rule-confidence {% if rule.confidence > 0.8 %}high{% elif rule.confidence > 0.5 %}medium{% else %}low{% endif %}">
                        {{ "%.1f"|format(rule.confidence * 100) }}%
                    </span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        // Chart configurations
        const chartConfig = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#888' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                y: { ticks: { color: '#888' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
        };

        // Rules performance chart
        new Chart(document.getElementById('rulesChart'), {
            type: 'doughnut',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    data: [{{ rules_dist.high }}, {{ rules_dist.medium }}, {{ rules_dist.low }}],
                    backgroundColor: ['#00ff88', '#ffaa00', '#ff4444']
                }]
            },
            options: { ...chartConfig, cutout: '60%' }
        });

        // Latency chart
        new Chart(document.getElementById('latencyChart'), {
            type: 'line',
            data: {
                labels: {{ latency_labels | tojson }},
                datasets: [{
                    label: 'Latency (ms)',
                    data: {{ latency_values }},
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0,212,255,0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: chartConfig
        });

        // MAB chart
        new Chart(document.getElementById('mabChart'), {
            type: 'bar',
            data: {
                labels: {{ mab_labels | tojson }},
                datasets: [{
                    label: 'Selections',
                    data: {{ mab_values }},
                    backgroundColor: ['#00d4ff', '#7b2ff7', '#00ff88']
                }]
            },
            options: chartConfig
        });
    </script>
</body>
</html>
"""

    def update_metrics(self, metrics: Dict[str, Any]):
        """Update dashboard metrics

        Args:
            metrics: Dictionary containing metric data
        """
        self.metrics.update(metrics)

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        rewards = self.metrics.get("rewards", [])
        rules = self.metrics.get("rules", [])
        latencies = self.metrics.get("latencies", [])
        llm_calls = self.metrics.get("llm_calls", [])

        # Calculate stats
        total_episodes = len(rewards)
        avg_reward = sum(rewards) / total_episodes if total_episodes > 0 else 0

        # Calculate reward trend
        if len(rewards) >= 10:
            recent = sum(rewards[-5:]) / 5
            previous = sum(rewards[-10:-5]) / 5
            reward_trend = ((recent - previous) / previous * 100) if previous > 0 else 0
        else:
            reward_trend = 0

        # Rule stats
        active_rules = len(rules)
        avg_confidence = sum(r.get("confidence", 0) for r in rules) / active_rules if active_rules > 0 else 0

        # LLM stats
        total_calls = len(llm_calls)
        cache_hits = sum(1 for c in llm_calls if c.get("cache_hit"))
        cache_hit_rate = (cache_hits / total_calls * 100) if total_calls > 0 else 0
        avg_latency = sum(l.get("latency", 0) for l in latencies) / len(latencies) if latencies else 0

        # MAB stats
        mab_selections = self.metrics.get("mab_selections", [])

        return {
            "total_episodes": total_episodes,
            "avg_reward": avg_reward,
            "reward_trend": reward_trend,
            "learning_progress": min(total_episodes / 100 * 100, 100),
            "active_rules": active_rules,
            "avg_confidence": avg_confidence * 100,
            "rules_updated": len([r for r in rules if r.get("updated")]),
            "llm_calls": total_calls,
            "cache_hit_rate": cache_hit_rate,
            "avg_latency": avg_latency,
            "mab_strategy": "epsilon-greedy",
            "exploration_rate": 0.1 * 100,
            "strategy_switches": len([s for s in mab_selections if s.get("switched")])
        }

    def get_rules_distribution(self) -> Dict[str, int]:
        """Get rule confidence distribution"""
        rules = self.metrics.get("rules", [])
        high = len([r for r in rules if r.get("confidence", 0) > 0.8])
        medium = len([r for r in rules if 0.5 < r.get("confidence", 0) <= 0.8])
        low = len([r for r in rules if r.get("confidence", 0) <= 0.5])
        return {"high": high, "medium": medium, "low": low}

    def get_latency_data(self) -> Tuple[List[str], List[float]]:
        """Get latency chart data"""
        latencies = self.metrics.get("latencies", [])[-20:]
        labels = [f"T{i+1}" for i in range(len(latencies))]
        values = [l.get("latency", 0) for l in latencies]
        return labels, values

    def get_mab_data(self) -> Tuple[List[str], List[int]]:
        """Get MAB selection data"""
        selections = self.metrics.get("mab_selections", [])
        strategy_counts = {}
        for s in selections:
            strategy = s.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        return list(strategy_counts.keys()), list(strategy_counts.values())

    def render(self) -> str:
        """Render dashboard HTML"""
        return render_template_string(
            self.html_template,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stats=self.get_stats(),
            top_rules=self.metrics.get("rules", [])[:10],
            rules_dist=self.get_rules_distribution(),
            latency_labels=self.get_latency_data()[0],
            latency_values=self.get_latency_data()[1],
            mab_labels=self.get_mab_data()[0],
            mab_values=self.get_mab_data()[1]
        )

    def run(self, debug: bool = False):
        """Run Flask server"""
        if not FLASK_AVAILABLE:
            print("Flask not available. Use generate_static_report() instead.")
            return

        app = Flask(__name__)

        @app.route("/")
        def index():
            return self.render()

        @app.route("/api/metrics")
        def api_metrics():
            return jsonify({
                "stats": self.get_stats(),
                "rules": self.metrics.get("rules", [])[:20],
                "rewards": self.metrics.get("rewards", [])[-50:]
            })

        @app.route("/api/update", methods=["POST"])
        def api_update():
            data = request.json
            self.update_metrics(data)
            return jsonify({"status": "ok"})

        print(f"Starting dashboard on http://{self.host}:{self.port}")
        app.run(host=self.host, port=self.port, debug=debug)

    def generate_static_report(self, output_path: str):
        """Generate static HTML report

        Args:
            output_path: Path to save report
        """
        html = self.render()
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html)
        print(f"Static report saved to: {output_path}")


def create_dashboard(port: int = 5000) -> LearningDashboard:
    """Create dashboard instance"""
    return LearningDashboard(port=port)


# Default instance
_dashboard: Optional[LearningDashboard] = None

def get_dashboard() -> LearningDashboard:
    """Get default dashboard instance"""
    global _dashboard
    if _dashboard is None:
        _dashboard = LearningDashboard()
    return _dashboard
