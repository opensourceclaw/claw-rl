"""claw-rl v2.10.0 - Training Data Generator.

Converts experiences into training examples for weight consolidation.
"""

from typing import Any, Dict, List


class TrainingDataGenerator:
    """Generate training data from experiences."""

    def generate(self, experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        examples = []
        for exp in experiences:
            content = exp.get("content", "")
            reward = exp.get("reward", 0.0)
            if content and reward > 0:
                examples.append({
                    "input": f"Task: {content[:100]}",
                    "output": "correct",
                    "weight": reward,
                })
        return examples
