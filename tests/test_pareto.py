#!/usr/bin/env python3
"""
Tests for Pareto Multi-Objective Optimization Module
"""

import pytest
from claw_rl.pareto.objective import (
    Objective,
    AccuracyObjective,
    EfficiencyObjective,
    MaintainabilityObjective,
    CompositeObjective,
    get_predefined_objectives,
)
from claw_rl.pareto.solution import Solution
from claw_rl.pareto.front import ParetoFront
from claw_rl.pareto.optimizer import ParetoOptimizer


class TestObjective:
    """Test Objective base class"""

    def test_normalize(self):
        """Test normalization to [0, 1] range."""
        # Create a concrete subclass for testing
        class ConcreteObjective(Objective):
            def evaluate(self, solution):
                return 0.5

        obj = ConcreteObjective("test")

        # Normal case
        assert obj.normalize(0.5, 0.0, 1.0) == 0.5

        # Clamp to 0
        assert obj.normalize(-0.5, 0.0, 1.0) == 0.0

        # Clamp to 1
        assert obj.normalize(1.5, 0.0, 1.0) == 1.0

        # Equal min/max returns 0.5
        assert obj.normalize(0.5, 0.5, 0.5) == 0.5


class TestAccuracyObjective:
    """Test AccuracyObjective"""

    def test_accuracy_evaluation(self):
        """Test accuracy evaluation from solution."""
        obj = AccuracyObjective(weight=2.0)

        solution = {"accuracy": 0.85}
        assert obj.evaluate(solution) == 0.85

        # Default value
        assert obj.evaluate({}) == 0.0


class TestEfficiencyObjective:
    """Test EfficiencyObjective"""

    def test_efficiency_evaluation(self):
        """Test efficiency evaluation."""
        obj = EfficiencyObjective()

        solution = {"efficiency": 0.9}
        assert obj.evaluate(solution) == 0.9


class TestMaintainabilityObjective:
    """Test MaintainabilityObjective"""

    def test_maintainability_evaluation(self):
        """Test maintainability evaluation."""
        obj = MaintainabilityObjective()

        solution = {"maintainability": 0.75}
        assert obj.evaluate(solution) == 0.75

        # Default value
        assert obj.evaluate({}) == 0.0


class TestCompositeObjective:
    """Test CompositeObjective"""

    def test_composite_evaluation(self):
        """Test composite objective evaluation."""
        acc_obj = AccuracyObjective(weight=0.6)
        eff_obj = EfficiencyObjective(weight=0.4)

        composite = CompositeObjective("combined", [acc_obj, eff_obj])

        solution = {"accuracy": 0.8, "efficiency": 0.7}
        # 0.8 * 0.6 + 0.7 * 0.4 = 0.48 + 0.28 = 0.76
        assert composite.evaluate(solution) == 0.76


class TestGetPredefinedObjectives:
    """Test get_predefined_objectives"""

    def test_returns_all_objectives(self):
        """Test returns all predefined objectives."""
        objectives = get_predefined_objectives()

        assert "accuracy" in objectives
        assert "efficiency" in objectives
        assert "maintainability" in objectives
        assert len(objectives) == 3


class TestSolution:
    """Test Solution data class"""

    def test_solution_creation(self):
        """Test solution creation."""
        sol = Solution(
            parameters={"lr": 0.01},
            objectives={"accuracy": 0.9, "efficiency": 0.8}
        )

        assert sol.parameters == {"lr": 0.01}
        assert sol.objectives == {"accuracy": 0.9, "efficiency": 0.8}
        assert sol.dominated is False
        assert sol.domination_count == 0
        assert sol.crowding_distance == 0.0
        assert sol.rank == 0
        assert sol.id is not None

    def test_solution_hash(self):
        """Test solution hash."""
        sol1 = Solution(id="test-1")
        sol2 = Solution(id="test-1")
        sol3 = Solution(id="test-2")

        assert hash(sol1) == hash(sol2)
        assert hash(sol1) != hash(sol3)

    def test_solution_equality(self):
        """Test solution equality."""
        sol1 = Solution(id="test-1")
        sol2 = Solution(id="test-1")
        sol3 = Solution(id="test-2")

        assert sol1 == sol2
        assert sol1 != sol3
        assert sol1 != "not a solution"

    def test_solution_dominates(self):
        """Test domination relationship."""
        sol1 = Solution(
            objectives_normalized={"accuracy": 0.9, "efficiency": 0.8}
        )
        sol2 = Solution(
            objectives_normalized={"accuracy": 0.7, "efficiency": 0.6}
        )

        assert sol1.dominates(sol2) is True
        assert sol2.dominates(sol1) is False
        assert sol1.dominates(sol1) is False  # Same ID

    def test_solution_dominates_equal(self):
        """Test domination when objectives are equal."""
        sol1 = Solution(
            objectives_normalized={"accuracy": 0.8, "efficiency": 0.8}
        )
        sol2 = Solution(
            objectives_normalized={"accuracy": 0.8, "efficiency": 0.8}
        )

        # Equal objectives should not dominate each other
        assert sol1.dominates(sol2) is False

    def test_solution_to_dict(self):
        """Test solution to dict conversion."""
        sol = Solution(
            id="test-id",
            parameters={"lr": 0.01},
            objectives={"accuracy": 0.9},
            objectives_normalized={"accuracy": 0.9},
            dominated=True,
            domination_count=2,
            dominated_by=["id1", "id2"],
            crowding_distance=1.5,
            rank=1
        )

        d = sol.to_dict()

        assert d["id"] == "test-id"
        assert d["parameters"] == {"lr": 0.01}
        assert d["objectives"] == {"accuracy": 0.9}
        assert d["dominated"] is True
        assert d["rank"] == 1

    def test_solution_from_dict(self):
        """Test solution from dict creation."""
        data = {
            "id": "test-id",
            "parameters": {"lr": 0.01},
            "objectives": {"accuracy": 0.9},
            "rank": 2
        }

        sol = Solution.from_dict(data)

        assert sol.id == "test-id"
        assert sol.parameters == {"lr": 0.01}
        assert sol.objectives == {"accuracy": 0.9}
        assert sol.rank == 2


class TestParetoFront:
    """Test ParetoFront"""

    def test_non_dominated_sort_empty(self):
        """Test non-dominated sort with empty list."""
        front = ParetoFront()
        result = front.non_dominated_sort([])

        assert result == {}

    def test_non_dominated_sort_single(self):
        """Test non-dominated sort with single solution."""
        front = ParetoFront()
        sol = Solution(objectives_normalized={"accuracy": 0.9})

        result = front.non_dominated_sort([sol])

        assert 0 in result
        assert sol in result[0]
        assert sol.rank == 0

    def test_non_dominated_sort_two_solutions(self):
        """Test non-dominated sort with two solutions."""
        front = ParetoFront()
        sol1 = Solution(
            id="sol1",
            objectives_normalized={"accuracy": 0.9, "efficiency": 0.8}
        )
        sol2 = Solution(
            id="sol2",
            objectives_normalized={"accuracy": 0.7, "efficiency": 0.6}
        )

        result = front.non_dominated_sort([sol1, sol2])

        # sol1 should dominate sol2
        assert sol1 in result[0]
        # sol2 should be in a later front (dominated)
        assert sol2 in result.get(1, []) or sol2.dominated

    def test_non_dominated_sort_no_domination(self):
        """Test non-dominated sort with non-dominated solutions."""
        front = ParetoFront()
        # One is better in accuracy, one is better in efficiency
        sol1 = Solution(
            id="sol1",
            objectives_normalized={"accuracy": 0.9, "efficiency": 0.3}
        )
        sol2 = Solution(
            id="sol2",
            objectives_normalized={"accuracy": 0.3, "efficiency": 0.9}
        )

        result = front.non_dominated_sort([sol1, sol2])

        # Both should be in front 0 (non-dominated)
        assert len(result[0]) == 2

    def test_crowding_distance_single(self):
        """Test crowding distance with single solution."""
        front = ParetoFront()
        sol = Solution(objectives_normalized={"accuracy": 0.9})

        front.crowding_distance([sol])

        assert sol.crowding_distance == float('inf')

    def test_crowding_distance_two(self):
        """Test crowding distance with two solutions."""
        front = ParetoFront()
        sol1 = Solution(objectives_normalized={"accuracy": 0.9})
        sol2 = Solution(objectives_normalized={"accuracy": 0.3})

        front.crowding_distance([sol1, sol2])

        # Two solutions should have infinite crowding distance
        assert sol1.crowding_distance == float('inf')
        assert sol2.crowding_distance == float('inf')

    def test_crowding_distance_multiple(self):
        """Test crowding distance with multiple solutions."""
        front = ParetoFront()
        solutions = [
            Solution(
                id=f"sol{i}",
                objectives_normalized={"accuracy": i * 0.25}
            )
            for i in range(5)
        ]

        front.crowding_distance(solutions)

        # Boundary solutions should have infinite distance
        assert solutions[0].crowding_distance == float('inf')
        assert solutions[4].crowding_distance == float('inf')

        # Middle solutions should have finite distance
        assert solutions[1].crowding_distance != float('inf')
        assert solutions[2].crowding_distance != float('inf')
        assert solutions[3].crowding_distance != float('inf')

    def test_select_elite_empty(self):
        """Test elite selection with empty list."""
        front = ParetoFront()
        result = front.select_elite([], 5)

        assert result == []

    def test_select_elite_basic(self):
        """Test elite selection."""
        front = ParetoFront()
        solutions = [
            Solution(
                id="sol1",
                objectives_normalized={"accuracy": 0.9, "efficiency": 0.9}
            ),
            Solution(
                id="sol2",
                objectives_normalized={"accuracy": 0.7, "efficiency": 0.7}
            ),
            Solution(
                id="sol3",
                objectives_normalized={"accuracy": 0.5, "efficiency": 0.5}
            ),
        ]

        selected = front.select_elite(solutions, 2)

        # Should select at least 1 solution (both sol1 and sol2 are non-dominated)
        assert len(selected) >= 1

    def test_get_pareto_front(self):
        """Test get Pareto front."""
        front = ParetoFront()
        sol1 = Solution(
            id="sol1",
            objectives_normalized={"accuracy": 0.9}
        )
        sol2 = Solution(
            id="sol2",
            objectives_normalized={"accuracy": 0.7}
        )

        front.non_dominated_sort([sol1, sol2])
        pareto = front.get_pareto_front()

        assert sol1 in pareto


class TestParetoOptimizer:
    """Test ParetoOptimizer"""

    def test_optimizer_creation(self):
        """Test optimizer creation."""
        optimizer = ParetoOptimizer()

        assert len(optimizer.objectives) == 3  # Default objectives
        assert optimizer.front is not None

    def test_optimizer_custom_objectives(self):
        """Test optimizer with custom objectives."""
        objectives = [AccuracyObjective()]
        optimizer = ParetoOptimizer(objectives=objectives)

        assert len(optimizer.objectives) == 1

    def test_optimize_basic(self):
        """Test basic optimization."""
        optimizer = ParetoOptimizer()

        candidates = [
            {"parameters": {"lr": 0.01}, "accuracy": 0.9, "efficiency": 0.8, "maintainability": 0.7},
            {"parameters": {"lr": 0.001}, "accuracy": 0.8, "efficiency": 0.9, "maintainability": 0.6},
        ]

        pareto_solutions = optimizer.optimize(candidates)

        assert len(pareto_solutions) > 0
        assert all(isinstance(sol, Solution) for sol in pareto_solutions)

    def test_optimize_empty(self):
        """Test optimization with empty candidates."""
        optimizer = ParetoOptimizer()

        result = optimizer.optimize([])

        assert result == []

    def test_optimize_no_normalize(self):
        """Test optimization without normalization."""
        optimizer = ParetoOptimizer()

        candidates = [
            {"parameters": {}, "accuracy": 0.9, "efficiency": 0.8, "maintainability": 0.7},
        ]

        pareto_solutions = optimizer.optimize(candidates, normalize=False)

        assert len(pareto_solutions) == 1
        # Objectives should not be normalized
        assert pareto_solutions[0].objectives_normalized == {}

    def test_get_best(self):
        """Test get best solutions."""
        optimizer = ParetoOptimizer()

        solutions = [
            Solution(
                id="sol1",
                objectives={"accuracy": 0.9, "efficiency": 0.8},
                objectives_normalized={"accuracy": 0.9, "efficiency": 0.8},
                rank=0
            ),
            Solution(
                id="sol2",
                objectives={"accuracy": 0.8, "efficiency": 0.9},
                objectives_normalized={"accuracy": 0.8, "efficiency": 0.9},
                rank=0
            ),
            Solution(
                id="sol3",
                objectives={"accuracy": 0.7, "efficiency": 0.7},
                objectives_normalized={"accuracy": 0.7, "efficiency": 0.7},
                rank=1
            ),
        ]

        best = optimizer.get_best(solutions, 2)

        assert len(best) <= 2

    def test_get_statistics_empty(self):
        """Test statistics with empty solutions."""
        optimizer = ParetoOptimizer()

        stats = optimizer.get_statistics([])

        assert stats["count"] == 0

    def test_get_statistics_basic(self):
        """Test basic statistics."""
        objectives = [AccuracyObjective(), EfficiencyObjective()]
        optimizer = ParetoOptimizer(objectives=objectives)

        solutions = [
            Solution(
                objectives={"accuracy": 0.9, "efficiency": 0.8}
            ),
            Solution(
                objectives={"accuracy": 0.7, "efficiency": 0.6}
            ),
        ]

        stats = optimizer.get_statistics(solutions)

        assert stats["count"] == 2
        assert "avg_objectives" in stats
        assert "accuracy" in stats["avg_objectives"]
        # (0.9 + 0.7) / 2 = 0.8
        assert stats["avg_objectives"]["accuracy"] == 0.8
        # (0.8 + 0.6) / 2 = 0.7
        assert stats["avg_objectives"]["efficiency"] == 0.7

    def test_normalize_objectives(self):
        """Test objective normalization."""
        optimizer = ParetoOptimizer()

        solutions = [
            Solution(objectives={"accuracy": 0.0, "efficiency": 0.2}),
            Solution(objectives={"accuracy": 0.5, "efficiency": 0.5}),
            Solution(objectives={"accuracy": 1.0, "efficiency": 0.8}),
        ]

        optimizer._normalize_objectives(solutions)

        # Check normalization
        assert solutions[0].objectives_normalized["accuracy"] == 0.0
        assert solutions[2].objectives_normalized["accuracy"] == 1.0
        assert 0.0 <= solutions[1].objectives_normalized["accuracy"] <= 1.0


class TestParetoIntegration:
    """Integration tests for Pareto module"""

    def test_full_optimization_workflow(self):
        """Test complete optimization workflow."""
        optimizer = ParetoOptimizer()

        # Generate diverse candidate solutions
        candidates = []
        for acc in [0.5, 0.6, 0.7, 0.8, 0.9]:
            for eff in [0.5, 0.6, 0.7, 0.8, 0.9]:
                for maint in [0.5, 0.6, 0.7, 0.8, 0.9]:
                    candidates.append({
                        "parameters": {
                            "accuracy": acc,
                            "efficiency": eff,
                            "maintainability": maint
                        },
                        "accuracy": acc,
                        "efficiency": eff,
                        "maintainability": maint
                    })

        # Run optimization
        pareto_solutions = optimizer.optimize(candidates)

        # Should have Pareto optimal solutions
        assert len(pareto_solutions) > 0

        # Get statistics
        stats = optimizer.get_statistics(pareto_solutions)
        assert stats["count"] == len(pareto_solutions)

        # Select top 3 using crowding distance
        top3 = optimizer.get_best(pareto_solutions, 3)
        assert len(top3) <= 3

    def test_trade_off_solutions(self):
        """Test that trade-off solutions are preserved."""
        optimizer = ParetoOptimizer()

        # Create candidates with different trade-offs
        candidates = [
            # High accuracy, low efficiency
            {"parameters": {"name": "A"}, "accuracy": 0.9, "efficiency": 0.3, "maintainability": 0.5},
            # Low accuracy, high efficiency
            {"parameters": {"name": "B"}, "accuracy": 0.3, "efficiency": 0.9, "maintainability": 0.5},
            # Balanced
            {"parameters": {"name": "C"}, "accuracy": 0.6, "efficiency": 0.6, "maintainability": 0.6},
            # Dominated by C
            {"parameters": {"name": "D"}, "accuracy": 0.5, "efficiency": 0.5, "maintainability": 0.5},
        ]

        pareto_solutions = optimizer.optimize(candidates)

        # A, B, C should be non-dominated (different trade-offs)
        # D is dominated by C
        assert len(pareto_solutions) >= 3