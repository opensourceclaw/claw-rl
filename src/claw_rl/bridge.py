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


class ClawRLBridge:
    """JSON-RPC Bridge for claw-rl"""

    def __init__(self):
        self.request_id = 0
        self.learning_loop = None
        self._initialize()

    def _initialize(self):
        """Initialize LearningLoop"""
        try:
            from pathlib import Path
            from claw_rl.core.learning_loop import LearningLoop

            workspace = os.environ.get('OPENCLAW_WORKSPACE', os.getcwd())
            data_dir = Path(workspace) / '.claw-rl'
            data_dir.mkdir(parents=True, exist_ok=True)

            self.learning_loop = LearningLoop(data_dir=data_dir)
            self._respond(None, {"status": "ok", "message": "initialized"})
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
        id = request.get("id")

        if not method:
            return self._respond(id, "Method not found", -32601)

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
        }

        handler = handlers.get(method)
        if not handler:
            return self._respond(id, f"Method '{method}' not found", -32601)

        try:
            result = handler(params)
            return self._respond(id, result)
        except Exception as e:
            return self._respond(id, str(e), -32000)

    def _handle_collect_feedback(self, params: Dict) -> Dict:
        """Handle feedback collection"""
        feedback = params.get("feedback", "")
        action = params.get("action", "")
        context = params.get("context", "")

        result = self.learning_loop.process_feedback(feedback, action, context)
        return {
            "status": "feedback_collected",
            "reward": result.get("reward", 0),
            "hints": result.get("hints", []),
        }

    def _handle_get_rules(self, params: Dict) -> Dict:
        """Handle get learned rules (uses get_recent_learnings)"""
        top_k = params.get("topK", params.get("top_k", 10))
        context = params.get("context", "")

        try:
            recent = self.learning_loop.get_recent_learnings(limit=top_k)
            # Convert to hints format
            hints = []
            for r in recent:
                for h in r.get("hints", []):
                    hints.append({
                        "pattern": h.get("original", ""),
                        "response": h.get("hint", ""),
                    })
            return {"rules": hints}
        except Exception:
            return {"rules": []}

    def _handle_status(self, params: Dict) -> Dict:
        """Handle status request"""
        stats = self.learning_loop.get_statistics()
        return {
            "status": "ok",
            "initialized": self.learning_loop is not None,
            "workspace": os.getcwd(),
            "statistics": stats,
        }

    def _handle_ping(self, params: Dict) -> Dict:
        """Handle ping"""
        return {"pong": True}

    def _handle_initialize(self, params: Dict) -> Dict:
        """Handle initialize request from TypeScript plugin"""
        workspace = params.get("workspace", os.getcwd())
        return {"status": "ok", "message": "initialized", "workspace": workspace}

    def _handle_process_learning(self, params: Dict) -> Dict:
        """Handle process_learning request (session end)"""
        try:
            stats = self.learning_loop.get_statistics()
            return {"status": "ok", "statistics": stats}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_shutdown(self, params: Dict) -> Dict:
        """Handle shutdown request"""
        return {"status": "shutting_down"}

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
