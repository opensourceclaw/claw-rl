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
Objective - 目标定义
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Objective(ABC):
    """目标抽象基类"""

    def __init__(self, name: str, weight: float = 1.0, minimize: bool = False):
        self.name = name
        self.weight = weight
        self.minimize = minimize

    @abstractmethod
    def evaluate(self, solution: Dict[str, Any]) -> float:
        """评估目标值"""
        pass

    def normalize(self, value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """归一化目标值到 [0, 1]"""
        if max_val == min_val:
            return 0.5
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))


class AccuracyObjective(Objective):
    """准确率目标"""

    def __init__(self, weight: float = 1.0):
        super().__init__("accuracy", weight, minimize=False)

    def evaluate(self, solution: Dict[str, Any]) -> float:
        return solution.get("accuracy", 0.0)


class EfficiencyObjective(Objective):
    """效率目标"""

    def __init__(self, weight: float = 1.0):
        super().__init__("efficiency", weight, minimize=False)

    def evaluate(self, solution: Dict[str, Any]) -> float:
        # 效率可以是执行时间、内存使用等
        # 归一化：越低越好，所以取反
        efficiency = solution.get("efficiency", 0.0)
        return efficiency if not self.minimize else 1.0 - efficiency


class MaintainabilityObjective(Objective):
    """可维护性目标"""

    def __init__(self, weight: float = 1.0):
        super().__init__("maintainability", weight, minimize=False)

    def evaluate(self, solution: Dict[str, Any]) -> float:
        return solution.get("maintainability", 0.0)


class CompositeObjective(Objective):
    """复合目标 - 多个目标的加权和"""

    def __init__(self, name: str, objectives: list[Objective]):
        super().__init__(name, weight=1.0)
        self.objectives = objectives

    def evaluate(self, solution: Dict[str, Any]) -> float:
        total = 0.0
        for obj in self.objectives:
            total += obj.evaluate(solution) * obj.weight
        return total


def get_predefined_objectives() -> Dict[str, Objective]:
    """获取预定义目标"""
    return {
        "accuracy": AccuracyObjective(),
        "efficiency": EfficiencyObjective(),
        "maintainability": MaintainabilityObjective(),
    }


__all__ = [
    "Objective",
    "AccuracyObjective",
    "EfficiencyObjective",
    "MaintainabilityObjective",
    "CompositeObjective",
    "get_predefined_objectives",
]
