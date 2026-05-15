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
claw-rl Bridge for OpenClaw Plugin
JSON-RPC interface via stdio
"""

import sys
import json
import os
from typing import Any, Dict, Optional

# Add src to path
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_parent = os.path.dirname(src_dir)
if src_parent not in sys.path:
    sys.path.insert(0, src_parent)

# JSON stdout filter - only allow JSON-RPC responses
_original_stdout = sys.stdout


class JsonStdout:
    """Wrapper that only allows JSON output"""

    def write(self, data):
        if data.strip().startswith('{') and '"jsonrpc"' in data:
            _original_stdout.write(data)
            _original_stdout.flush()
        elif data == '\n':
            _original_stdout.write(data)
            _original_stdout.flush()

    def flush(self):
        _original_stdout.flush()


sys.stdout = JsonStdout()

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

from claw_rl.adapters import BridgeAdapterRegistry


class ClawRLBridge:
    """JSON-RPC Bridge for claw-rl"""

    def __init__(self):
        self.request_id = 0
        self._adapter = None
        self._initialize()

    def _initialize(self):
        """Initialize adapter and core components."""
        try:
            workspace = os.environ.get('OPENCLAW_WORKSPACE', os.getcwd())
            self._adapter = BridgeAdapterRegistry.create_adapter()
            result = self._adapter.initialize(workspace)
            self._respond(None, result)
        except Exception as e:
            self._respond(None, {"error": str(e)}, -32000)

    def _respond(self, id: Any, result: Any, error_code: Optional[int] = None):
        """Send JSON-RPC response"""
        response = {
            "jsonrpc": "2.0",
            "id": id,
        }

        if error_code is not None:
            response["error"] = {
                "code": error_code,
                "message": result if isinstance(result, str) else str(result)
            }
        else:
            response["result"] = result

        print(json.dumps(response), flush=True)

    def _handle_request(self, request: Dict) -> Any:
        """Handle JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        if not method:
            return self._respond(req_id, "Method not found", -32601)

        handlers = {
            "initialize": self._handle_initialize,
            "collect_feedback": self._handle_collect_feedback,
            "get_learned_rules": self._handle_get_rules,
            "get_rules": self._handle_get_rules,
            "learning_status": self._handle_status,
            "status": self._handle_status,
            "process_learning": self._handle_process_learning,
            "shutdown": self._handle_shutdown,
            "ping": self._handle_ping,
            # P0: Enhanced Binary RL + Improved OPD + Fast Learning + Quality Monitor
            "enhanced_binary_rl": self._handle_enhanced_binary_rl,
            "enhanced_opd": self._handle_enhanced_opd,
            "fast_learning": self._handle_fast_learning,
            "rule_quality_monitor": self._handle_rule_quality_monitor,
        }

        handler = handlers.get(method)
        if not handler:
            return self._respond(req_id, f"Method '{method}' not found", -32601)

        try:
            result = handler(params)
            return self._respond(req_id, result)
        except Exception as e:
            return self._respond(req_id, str(e), -32000)

    def _handle_collect_feedback(self, params: Dict) -> Dict:
        feedback = params.get("feedback", "")
        action = params.get("action", "")
        context = params.get("context", "")
        return self._adapter.collect_feedback(feedback, action, context)

    def _handle_get_rules(self, params: Dict) -> Dict:
        top_k = params.get("topK", params.get("top_k", 10))
        context = params.get("context", "")
        try:
            return self._adapter.get_rules(top_k=top_k, context=context)
        except Exception:
            return {"rules": []}

    def _handle_status(self, params: Dict) -> Dict:
        try:
            result = self._adapter.status()
            return result
        except Exception:
            return {"status": "error"}

    def _handle_ping(self, params: Dict) -> Dict:
        return self._adapter.ping() if self._adapter else {"pong": True}

    def _handle_initialize(self, params: Dict) -> Dict:
        workspace = params.get("workspace", os.getcwd())
        return {"status": "ok", "message": "initialized", "workspace": workspace}

    def _handle_process_learning(self, params: Dict) -> Dict:
        try:
            return self._adapter.process_learning()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_shutdown(self, params: Dict) -> Dict:
        return self._adapter.shutdown() if self._adapter else {"status": "shutting_down"}

    # ---- P0 handlers: Enhanced RL + OPD + Fast Learning + Quality -----

    def _handle_enhanced_binary_rl(self, params: Dict) -> Dict:
        """P0: Enhanced binary RL judge — multi-signal classification."""
        from claw_rl.feedback.enhanced_binary_rl import EnhancedBinaryRLJudge

        feedback = params.get("feedback", "")
        context = params.get("context")

        judge = EnhancedBinaryRLJudge()
        result = judge.judge(feedback, context)

        return {
            "is_positive": result.is_positive,
            "confidence": result.confidence,
            "reward": result.reward,
            "signals": result.signals,
            "pattern_matched": result.pattern_matched,
            "semantic_label": result.semantic_label,
            "reason": result.reason,
        }

    def _handle_enhanced_opd(self, params: Dict) -> Dict:
        """P0: Improved OPD extraction — structured hints with quality scoring."""
        from claw_rl.feedback.enhanced_opd import ImprovedOPDExtractor

        correction = params.get("correction", "")
        context = params.get("context")

        extractor = ImprovedOPDExtractor()
        hint = extractor.extract(correction, context)

        if hint:
            return {
                "found": True,
                "hint": hint.to_dict(),
            }
        return {"found": False, "hint": None}

    def _handle_fast_learning(self, params: Dict) -> Dict:
        """P0: Fast learning loop — immediate rule application."""
        from claw_rl.feedback.enhanced_opd import Hint, Priority, Scope
        from claw_rl.core.fast_learning_loop import FastLearningLoop

        action = params.get("action", "unknown")
        directive = params.get("directive", "")
        priority_str = params.get("priority", "medium")
        scope_str = params.get("scope", "session")

        hint = Hint(
            action=action,
            directive=directive,
            priority={"high": Priority.HIGH, "medium": Priority.MEDIUM, "low": Priority.LOW}.get(priority_str, Priority.MEDIUM),
            scope={"global": Scope.GLOBAL, "project": Scope.PROJECT, "session": Scope.SESSION, "context": Scope.CONTEXT}.get(scope_str, Scope.SESSION),
            actionability=params.get("actionability", 0.7),
            confidence=params.get("confidence", 0.7),
        )

        loop = FastLearningLoop()
        result = loop.apply_hint(hint)

        return {
            "success": result.success,
            "rule_id": result.rule_id,
            "created": result.created,
            "updated": result.updated,
            "conflict_resolved": result.conflict_resolved,
            "reason": result.reason,
        }

    def _handle_rule_quality_monitor(self, params: Dict) -> Dict:
        """P0: Rule quality monitoring — evaluation + pruning."""
        from claw_rl.core.fast_learning_loop import RuleStore, Rule
        from claw_rl.core.rule_quality_monitor import RuleQualityMonitor

        action = params.get("action", "status")

        # For status action: return overall rule quality report
        store = RuleStore()
        monitor = RuleQualityMonitor(store)
        report = monitor.evaluate_rules()

        return {
            "total_rules": report.total_rules,
            "healthy": report.healthy,
            "degraded": report.degraded,
            "stale": report.stale,
            "low_performing": report.low_performing,
            "untested": report.untested,
            "pruned": report.pruned,
            "average_effectiveness": report.average_effectiveness,
        }

    def run(self):
        """Run the bridge"""
        self._respond(0, {"ready": True})

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                self._handle_request(request)
            except json.JSONDecodeError as e:
                self._respond(None, f"Invalid JSON: {e}", -32700)
            except Exception as e:
                self._respond(None, str(e), -32000)


def main():
    """Entry point"""
    bridge = ClawRLBridge()
    bridge.run()


if __name__ == "__main__":
    main()
