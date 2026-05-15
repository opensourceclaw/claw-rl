"""
Improved OPD Extractor (P0-3)

Structured hint extraction from correction feedback with:
1. Pattern-based extraction (extended from original)
2. Actionability scoring (content-based quality assessment)
3. Priority assignment (dynamic based on impact/frequency/urgency)
4. Example generation (concrete examples for actions)

Target: OPD actionability >80%
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re


class Priority(Enum):
    """Hint priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def to_int(self) -> int:
        return {Priority.HIGH: 5, Priority.MEDIUM: 3, Priority.LOW: 1}[self]


class Scope(Enum):
    """Application scope of a hint."""
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"
    CONTEXT = "context"


@dataclass
class Hint:
    """Structured OPD hint with quality metadata."""
    action: str
    directive: str
    scope: Scope = Scope.CONTEXT
    priority: Priority = Priority.MEDIUM
    actionability: float = 0.5  # 0.0-1.0
    confidence: float = 0.5
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "directive": self.directive,
            "scope": self.scope.value,
            "priority": self.priority.value,
            "actionability": self.actionability,
            "confidence": self.confidence,
            "examples": self.examples,
        }


class ImprovedOPDExtractor:
    """Structured hint extraction with quality scoring.

    Extends the original OPDHintExtractor with:
    - Categorized pattern matching
    - Content-based actionability scoring
    - Dynamic priority assignment
    - Automatic example generation

    Usage:
        extractor = ImprovedOPDExtractor()
        hint = extractor.extract("incorrect, should place file in src/")
        # -> Hint(action="file_placement", directive="place file in src/",
        #          priority=HIGH, actionability=0.85)
    """

    # Extraction patterns by hint category
    EXTRACTION_PATTERNS = {
        # NOTE: "should_not" must be checked before "should" to avoid
        # false positives from "要" matching inside "不要" in Chinese text.
        "should_not": [
            r"(?i)\b(don't|do not|never)\s+(.+)",
            r"(?i)\b(avoid)\s+(.+)",
            r"(不要|不能|不应该|不该|避免|禁止)\s*(.+)",
        ],
        "should": [
            r"(?i)\b(should|must)\s+(.+)",
            r"(需要|应该|要|必须|务必)\s*(.+)",
        ],
        "sequence": [
            r"(?i)\b(first)\s+(.+?)\s*(then|next)\s+(.+)",
            r"(先|首先)\s*(.+?)\s*(再|然后|接着)\s*(.+)",
        ],
        "conditional": [
            r"(?i)\b(if|when)\s+(.+?)\s*[,，]\s*(then)\s+(.+)",
            r"(如果|当)\s*(.+?)\s*[,，]?\s*(就|那么|会)\s*(.+)",
        ],
        "preference": [
            r"(?i)\b(I prefer|I like|better to|prefer)\s+(.+)",
            r"(?i)\b(usually|always)\s+(.+)",
            r"(最好|更倾向于|一般|通常|总是)\s*(.+)",
        ],
        "action_required": [
            r"(?i)\b(please)\s+(.+)",
            r"(?i)\b(need to|have to|has to)\s+(.+)",
            r"(请|麻烦|记得|别忘了)\s*(.+)",
        ],
    }

    def __init__(self):
        self._stats = {"extractions": 0, "hints": 0, "by_priority": {"high": 0, "medium": 0, "low": 0}}

    def extract(
        self,
        correction: str,
        context: Optional[Dict] = None,
    ) -> Optional[Hint]:
        """Extract a structured hint from correction feedback.

        Args:
            correction: User correction/feedback text
            context: Optional context dict with action/history info

        Returns:
            Hint if extraction successful, None otherwise
        """
        if not correction or not correction.strip():
            return None

        correction = correction.strip()
        self._stats["extractions"] += 1

        # Step 1: Parse correction and identify category
        category, match_groups = self._parse_correction(correction)
        if not category:
            return None

        # Step 2: Identify target action
        action = self._identify_action(correction, category)

        # Step 3: Extract directive text
        directive = self._extract_directive(category, match_groups)

        # Step 4: Determine scope
        scope = self._determine_scope(correction, context)

        # Step 5: Assign priority
        priority = self._assign_priority(correction, category, context)

        # Step 6: Score actionability
        actionability = self._score_actionability(directive, action)

        # Step 7: Generate examples
        examples = self._generate_examples(directive, action, context)

        self._stats["hints"] += 1
        self._stats["by_priority"][priority.value] += 1

        return Hint(
            action=action,
            directive=directive,
            scope=scope,
            priority=priority,
            actionability=actionability,
            confidence=0.7,  # Moderate base confidence
            examples=examples,
        )

    def extract_all(
        self,
        corrections: List[str],
        context: Optional[Dict] = None,
    ) -> List[Hint]:
        """Extract hints from multiple corrections.

        Args:
            corrections: List of correction texts
            context: Optional context dict

        Returns:
            List of extracted Hint objects
        """
        hints = []
        for correction in corrections:
            hint = self.extract(correction, context)
            if hint:
                hints.append(hint)
        return self._deduplicate_hints(hints)

    def get_statistics(self) -> Dict:
        """Get extractor statistics."""
        return dict(self._stats)

    def _parse_correction(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Parse correction text to identify category and extract groups.

        Returns:
            Tuple of (category_name, match_groups)
        """
        for category, patterns in self.EXTRACTION_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return category, list(match.groups())
        return None, []

    @staticmethod
    def _identify_action(text: str, category: str) -> str:
        """Identify the target action from correction context."""
        # Action patterns in the correction
        action_keywords = [
            r"(?i)\b(create|delete|modify|update|move|rename|write|read|execute|run|build|test|deploy|commit|push|merge)\b",
            r"(创建|删除|修改|更新|移动|重命名|写|读|执行|运行|构建|测试|部署|提交|推送|合并)",
        ]

        for kw_pattern in action_keywords:
            match = re.search(kw_pattern, text)
            if match:
                return match.group(0).lower()

        # Fallback: use category as action
        return category.replace("_", " ")

    @staticmethod
    def _extract_directive(category: str, groups: List[str]) -> str:
        """Extract directive text from matched groups."""
        if category == "should":
            directive = groups[1] if len(groups) > 1 else groups[0]
        elif category == "should_not":
            directive = f"avoid {groups[1]}" if len(groups) > 1 else f"avoid {groups[0]}"
        elif category == "sequence":
            if len(groups) >= 4:
                directive = f"first {groups[1]}, then {groups[3]}"
            elif len(groups) >= 3:
                directive = f"{groups[1]} before {groups[2]}"
            else:
                directive = " ".join(groups)
        elif category == "conditional":
            if len(groups) >= 4:
                directive = f"if {groups[1]}, then {groups[3]}"
            else:
                directive = " ".join(groups)
        elif category in ("preference", "action_required"):
            directive = groups[1] if len(groups) > 1 else groups[0]
        else:
            directive = " ".join(groups)

        return directive.strip()

    @staticmethod
    def _determine_scope(text: str, context: Optional[Dict]) -> Scope:
        """Determine application scope from text and context.

        Priority order: GLOBAL > PROJECT > SESSION > CONTEXT
        """
        # Check for explicit scope signals
        if re.search(r"(?i)\b(always|always do|永远|forever|persistent)\b", text):
            return Scope.GLOBAL
        if re.search(r"(?i)\b(in this project|for this project|项目(中|里|中)|这个项目|repo)\b", text):
            return Scope.PROJECT
        if re.search(r"(?i)\b(in this session|for now|this time|当前|本次|这次|现在)\b", text):
            return Scope.SESSION

        # Default: session-level for "should/should_not", context for others
        if any(kw in text.lower() for kw in ("should", "需要", "应该", "要", "必须")):
            return Scope.SESSION

        return Scope.CONTEXT

    @staticmethod
    def _assign_priority(text: str, category: str,
                          context: Optional[Dict]) -> Priority:
        """Assign priority based on impact, frequency, and urgency.

        Factors:
        - Impact: "must"/"必"/"error"/"bug" → high
        - Frequency: "always"/"经常" → medium (if not high)
        - Urgency: "urgent"/"ASAP"/"紧急" → high
        """
        # High impact signals
        if re.search(r"(?i)\b(must|必须|务必|error|bug|broken|broken|crash|崩溃|错误)\b", text):
            return Priority.HIGH
        if re.search(r"(?i)\b(urgent|asap|immediately|紧急|马上|立即)\b", text):
            return Priority.HIGH

        # Medium impact signals
        if re.search(r"(?i)\b(should|需要|应该|要|often|经常|重要)\b", text):
            return Priority.MEDIUM

        # Category-based defaults
        if category == "should_not":
            return Priority.MEDIUM

        return Priority.LOW

    @staticmethod
    def _score_actionability(directive: str, action: str) -> float:
        """Score how actionable a hint is (0.0-1.0).

        Factors:
        - Specificity: How specific is the directive?
        - Feasibility: Can it be implemented?
        - Clarity: Is it clear what to do?
        """
        specificity = ImprovedOPDExtractor._compute_specificity(directive)
        feasibility = ImprovedOPDExtractor._compute_feasibility(directive, action)
        clarity = ImprovedOPDExtractor._compute_clarity(directive)

        return (specificity + feasibility + clarity) / 3.0

    @staticmethod
    def _compute_specificity(directive: str) -> float:
        """Compute specificity score (how specific is the instruction)."""
        score = 0.3  # Base

        # Longer directives tend to be more specific
        if len(directive) > 30:
            score += 0.3
        elif len(directive) > 15:
            score += 0.2
        elif len(directive) > 5:
            score += 0.1

        # Contains concrete entities (paths, filenames, etc.)
        if re.search(r'[/\\]|[.](py|js|ts|md|json|yaml|toml)\b', directive):
            score += 0.3

        # Contains actions or imperative verbs
        if re.search(r'(?i)\b(create|delete|modify|update|move|rename|write|run|test|build)\b',
                     directive):
            score += 0.2

        # Contains conditions or constraints
        if re.search(r'(?i)\b(if|when|only|except|unless)\b', directive):
            score += 0.1

        return min(1.0, score)

    @staticmethod
    def _compute_feasibility(directive: str, action: str) -> float:
        """Compute feasibility score (can this actually be done?)."""
        score = 0.5  # Base: most things are feasible

        # Undefined or vague actions are less feasible
        vague = ["something", "things", "stuff", "somehow", "东西", "一些"]
        if any(v in directive.lower() for v in vague):
            score -= 0.2

        # Concrete file/system operations are very feasible
        concrete = [
            "file", "directory", "config", "setting", "parameter",
            "文件", "目录", "配置", "设置", "参数",
        ]
        if any(c in directive.lower() for c in concrete):
            score += 0.2

        # Negation (avoiding things) is feasible but harder to measure
        if "avoid" in directive.lower() or "不要" in directive or "don't" in directive.lower():
            score -= 0.1

        return min(1.0, max(0.0, score))

    @staticmethod
    def _compute_clarity(directive: str) -> float:
        """Compute clarity score (how clear is the instruction)."""
        score = 0.4  # Base

        # Well-structured directive
        if not directive:
            return 0.0

        # Contains both subject and action
        if len(directive.split()) >= 3:
            score += 0.2

        # No ambiguous pronouns
        ambiguous = ["it", "this", "that", "these", "those", "它", "这", "那"]
        if not any(a in directive.lower() for a in ambiguous):
            score += 0.2

        # Contains concrete values
        if re.search(r'\d+|"[^"]*"|\'[^\']*\'', directive):
            score += 0.1

        return min(1.0, score)

    @staticmethod
    def _generate_examples(directive: str, action: str,
                            context: Optional[Dict]) -> List[str]:
        """Generate concrete examples from the directive.

        Args:
            directive: Extracted directive text
            action: Target action
            context: Optional context

        Returns:
            List of example strings
        """
        examples = []

        # Action-type example
        examples.append(f"When performing {action}: {directive}")

        # Conditional example if applicable
        if "if" in directive.lower() or "when" in directive.lower():
            examples.append(directive)

        # General recommendation
        examples.append(f"Tip: {directive}")

        return examples[:3]

    @staticmethod
    def _deduplicate_hints(hints: List[Hint]) -> List[Hint]:
        """Remove duplicate hints, keeping highest actionability."""
        seen: Dict[str, Hint] = {}
        for hint in hints:
            key = hint.action + "::" + hint.directive[:50].lower()
            if key not in seen or hint.actionability > seen[key].actionability:
                seen[key] = hint
        return list(seen.values())


__all__ = [
    'ImprovedOPDExtractor',
    'Hint',
    'Priority',
    'Scope',
]
