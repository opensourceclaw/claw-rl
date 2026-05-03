"""claw-rl v2.10.0 - Offline Training Pipeline."""

import threading
import time
from typing import Any, Callable, Dict, List, Optional


class OfflinePipeline:
    """Periodic offline weight consolidation training.

    Runs in background, collects high-value experiences, and
    performs weight consolidation when enough data is available.
    """

    def __init__(self, interval_hours: float = 6.0):
        self.interval_hours = interval_hours
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cycles = 0
        self._callbacks: List[Callable] = []

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def on_cycle(self, callback: Callable):
        self._callbacks.append(callback)

    def run_once(self) -> Dict[str, Any]:
        self._cycles += 1
        for cb in self._callbacks:
            cb()
        return {"cycle": self._cycles, "complete": True}

    def _loop(self):
        while self._running:
            time.sleep(self.interval_hours * 3600)
            if self._running:
                self.run_once()

    def get_stats(self) -> Dict[str, Any]:
        return {"cycles": self._cycles, "running": self._running}
