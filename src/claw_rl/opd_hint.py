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
    - should: "应该 X" → "操作前 X"
    - should_not: "不要 X" → "避免 X"
    - sequence: "先 X 再 Y" → "顺序：先 X 再 Y"
    - conditional: "如果 X，则 Y" → "条件：X → Y"
    """
    
    def extract(self, feedback: str) -> Optional[OPDHint]:
        """
        Extract OPD hint from user feedback using string methods.
        
        Args:
            feedback: User feedback text
        
        Returns:
            OPDHint if pattern matched, None otherwise
        """
        if not feedback or not feedback.strip():
            return None
        
        feedback = feedback.strip()
        
        # Pattern 1: "应该 X" → "操作前 X"
        if feedback.startswith("应该"):
            action = feedback[2:].strip()  # Remove "应该" (2 characters)
            if action:
                return OPDHint(
                    hint_type='should',
                    content=f"操作前{action}",
                    priority=3,
                    confidence=0.9
                )
        
        # Pattern 2: "不要 X" → "避免 X"
        if feedback.startswith("不要"):
            action = feedback[2:].strip()  # Remove "不要" (2 characters)
            if action:
                return OPDHint(
                    hint_type='should_not',
                    content=f"避免{action}",
                    priority=4,
                    confidence=0.9
                )
        
        # Pattern 3: "先 X 再 Y" → "顺序：先 X 再 Y"
        if "先" in feedback and "再" in feedback:
            # Find positions
            first_idx = feedback.find("先")
            again_idx = feedback.find("再", first_idx + 1)
            if first_idx >= 0 and again_idx > first_idx:
                step1 = feedback[first_idx+1:again_idx].strip()
                step2 = feedback[again_idx+1:].strip()
                if step1 and step2:
                    return OPDHint(
                        hint_type='sequence',
                        content=f"顺序：先{step1}再{step2}",
                        priority=5,
                        confidence=0.95
                    )
        
        # Pattern 4: "如果 X，则 Y" → "条件：X → Y"
        if "如果" in feedback and ("则" in feedback or "就" in feedback):
            if_pos = feedback.find("如果")
            then_pos = -1
            then_word = ""
            if "则" in feedback:
                then_pos = feedback.find("则", if_pos + 2)
                then_word = "则"
            elif "就" in feedback:
                then_pos = feedback.find("就", if_pos + 2)
                then_word = "就"
            
            if if_pos >= 0 and then_pos > if_pos:
                condition = feedback[if_pos+2:then_pos].strip()
                action = feedback[then_pos+1:].strip()
                if condition and action:
                    return OPDHint(
                        hint_type='conditional',
                        content=f"条件：{condition} → {action}",
                        priority=4,
                        confidence=0.85
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
            'pattern_types': 4,
            'patterns': [
                '应该 X',
                '不要 X', 
                '先 X 再 Y',
                '如果 X，则 Y',
            ]
        }