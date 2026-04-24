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
ParetoFront - Pareto 前沿计算
"""

from typing import List, Dict, Any
from .solution import Solution


class ParetoFront:
    """Pareto 前沿管理器"""

    def __init__(self):
        self.fronts: Dict[int, List[Solution]] = {}

    def non_dominated_sort(self, solutions: List[Solution]) -> Dict[int, List[Solution]]:
        """非支配排序 (NSGA-II)

        Args:
            solutions: 解列表

        Returns:
            Dict[int, List[Solution]]: {rank: [solutions]}
        """
        if not solutions:
            return {}

        # 重置解的状态
        for sol in solutions:
            sol.dominated = False
            sol.domination_count = 0
            sol.dominated_by = []
            sol.rank = 0

        n = len(solutions)

        # 计算支配关系
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                if solutions[i].dominates(solutions[j]):
                    solutions[j].dominated_by.append(solutions[i].id)
                    solutions[j].domination_count += 1
                elif solutions[j].dominates(solutions[i]):
                    solutions[i].dominated = True

        # 构建前沿
        fronts: Dict[int, List[Solution]] = {}
        current_front = 0

        while True:
            front = []
            for sol in solutions:
                if sol.rank == current_front and not sol.dominated:
                    front.append(sol)

            if not front:
                break

            fronts[current_front] = front

            # 为前沿中的解标记被支配者的计数
            for sol in front:
                for dominated_id in sol.dominated_by:
                    for other in solutions:
                        if other.id == dominated_id:
                            other.domination_count -= 1
                            if other.domination_count == 0:
                                other.dominated = False  # 不再被支配
                            break

            current_front += 1

        self.fronts = fronts
        return fronts

    def crowding_distance(self, solutions: List[Solution]) -> None:
        """计算拥挤度距离

        Args:
            solutions: 同一前沿的解列表
        """
        if len(solutions) <= 2:
            for sol in solutions:
                sol.crowding_distance = float('inf')
            return

        # 获取所有目标名称
        objective_names = list(solutions[0].objectives_normalized.keys())

        for sol in solutions:
            sol.crowding_distance = 0.0

        for obj_name in objective_names:
            # 按目标值排序
            sorted_sols = sorted(solutions, key=lambda s: s.objectives_normalized.get(obj_name, 0))

            # 边界解的拥挤度为无穷大
            sorted_sols[0].crowding_distance = float('inf')
            sorted_sols[-1].crowding_distance = float('inf')

            # 获取目标值范围
            min_val = sorted_sols[0].objectives_normalized.get(obj_name, 0)
            max_val = sorted_sols[-1].objectives_normalized.get(obj_name, 0)
            range_val = max_val - min_val

            if range_val == 0:
                continue

            # 计算中间解的拥挤度
            for i in range(1, len(sorted_sols) - 1):
                prev_val = sorted_sols[i - 1].objectives_normalized.get(obj_name, 0)
                next_val = sorted_sols[i + 1].objectives_normalized.get(obj_name, 0)
                sorted_sols[i].crowding_distance += (next_val - prev_val) / range_val

    def select_elite(
        self,
        solutions: List[Solution],
        n: int,
        use_crowding: bool = True
    ) -> List[Solution]:
        """精英选择

        Args:
            solutions: 候选解列表
            n: 选择数量
            use_crowding: 是否使用拥挤度距离

        Returns:
            List[Solution]: 选中的解
        """
        if not solutions:
            return []

        # 非支配排序
        self.non_dominated_sort(solutions)

        selected: List[Solution] = []
        remaining = n

        # 按前沿等级依次选择
        front_idx = 0
        while remaining > 0 and front_idx in self.fronts:
            front = self.fronts[front_idx]

            if len(front) <= remaining:
                selected.extend(front)
                remaining -= len(front)
            else:
                # 需要从当前前沿选择部分解
                if use_crowding:
                    self.crowding_distance(front)
                    # 按拥挤度降序排序
                    front_sorted = sorted(
                        front,
                        key=lambda s: s.crowding_distance if s.crowding_distance != float('inf') else -1,
                        reverse=True
                    )
                    selected.extend(front_sorted[:remaining])
                else:
                    selected.extend(front[:remaining])
                remaining = 0

            front_idx += 1

        return selected

    def get_pareto_front(self) -> List[Solution]:
        """获取第一前沿（Pareto 最优解）"""
        return self.fronts.get(0, [])


__all__ = ["ParetoFront"]
