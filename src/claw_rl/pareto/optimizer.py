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
ParetoOptimizer - Pareto optimize器
"""

from typing import List, Dict, Any, Optional
from .solution import Solution
from .front import ParetoFront
from .objective import Objective, get_predefined_objectives


class ParetoOptimizer:
    """Pareto 多objectiveoptimize器"""

    def __init__(self, objectives: Optional[List[Objective]] = None):
        """initializeoptimize器

        Args:
            objectives: objectivelist，if为 None then使用预定义objective
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
        """execute Pareto optimize

        Args:
            candidates: 候选solutionlist（dict形式）
            normalize: 是否normalizeobjectivevalue

        Returns:
            List[Solution]: Pareto 最优solutionlist
        """
        # convert为 Solution object
        solutions = []
        for cand in candidates:
            sol = Solution(
                parameters=cand.get("parameters", {}),
                objectives={obj.name: obj.evaluate(cand) for obj in self.objectives}
            )
            solutions.append(sol)

        # normalizeobjectivevalue
        if normalize:
            self._normalize_objectives(solutions)

        # non-dominated sorting
        self.front.non_dominated_sort(solutions)

        return self.front.get_pareto_front()

    def get_best(self, solutions: List[Solution], n: int, use_crowding: bool = True) -> List[Solution]:
        """get top-n solution

        Args:
            solutions: solutionlist
            n: count
            use_crowding: 是否使用拥挤degree

        Returns:
            List[Solution]: 选中的solution
        """
        return self.front.select_elite(solutions, n, use_crowding)

    def _normalize_objectives(self, solutions: List[Solution]) -> None:
        """normalize所有objectivevalue"""
        if not solutions:
            return

        # get每个objective的范围
        obj_ranges: Dict[str, tuple] = {}
        for obj in self.objectives:
            values = [sol.objectives.get(obj.name, 0.0) for sol in solutions]
            min_val = min(values)
            max_val = max(values)
            obj_ranges[obj.name] = (min_val, max_val)

        # normalize
        for sol in solutions:
            sol.objectives_normalized = {}
            for obj in self.objectives:
                value = sol.objectives.get(obj.name, 0.0)
                min_val, max_val = obj_ranges[obj.name]
                normalized = obj.normalize(value, min_val, max_val)
                sol.objectives_normalized[obj.name] = normalized

    def get_statistics(self, solutions: List[Solution]) -> Dict[str, Any]:
        """getsolution集的statisticsinfo

        Args:
            solutions: solutionlist

        Returns:
            Dict: statisticsinfo
        """
        if not solutions:
            return {"count": 0}

        stats = {
            "count": len(solutions),
            "by_rank": {},
            "avg_objectives": {},
        }

        # 按等级statistics
        for sol in solutions:
            rank = sol.rank
            stats["by_rank"][rank] = stats["by_rank"].get(rank, 0) + 1

        # 平均objectivevalue
        for obj in self.objectives:
            values = [sol.objectives.get(obj.name, 0.0) for sol in solutions]
            stats["avg_objectives"][obj.name] = sum(values) / len(values) if values else 0.0

        return stats


__all__ = ["ParetoOptimizer"]
