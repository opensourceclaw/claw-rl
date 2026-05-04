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
