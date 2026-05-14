"""Tests for claw-rl v3.0.0 modules."""
import pytest
from claw_rl.skill_library import SkillLibrary, Skill
from claw_rl.process_reward import ProcessRewardModel, ProcessRewardResult
from claw_rl.triad import Proposer, Solver, Judge, TriadArchitecture, Task, Solution
from claw_rl.self_play import SelfPlayRL


# ── SkillLibrary ───────────────────────────────────

class TestSkillLibrary:
    def setup_method(self):
        self.lib = SkillLibrary()

    def test_add_skill(self):
        s = self.lib.add_skill("test", "debug error", "run debugger", 0.7)
        assert s.name == "test"
        assert s.reward == 0.7

    def test_find_skills(self):
        self.lib.add_skill("debug", "debug error crash", "run debugger", 0.8)
        self.lib.add_skill("test", "test coverage report", "run tests", 0.6)
        results = self.lib.find_skills("debug error", top_k=5)
        assert len(results) > 0
        assert results[0].name == "debug"

    def test_find_no_match(self):
        results = self.lib.find_skills("nonexistent query")
        assert results == []

    def test_improve_skill(self):
        s = self.lib.add_skill("learn", "improve performance", "optimize", 0.5)
        assert self.lib.improve_skill(s.id, 0.2)
        assert self.lib.get_skill(s.id).reward == 0.7

    def test_get_stats(self):
        self.lib.add_skill("a", "pattern", "action", 0.5)
        self.lib.add_skill("b", "pattern2", "action2", 0.8)
        stats = self.lib.get_stats()
        assert stats["total_skills"] == 2


# ── ProcessRewardModel ─────────────────────────────

class TestProcessRewardModel:
    def setup_method(self):
        self.prm = ProcessRewardModel()

    def test_evaluate_single_step(self):
        score = self.prm.evaluate_step("completed task successfully", 0.8)
        assert 0.0 <= score <= 1.0

    def test_evaluate_sequence(self):
        steps = [
            {"description": "planned approach", "outcome": 0.9},
            {"description": "executed successfully", "outcome": 1.0},
            {"description": "verified results", "outcome": 0.8},
        ]
        result = self.prm.evaluate_sequence(steps)
        assert result.total_steps == 3
        assert len(result.scores) == 3
        assert result.weighted_score > 0
        assert result.feedback != ""

    def test_weighted_score_empty(self):
        assert self.prm.get_weighted_score([]) == 0.0


# ── TriadArchitecture ──────────────────────────────

class TestTriad:
    def setup_method(self):
        self.triad = TriadArchitecture()

    def test_proposer_generates_task(self):
        p = Proposer()
        task = p.generate_task(0.5)
        assert task.description != ""
        assert 0.0 <= task.difficulty <= 1.0

    def test_solver_solves_task(self):
        lib = SkillLibrary()
        lib.add_skill("debug", "error crash", "run debugger", 0.9)
        solver = Solver(lib)
        task = Task(description="debug an error crash", difficulty=0.5)
        solution = solver.solve(task)
        assert len(solution.steps) > 0
        assert len(solution.skills_used) > 0

    def test_judge_evaluates(self):
        judge = Judge()
        task = Task(description="test", difficulty=0.5)
        solution = Solution(
            task=task,
            steps=[{"description": "completed task", "outcome": 0.9}],
        )
        judgement = judge.evaluate(solution)
        assert 0.0 <= judgement.score <= 1.0
        assert judgement.feedback != ""

    def test_triad_cycle(self):
        result = self.triad.run_cycle(0.5)
        assert result.task is not None
        assert result.judgement is not None
        assert result.judgement.score >= 0.0

    def test_triad_multiple_cycles(self):
        results = self.triad.run_cycles(5)
        assert len(results) == 5

    def test_triad_stats(self):
        self.triad.run_cycles(3)
        stats = self.triad.get_stats()
        assert stats["cycles"] == 3


# ── SelfPlayRL ─────────────────────────────────────

class TestSelfPlayRL:
    def setup_method(self):
        self.sp = SelfPlayRL()

    def test_run_session(self):
        result = self.sp.run_session(cycles=10, start_level=0.4)
        assert result.cycles == 10
        assert len(result.score_progression) == 10
        assert result.final_level > 0

    def test_skill_creation(self):
        result = self.sp.run_session(cycles=15)
        assert result.skills_created >= 0

    def test_latest_result(self):
        self.sp.run_session(cycles=5)
        r = self.sp.get_latest_result()
        assert r.cycles == 5
