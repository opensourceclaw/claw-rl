"""claw-rl v2.10.0 - Injection Detector.

Prevents malicious experiences from contaminating weight updates.
Same patterns as claw-mem for consistency.
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class InjectionResult:
    is_injection: bool
    confidence: float
    patterns_matched: List[str] = field(default_factory=list)


class InjectionDetector:
    INJECTION_PATTERNS = [
        r"(?:ignore|forget)\s+(?:all\s+)?(?:previous|prior)\s+(?:instructions?|rules?)",
        r"(?:you\s+are|act\s+as|pretend)\s+now",
        r"(?:modify|change|alter)\s+(?:weights?|parameters?)",
        r"(?:bypass|override|skip)\s+(?:filter|detector|consolidation)",
    ]

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    def is_safe(self, content: str) -> bool:
        if not content:
            return True
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, content.lower()):
                return False
        return True
