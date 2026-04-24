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
Solution - 解的数据结构
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class Solution:
    """Pareto 优化解"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parameters: Dict[str, Any] = field(default_factory=dict)
    objectives: Dict[str, float] = field(default_factory=dict)  # objective_name -> score
    objectives_normalized: Dict[str, float] = field(default_factory=dict)
    dominated: bool = False
    domination_count: int = 0
    dominated_by: List[str] = field(default_factory=list)
    crowding_distance: float = 0.0
    rank: int = 0  # Pareto 前沿等级

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Solution):
            return False
        return self.id == other.id

    def dominates(self, other: "Solution") -> bool:
        """判断是否支配另一个解"""
        if self.id == other.id:
            return False

        at_least_as_good = True
        strictly_better = False

        for obj_name, obj_value in self.objectives_normalized.items():
            other_value = other.objectives_normalized.get(obj_name, 0.0)

            if obj_value < other_value:
                at_least_as_good = False
                break
            elif obj_value > other_value:
                strictly_better = True

        return at_least_as_good and strictly_better

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "parameters": self.parameters,
            "objectives": self.objectives,
            "objectives_normalized": self.objectives_normalized,
            "dominated": self.dominated,
            "domination_count": self.domination_count,
            "dominated_by": self.dominated_by,
            "crowding_distance": self.crowding_distance,
            "rank": self.rank,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Solution":
        """从字典创建"""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            parameters=data.get("parameters", {}),
            objectives=data.get("objectives", {}),
            objectives_normalized=data.get("objectives_normalized", {}),
            dominated=data.get("dominated", False),
            domination_count=data.get("domination_count", 0),
            dominated_by=data.get("dominated_by", []),
            crowding_distance=data.get("crowding_distance", 0.0),
            rank=data.get("rank", 0),
        )


__all__ = ["Solution"]
