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

"""Tests for claw-rl bridge adapter abstraction layer."""

import os
from unittest.mock import MagicMock, patch

import pytest

from claw_rl.adapters import (
    BaseBridgeStrategy,
    BridgeAdapterError,
    BridgeAdapterRegistry,
    RLBridgeAdapter,
    V1BridgeStrategy,
    V2BridgeStrategy,
)


# ---- Helpers ----------------------------------------------------------------

def _mock_learning_loop():
    ll = MagicMock()
    ll.get_recent_learnings.return_value = [
        {"hint": "test hint", "score": 0.9, "feedback": "test", "action": "action1", "reward": 1,
         "hints": [{"hint_type": "correction", "content": "fix this"}]}
    ]
    ll.get_statistics.return_value = {"total": 10, "positive": 7, "negative": 3}
    ll.process_feedback.return_value = {"reward": 1, "hints": [{"hint_type": "test", "content": "tip"}]}
    return ll


def _mock_binary_rl():
    br = MagicMock()
    br.judge.return_value = (1.0, 0.95)
    return br


def _mock_opd_hint():
    oh = MagicMock()
    hint = MagicMock()
    hint.to_dict.return_value = {"hint_type": "improvement", "content": "be better"}
    oh.extract.return_value = hint
    return oh


# ---- BaseBridgeStrategy ABC ------------------------------------------------

class TestBaseBridgeStrategy:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BaseBridgeStrategy()

    def test_default_supports(self):
        class Partial(BaseBridgeStrategy):
            def get_version(self): pass
            def get_initialize_response(self, ws): pass
            def format_collect_feedback_result(self, r, c, h): pass
            def format_extract_hint_result(self, h): pass
            def format_rules(self, l, c): pass
            def format_status(self, s, c): pass
            def format_shutdown_response(self, rc, al): pass
        s = Partial()
        assert s.supports_judge() is False
        assert s.supports_hint() is False
        assert s.supports_ping() is False


# ---- V2BridgeStrategy -------------------------------------------------------

class TestV2BridgeStrategy:
    def test_version(self):
        s = V2BridgeStrategy()
        assert s.get_version() == "2.0.0"

    def test_supports(self):
        s = V2BridgeStrategy()
        assert s.supports_judge() is True
        assert s.supports_hint() is True
        assert s.supports_ping() is False

    def test_get_initialize_response(self):
        s = V2BridgeStrategy()
        resp = s.get_initialize_response("/tmp/ws")
        assert resp["status"] == "success"
        assert resp["workspace"] == "/tmp/ws"

    def test_format_collect_feedback_result(self):
        s = V2BridgeStrategy()
        resp = s.format_collect_feedback_result(1.0, 0.95)
        assert resp["status"] == "success"
        assert resp["reward"] == 1.0
        assert resp["confidence"] == 0.95

    def test_format_collect_feedback_result_no_confidence(self):
        s = V2BridgeStrategy()
        resp = s.format_collect_feedback_result(0.5, None)
        assert resp["confidence"] == 0.0

    def test_format_extract_hint_found(self):
        s = V2BridgeStrategy()
        hint = MagicMock()
        hint.to_dict.return_value = {"type": "fix", "content": "do x"}
        resp = s.format_extract_hint_result(hint)
        assert resp["status"] == "success"
        assert resp["hint"] == {"type": "fix", "content": "do x"}

    def test_format_extract_hint_none(self):
        s = V2BridgeStrategy()
        resp = s.format_extract_hint_result(None)
        assert resp["status"] == "success"
        assert resp["hint"] is None

    def test_format_rules_from_dict(self):
        s = V2BridgeStrategy()
        learnings = [{"hint": "do better", "score": 0.8}]
        rules = s.format_rules(learnings)
        assert len(rules) == 1
        assert rules[0]["content"] == "do better"
        assert rules[0]["score"] == 0.8

    def test_format_rules_from_object(self):
        s = V2BridgeStrategy()
        rules = s.format_rules(["plain text"])
        assert len(rules) == 1
        assert rules[0]["content"] == "plain text"
        assert rules[0]["score"] == 1.0

    def test_format_rules_empty(self):
        s = V2BridgeStrategy()
        assert s.format_rules([]) == []
        assert s.format_rules(None) == []

    def test_format_status(self):
        s = V2BridgeStrategy()
        resp = s.format_status({}, {"binary_rl": True, "opd_hint": False, "learning_loop": True})
        assert resp["initialized"] is True
        assert resp["components"]["binary_rl"] is True
        assert resp["components"]["opd_hint"] is False

    def test_format_shutdown(self):
        s = V2BridgeStrategy()
        resp = s.format_shutdown_response(42, 1.5)
        assert resp["status"] == "success"
        assert resp["total_requests"] == 42
        assert resp["avg_latency_ms"] == 1.5


# ---- V1BridgeStrategy -------------------------------------------------------

class TestV1BridgeStrategy:
    def test_version(self):
        s = V1BridgeStrategy()
        assert s.get_version() == "1.0.0"

    def test_supports(self):
        s = V1BridgeStrategy()
        assert s.supports_judge() is False
        assert s.supports_hint() is False
        assert s.supports_ping() is True

    def test_get_initialize_response(self):
        s = V1BridgeStrategy()
        resp = s.get_initialize_response("/ws")
        assert resp["status"] == "ok"
        assert resp["message"] == "initialized"

    def test_format_collect_feedback_result(self):
        s = V1BridgeStrategy()
        hints = [{"hint_type": "tip", "content": "try"}]
        resp = s.format_collect_feedback_result(1, hints=hints)
        assert resp["status"] == "feedback_collected"
        assert resp["reward"] == 1
        assert resp["hints"] == hints

    def test_format_extract_hint_result(self):
        s = V1BridgeStrategy()
        resp = s.format_extract_hint_result(None)
        assert resp["status"] == "error"
        assert "not supported" in resp["error"]

    def test_format_rules(self):
        s = V1BridgeStrategy()
        learnings = [{
            "hints": [{"hint_type": "correction", "content": "fix x"}],
            "reward": 1, "feedback": "good", "action": "do x"
        }]
        rules = s.format_rules(learnings)
        assert len(rules) == 2  # one hint + one learning
        assert rules[0]["pattern"] == "correction"
        assert rules[0]["response"] == "fix x"
        assert rules[0]["source"] == "hint"
        assert rules[1]["pattern"] == "learned"
        assert rules[1]["source"] == "feedback"

    def test_format_rules_empty(self):
        s = V1BridgeStrategy()
        assert s.format_rules([]) == []

    def test_format_status(self):
        s = V1BridgeStrategy()
        resp = s.format_status({"total": 10}, {"learning_loop": True})
        assert resp["status"] == "ok"
        assert resp["initialized"] is True
        assert resp["statistics"] == {"total": 10}

    def test_format_shutdown(self):
        s = V1BridgeStrategy()
        resp = s.format_shutdown_response(10, 0.5)
        assert resp["status"] == "shutting_down"


# ---- RLBridgeAdapter --------------------------------------------------------

class TestRLBridgeAdapter:
    @pytest.fixture
    def mock_ll(self):
        return _mock_learning_loop()

    def test_version(self):
        adapter = RLBridgeAdapter(V2BridgeStrategy())
        assert adapter.version == "2.0.0"

    def test_initialized_false_before_init(self):
        adapter = RLBridgeAdapter(V2BridgeStrategy())
        assert adapter.initialized is False

    def test_initialize_v2(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            with patch("claw_rl.feedback.binary_rl.BinaryRLJudge", return_value=_mock_binary_rl()):
                with patch("claw_rl.feedback.opd_hint.OPDHintExtractor", return_value=_mock_opd_hint()):
                    adapter = RLBridgeAdapter(V2BridgeStrategy())
                    resp = adapter.initialize("/tmp/ws")
                    assert resp["status"] == "success"
                    assert adapter.initialized is True
                    assert adapter.binary_rl is not None
                    assert adapter.opd_hint is not None
                    assert adapter.learning_loop is not None

    def test_initialize_v1(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            adapter = RLBridgeAdapter(V1BridgeStrategy())
            resp = adapter.initialize("/tmp/ws")
            assert resp["status"] == "ok"
            assert adapter.initialized is True
            assert adapter.binary_rl is None
            assert adapter.opd_hint is None
            assert adapter.learning_loop is not None

    def test_collect_feedback_v2(self, mock_ll):
        mock_br = _mock_binary_rl()
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            with patch("claw_rl.feedback.binary_rl.BinaryRLJudge", return_value=mock_br):
                adapter = RLBridgeAdapter(V2BridgeStrategy())
                adapter.initialize("/tmp/ws")
                resp = adapter.collect_feedback("great job!", "action1")
                assert resp["status"] == "success"
                assert resp["reward"] == 1.0
                assert resp["confidence"] == 0.95

    def test_collect_feedback_v1(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            adapter = RLBridgeAdapter(V1BridgeStrategy())
            adapter.initialize("/tmp/ws")
            resp = adapter.collect_feedback("nice", "action1", "ctx")
            assert resp["status"] == "feedback_collected"
            assert resp["reward"] == 1
            assert "hints" in resp

    def test_collect_feedback_not_initialized(self):
        adapter = RLBridgeAdapter(V2BridgeStrategy())
        resp = adapter.collect_feedback("test")
        assert resp == {"error": "Bridge not initialized"}

    def test_extract_hint_v2(self, mock_ll):
        mock_hint = _mock_opd_hint()
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            with patch("claw_rl.feedback.binary_rl.BinaryRLJudge", return_value=_mock_binary_rl()):
                with patch("claw_rl.feedback.opd_hint.OPDHintExtractor", return_value=mock_hint):
                    adapter = RLBridgeAdapter(V2BridgeStrategy())
                    adapter.initialize("/tmp/ws")
                    resp = adapter.extract_hint("please fix x")
                    assert resp["status"] == "success"
                    assert resp["hint"] == {"hint_type": "improvement", "content": "be better"}

    def test_extract_hint_v1_unsupported(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            adapter = RLBridgeAdapter(V1BridgeStrategy())
            adapter.initialize("/tmp/ws")
            resp = adapter.extract_hint("test")
            assert resp["status"] == "error"

    def test_get_rules_v2(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            with patch("claw_rl.feedback.binary_rl.BinaryRLJudge", return_value=_mock_binary_rl()):
                with patch("claw_rl.feedback.opd_hint.OPDHintExtractor", return_value=_mock_opd_hint()):
                    adapter = RLBridgeAdapter(V2BridgeStrategy())
                    adapter.initialize("/tmp/ws")
                    resp = adapter.get_rules(top_k=5)
                    assert resp["status"] == "success"
                    assert len(resp["rules"]) == 1
                    assert resp["rules"][0]["content"] == "test hint"

    def test_get_rules_with_context(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            adapter = RLBridgeAdapter(V2BridgeStrategy())
            adapter.initialize("/tmp/ws")
            resp = adapter.get_rules(top_k=5, context="dev")
            assert resp["status"] == "success"
            mock_ll.get_recent_learnings.assert_called_with(limit=5, context_filter="dev")

    def test_get_rules_not_initialized(self):
        adapter = RLBridgeAdapter(V2BridgeStrategy())
        resp = adapter.get_rules()
        assert resp == {"error": "Bridge not initialized"}

    def test_status(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            with patch("claw_rl.feedback.binary_rl.BinaryRLJudge", return_value=_mock_binary_rl()):
                adapter = RLBridgeAdapter(V2BridgeStrategy())
                adapter.initialize("/tmp/ws")
                resp = adapter.status()
                assert resp["initialized"] is True
                assert "workspace" in resp
                assert "components" in resp

    def test_status_not_initialized(self):
        adapter = RLBridgeAdapter(V2BridgeStrategy())
        resp = adapter.status()
        assert resp == {"error": "Bridge not initialized"}

    def test_process_learning(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            adapter = RLBridgeAdapter(V2BridgeStrategy())
            adapter.initialize("/tmp/ws")
            resp = adapter.process_learning()
            assert resp["status"] == "success"
            assert "statistics" in resp

    def test_shutdown(self):
        adapter = RLBridgeAdapter(V2BridgeStrategy())
        resp = adapter.shutdown(100, 2.5)
        assert resp["status"] == "success"
        assert resp["total_requests"] == 100
        assert resp["avg_latency_ms"] == 2.5

    def test_ping(self):
        adapter = RLBridgeAdapter(V2BridgeStrategy())
        assert adapter.ping() == {"pong": True}

    def test_components(self, mock_ll):
        with patch("claw_rl.core.learning_loop.LearningLoop", return_value=mock_ll):
            with patch("claw_rl.feedback.binary_rl.BinaryRLJudge", return_value=_mock_binary_rl()):
                with patch("claw_rl.feedback.opd_hint.OPDHintExtractor", return_value=_mock_opd_hint()):
                    adapter = RLBridgeAdapter(V2BridgeStrategy())
                    adapter.initialize("/tmp/ws")
                    comps = adapter.components
                    assert comps == {"binary_rl": True, "opd_hint": True, "learning_loop": True}


# ---- BridgeAdapterRegistry ---------------------------------------------------

class TestBridgeAdapterRegistry:
    def test_detect_version_default(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("claw_rl.adapters.bridge_registry.Path.exists", return_value=False):
                key = BridgeAdapterRegistry.detect_version_key()
                assert key == "v2"

    def test_detect_version_from_env_v1(self):
        with patch.dict(os.environ, {"OPENCLAW_VERSION": "1.5.0"}, clear=True):
            key = BridgeAdapterRegistry.detect_version_key()
            assert key == "v1"

    def test_detect_version_from_env_v2(self):
        with patch.dict(os.environ, {"OPENCLAW_VERSION": "2.9.0"}, clear=True):
            key = BridgeAdapterRegistry.detect_version_key()
            assert key == "v2"

    def test_create_strategy_v2(self):
        s = BridgeAdapterRegistry.create_strategy("v2")
        assert isinstance(s, V2BridgeStrategy)

    def test_create_strategy_v1(self):
        s = BridgeAdapterRegistry.create_strategy("v1")
        assert isinstance(s, V1BridgeStrategy)

    def test_create_strategy_unknown_raises(self):
        with pytest.raises(BridgeAdapterError, match="Unknown bridge adapter version"):
            BridgeAdapterRegistry.create_strategy("v3")

    def test_create_strategy_default(self):
        with patch.object(BridgeAdapterRegistry, "detect_version_key", return_value="v2"):
            s = BridgeAdapterRegistry.create_strategy()
            assert isinstance(s, V2BridgeStrategy)

    def test_create_adapter(self):
        adapter = BridgeAdapterRegistry.create_adapter("v2")
        assert isinstance(adapter, RLBridgeAdapter)
        assert adapter.version == "2.0.0"

    def test_create_adapter_v1(self):
        adapter = BridgeAdapterRegistry.create_adapter("v1")
        assert isinstance(adapter, RLBridgeAdapter)
        assert adapter.version == "1.0.0"


# ---- Integration / Format Consistency ---------------------------------------

class TestIntegration:
    def test_format_consistency_v2_vs_v1_collect_feedback(self):
        v2 = V2BridgeStrategy()
        v1 = V1BridgeStrategy()

        r2 = v2.format_collect_feedback_result(1.0, 0.95)
        r1 = v1.format_collect_feedback_result(1, hints=[])

        assert r2["status"] == "success"
        assert r1["status"] == "feedback_collected"
        assert r2["reward"] == r1["reward"]

    def test_format_rules_v2_vs_v1_different_keys(self):
        learnings = [{"hint": "tip", "score": 0.8, "feedback": "good", "action": "do", "reward": 1,
                       "hints": [{"hint_type": "fix", "content": "improve"}]}]

        v2_rules = V2BridgeStrategy().format_rules(learnings)
        v1_rules = V1BridgeStrategy().format_rules(learnings)

        # V2 has content/score
        assert "content" in v2_rules[0]
        assert "score" in v2_rules[0]
        # V1 has pattern/response/source/reward
        assert "pattern" in v1_rules[0]
        assert "response" in v1_rules[0]
        assert "source" in v1_rules[0]
        assert "reward" in v1_rules[0]

    def test_v1_no_v2_components(self):
        adapter_v1 = RLBridgeAdapter(V1BridgeStrategy())
        adapter_v2 = RLBridgeAdapter(V2BridgeStrategy())

        assert V1BridgeStrategy().supports_judge() is False
        assert V2BridgeStrategy().supports_judge() is True
        assert V1BridgeStrategy().supports_hint() is False
        assert V2BridgeStrategy().supports_hint() is True
