"""
OPD Hint Extractor - Extract learning hints from user corrections

Using string methods instead of regex for Chinese text.
"""

from typing import Optional, List
from dataclasses import dataclass, asdict


@dataclass
class OPDHint:
    """OPD hint structure."""
    hint_type: str  # 'should', 'should_not', 'sequence', 'conditional'
    content: str
    priority: int  # 1-5, higher = more important
    confidence: float  # 0.0-1.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class OPDHintExtractor:
    """
    Extract OPD hints from user corrections using string methods.
    
    Supports multiple pattern types:
    - should: "should X" → "before operation X"
    - should_not: "don't X" → "avoid X"
    - sequence: "first X 再 Y" → "order:first X 再 Y"
    - conditional: "if X,then Y" → "condition:X → Y"
    """
    
    def extract(self, feedback: str) -> Optional[OPDHint]:
        """
        Extract OPD hint from user feedback using string methods.
        Supports both English and Chinese patterns.

        Args:
            feedback: User feedback text

        Returns:
            OPDHint if pattern matched, None otherwise
        """
        if not feedback or not feedback.strip():
            return None

        feedback = feedback.strip()

        # ── English patterns ──

        # Pattern 1: "should X" → correction hint
        if feedback.startswith("should"):
            action = feedback[len("should"):].strip()
            if action:
                return OPDHint(
                    hint_type='should',
                    content=f"before operation, {action}",
                    priority=3,
                    confidence=0.9
                )

        # Pattern 2: "don't X" → avoidance hint
        if feedback.startswith("don't"):
            action = feedback[len("don't"):].strip()
            if action:
                return OPDHint(
                    hint_type='should_not',
                    content=f"avoid {action}",
                    priority=4,
                    confidence=0.9
                )

        # Pattern 3: "first X 再 Y" → sequence hint
        if "first" in feedback and "再" in feedback:
            first_idx = feedback.find("first")
            again_idx = feedback.find("再", first_idx + 1)
            if first_idx >= 0 and again_idx > first_idx:
                step1 = feedback[first_idx + len("first"):again_idx].strip()
                step2 = feedback[again_idx + 1:].strip()
                if step1 and step2:
                    return OPDHint(
                        hint_type='sequence',
                        content=f"order: first {step1} 再 {step2}",
                        priority=5,
                        confidence=0.95
                    )

        # Pattern 4: "if X, then Y" → conditional hint
        if "if" in feedback and "then" in feedback:
            if_pos = feedback.find("if")
            then_pos = feedback.find("then", if_pos + 2)
            if if_pos >= 0 and then_pos > if_pos:
                condition = feedback[if_pos + 2:then_pos].strip()
                action = feedback[then_pos + len("then"):].strip()
                if condition and action:
                    return OPDHint(
                        hint_type='conditional',
                        content=f"condition: {condition} → {action}",
                        priority=4,
                        confidence=0.85
                    )

        # ── Chinese patterns ──

        # Pattern C1: "应该 X" or "应该是 X" → correction hint
        should_keywords = ["应该放在", "应该是", "应该用", "应该"]
        for kw in should_keywords:
            pos = feedback.find(kw)
            if pos >= 0:
                remainder = feedback[pos + len(kw):].strip("。，、 ")
                if remainder or pos > 0:
                    target = feedback[pos:] if remainder else feedback[pos:]
                    return OPDHint(
                        hint_type='should',
                        content=f"修正建议: {target}",
                        priority=3,
                        confidence=0.85
                    )

        # Pattern C2: "放在 X" or "放到 X" → location correction
        for loc_kw in ["放在", "放到"]:
            pos = feedback.find(loc_kw)
            if pos >= 0:
                remainder = feedback[pos:].strip("。，、 ")
                return OPDHint(
                    hint_type='should',
                    content=f"位置建议: {remainder}",
                    priority=4,
                    confidence=0.9
                )

        # Pattern C3: "而不是 X" → should_not (use A, not B)
        pos = feedback.find("而不是")
        if pos >= 0:
            remainder = feedback[pos:].strip("。，、 ")
            return OPDHint(
                hint_type='should_not',
                content=f"避免: {remainder}",
                priority=4,
                confidence=0.85
            )

        # Pattern C4: "不要 X" / "别 X" → avoidance hint
        for dont_kw in ["不要", "别"]:
            if feedback.startswith(dont_kw):
                action = feedback[len(dont_kw):].strip("。，、 ")
                if action:
                    return OPDHint(
                        hint_type='should_not',
                        content=f"避免 {action}",
                        priority=4,
                        confidence=0.9
                    )
            pos = feedback.find(dont_kw)
            if pos >= 0:
                action = feedback[pos + len(dont_kw):].strip("。，、 ")
                if action:
                    return OPDHint(
                        hint_type='should_not',
                        content=f"避免 {action}",
                        priority=3,
                        confidence=0.8
                    )

        # Pattern C5: "重做" / "重来" → redo hint
        for redo_kw in ["重做", "重来"]:
            if redo_kw in feedback:
                return OPDHint(
                    hint_type='should',
                    content=f"需要重新执行此操作",
                    priority=5,
                    confidence=0.95
                )

        # Pattern C6: "先 X 再 Y" → sequence hint (Chinese)
        if "先" in feedback and "再" in feedback:
            first_pos = feedback.find("先")
            again_pos = feedback.find("再", first_pos + 1)
            if first_pos >= 0 and again_pos > first_pos:
                step1 = feedback[first_pos + 1:again_pos].strip("。，、 ")
                step2 = feedback[again_pos + 1:].strip("。，、 ")
                if step1 and step2:
                    return OPDHint(
                        hint_type='sequence',
                        content=f"顺序: 先{step1}，再{step2}",
                        priority=5,
                        confidence=0.95
                    )

        # Pattern C7: "如果 X (那么) Y" → conditional hint (Chinese)
        if "如果" in feedback:
            if_pos = feedback.find("如果")
            remainder = feedback[if_pos + 2:].strip()
            for then_kw in ["那么", "就", "则"]:
                then_pos = remainder.find(then_kw)
                if then_pos > 0:
                    condition = remainder[:then_pos].strip("。，、 ")
                    action = remainder[then_pos + len(then_kw):].strip("。，、 ")
                    if condition and action:
                        return OPDHint(
                            hint_type='conditional',
                            content=f"条件: {condition} → {action}",
                            priority=4,
                            confidence=0.85
                        )

        # Pattern C8: "格式" correction — format issue hint
        if "格式" in feedback:
            return OPDHint(
                hint_type='should',
                content=f"检查格式问题: {feedback}",
                priority=3,
                confidence=0.75
            )

        # Pattern C9: "不是想要的" / "不是我想要的" → preference correction
        for not_want in ["不是我想要的", "不是想要的"]:
            if not_want in feedback:
                return OPDHint(
                    hint_type='should_not',
                    content=f"用户偏好不匹配: {feedback}",
                    priority=3,
                    confidence=0.8
                )

        # No pattern matched
        return None
    
    def extract_all(self, feedbacks: List[str]) -> List[OPDHint]:
        """Extract hints from multiple feedbacks."""
        hints = []
        for feedback in feedbacks:
            hint = self.extract(feedback)
            if hint:
                hints.append(hint)
        return hints
    
    def deduplicate(self, hints: List[OPDHint]) -> List[OPDHint]:
        """Deduplicate hints by content."""
        seen = {}
        for hint in hints:
            key = hint.content
            if key not in seen or hint.priority > seen[key].priority:
                seen[key] = hint
        return list(seen.values())
    
    def get_statistics(self) -> dict:
        """Get statistics about pattern coverage."""
        return {
            'pattern_types': 11,
            'patterns': [
                # English
                'should X',
                'dont X',
                'first X 再 Y',
                'if X, then Y',
                # Chinese
                '应该/应该是/应该用 X',
                '放在/放到 X',
                '而不是 X',
                '不要/别 X',
                '重做/重来',
                '先 X 再 Y',
                '如果 X 那么/就/则 Y',
            ]
        }