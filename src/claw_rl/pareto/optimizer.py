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
ParetoOptimizer - Pareto 优化器
"""

from typing import List, Dict, Any, Optional
from .solution import Solution
from .front import ParetoFront
from .objective import Objective, get_predefined_objectives


class ParetoOptimizer:
    """Pareto 多目标优化器"""

    def __init__(self, objectives: Optional[List[Objective]] = None):
        """初始化优化器

        Args:
            objectives: 目标列表，如果为 None 则使用预定义目标
        """
        if objectives is None:
            self.objectives = list(get_predefined_objectives().values())
        else:
            self.objectives = objectives

        self.front = ParetoFront()

    def optimize(
        self,
        candidates: List[Dict[str, Any]],
        normalize: bool = True
    ) -> List[Solution]:
        """执行 Pareto 优化

        Args:
            candidates: 候选解列表（字典形式）
            normalize: 是否归一化目标值

        Returns:
            List[Solution]: Pareto 最优解列表
        """
        # 转换为 Solution 对象
        solutions = []
        for cand in candidates:
            sol = Solution(
                parameters=cand.get("parameters", {}),
                objectives={obj.name: obj.evaluate(cand) for obj in self.objectives}
            )
            solutions.append(sol)

        # 归一化目标值
        if normalize:
            self._normalize_objectives(solutions)

        # 非支配排序
        self.front.non_dominated_sort(solutions)

        return self.front.get_pareto_front()

    def get_best(self, solutions: List[Solution], n: int, use_crowding: bool = True) -> List[Solution]:
        """获取 top-n 解

        Args:
            solutions: 解列表
            n: 数量
            use_crowding: 是否使用拥挤度

        Returns:
            List[Solution]: 选中的解
        """
        return self.front.select_elite(solutions, n, use_crowding)

    def _normalize_objectives(self, solutions: List[Solution]) -> None:
        """归一化所有目标值"""
        if not solutions:
            return

        # 获取每个目标的范围
        obj_ranges: Dict[str, tuple] = {}
        for obj in self.objectives:
            values = [sol.objectives.get(obj.name, 0.0) for sol in solutions]
            min_val = min(values)
            max_val = max(values)
            obj_ranges[obj.name] = (min_val, max_val)

        # 归一化
        for sol in solutions:
            sol.objectives_normalized = {}
            for obj in self.objectives:
                value = sol.objectives.get(obj.name, 0.0)
                min_val, max_val = obj_ranges[obj.name]
                normalized = obj.normalize(value, min_val, max_val)
                sol.objectives_normalized[obj.name] = normalized

    def get_statistics(self, solutions: List[Solution]) -> Dict[str, Any]:
        """获取解集的统计信息

        Args:
            solutions: 解列表

        Returns:
            Dict: 统计信息
        """
        if not solutions:
            return {"count": 0}

        stats = {
            "count": len(solutions),
            "by_rank": {},
            "avg_objectives": {},
        }

        # 按等级统计
        for sol in solutions:
            rank = sol.rank
            stats["by_rank"][rank] = stats["by_rank"].get(rank, 0) + 1

        # 平均目标值
        for obj in self.objectives:
            values = [sol.objectives.get(obj.name, 0.0) for sol in solutions]
            stats["avg_objectives"][obj.name] = sum(values) / len(values) if values else 0.0

        return stats


__all__ = ["ParetoOptimizer"]
