"""Tests for Friday experience optimization — claw-rl modules."""
import pytest
from claw_rl.incremental_learner import IncrementalLearner
from claw_rl.chinese_feedback import ChineseFeedbackParser, FeedbackSignal
from claw_rl.stable_injector import StableRuleInjector


class TestIncrementalLearner:
    def setup_method(self):
        self.il = IncrementalLearner(merge_interval=0)  # always merge

    def test_learn_immediate_high_priority(self):
        rule = self.il.learn_immediate({"action": "fix_bug", "priority": "high", "reward": 0.9})
        assert rule is not None
        assert rule["name"] == "fix_bug"

    def test_learn_immediate_normal_queued(self):
        rule = self.il.learn_immediate({"action": "minor", "priority": "normal"})
        assert rule is None
        assert len(self.il._pending) == 1

    def test_batch_merge(self):
        self.il.learn_immediate({"action": "a", "priority": "normal"})
        self.il.learn_immediate({"action": "a", "priority": "normal"})  # duplicate
        merged = self.il.learn_batch()
        assert len(merged) >= 1


class TestChineseFeedback:
    def setup_method(self):
        self.cfp = ChineseFeedbackParser()

    def test_positive_patterns(self):
        assert self.cfp.parse("很好，就这样做") == FeedbackSignal.POSITIVE
        assert self.cfp.parse("没问题") == FeedbackSignal.POSITIVE
        assert self.cfp.parse("太棒了") == FeedbackSignal.POSITIVE

    def test_negative_patterns(self):
        assert self.cfp.parse("不对，改一下") == FeedbackSignal.NEGATIVE
        assert self.cfp.parse("这个错误需要修改") == FeedbackSignal.NEGATIVE

    def test_neutral(self):
        assert self.cfp.parse("今天天气如何") == FeedbackSignal.NEUTRAL

    def test_with_confidence(self):
        sig, conf = self.cfp.parse_with_confidence("很好很好很好")
        assert sig == FeedbackSignal.POSITIVE
        assert conf > 0.5


class TestStableInjector:
    def setup_method(self):
        self.si = StableRuleInjector()

    def test_inject_valid(self):
        assert self.si.inject_rule({"name": "test_rule", "action": "do_x"})

    def test_inject_invalid_rollback(self):
        before = len(self.si._rules)
        assert not self.si.inject_rule({"action": "no_name"})
        assert len(self.si._rules) == before

    def test_batch_inject(self):
        rules = [{"name": "r1"}, {"name": "r2"}, {"name": "r3"}]
        count = self.si.inject_batch(rules)
        assert count == 3
