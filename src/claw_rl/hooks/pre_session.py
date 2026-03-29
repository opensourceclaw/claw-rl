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
claw-rl Pre-Session Hook

Injects learned hints and patterns before session starts.
"""

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import json


@dataclass
class PreSessionInput:
    """Input for pre-session hook"""
    session_id: str
    user_id: str
    timestamp: str


@dataclass
class PreSessionOutput:
    """Output from pre-session hook"""
    injected_memory: str
    hints: List[str]
    patterns: List[str]
    active: bool


class PreSessionHook:
    """
    Pre-Session Hook
    
    Injects learned hints and patterns before session starts.
    
    Usage:
        hook = PreSessionHook()
        result = hook.execute(PreSessionInput(
            session_id="session_001",
            user_id="peter",
            timestamp="2026-03-29T09:00:00"
        ))
        print(result.injected_memory)
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize Pre-Session Hook
        
        Args:
            data_dir: Optional custom data directory
        """
        self.data_dir = data_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
    
    def execute(self, input: PreSessionInput) -> PreSessionOutput:
        """
        Execute pre-session hook
        
        Args:
            input: Session input data
            
        Returns:
            PreSessionOutput: Injected memory and loaded hints/patterns
        """
        # Load recent hints
        hints = self._load_recent_hints(days=7, limit=5)
        
        # Load patterns from claw-mem
        patterns = self._load_patterns(limit=3)
        
        # Build injected memory section
        injected = self._build_memory(hints, patterns)
        
        return PreSessionOutput(
            injected_memory=injected,
            hints=hints,
            patterns=patterns,
            active=True
        )
    
    def _load_recent_hints(self, days: int = 7, limit: int = 5) -> List[str]:
        """
        Load hints from recent sessions
        
        Args:
            days: Number of days to look back
            limit: Maximum number of hints to return
            
        Returns:
            List[str]: Recent hints
        """
        hints = []
        hints_dir = self.data_dir / 'hints'
        
        if not hints_dir.exists():
            return hints
        
        # Calculate cutoff date
        cutoff = datetime.now() - timedelta(days=days)
        
        # Read hint files
        for hint_file in sorted(hints_dir.glob('*.jsonl'), reverse=True):
            try:
                # Parse date from filename (YYYY-MM-DD.jsonl)
                file_date = datetime.strptime(hint_file.stem, '%Y-%m-%d')
                if file_date < cutoff:
                    continue
                
                # Read hints from file
                with open(hint_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if len(hints) >= limit:
                            break
                        data = json.loads(line)
                        if 'hint' in data:
                            hints.append(data['hint'])
                
                if len(hints) >= limit:
                    break
                    
            except (ValueError, json.JSONDecodeError):
                continue
        
        return hints[:limit]
    
    def _load_patterns(self, limit: int = 3) -> List[str]:
        """
        Load learned patterns from claw-mem
        
        Args:
            limit: Maximum number of patterns to return
            
        Returns:
            List[str]: Learned patterns
        """
        patterns = []
        
        # Check claw-mem location
        claw_mem_file = Path.home() / '.openclaw' / 'workspace' / 'memory' / 'claw-rl-learnings.md'
        
        if not claw_mem_file.exists():
            return patterns
        
        # Read patterns from file
        try:
            with open(claw_mem_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(patterns) >= limit:
                        break
                    
                    # Look for pattern lines (starting with timestamp)
                    if line.startswith('[') and ']' in line:
                        # Extract pattern text after timestamp
                        parts = line.split(']', 1)
                        if len(parts) > 1:
                            pattern = parts[1].strip()
                            if pattern and not pattern.startswith('-'):
                                patterns.append(pattern)
        except Exception:
            pass
        
        return patterns[:limit]
    
    def _build_memory(self, hints: List[str], patterns: List[str]) -> str:
        """
        Build memory section for injection
        
        Args:
            hints: List of hints
            patterns: List of patterns
            
        Returns:
            str: Formatted memory section
        """
        sections = []
        
        if hints:
            sections.append("## 🧠 Learned Hints (claw-rl)\n")
            sections.append("Recent learning signals from user feedback:\n\n")
            for i, hint in enumerate(hints, 1):
                sections.append(f"{i}. {hint}\n")
        
        if patterns:
            if sections:
                sections.append("\n")
            sections.append("## 📊 Learned Patterns (claw-rl)\n")
            sections.append("Patterns discovered from past decisions:\n\n")
            for i, pattern in enumerate(patterns, 1):
                sections.append(f"{i}. {pattern}\n")
        
        return "".join(sections) if sections else ""
