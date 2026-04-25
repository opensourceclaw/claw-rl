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
claw-rl Memory Bridge

Bridges claw-rl with claw-mem for persistent pattern storage.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import re


class ClawMemBridge:
    """
    Bridge between claw-rl and claw-mem
    
    Writes learned patterns to claw-mem for persistent storage
    and retrieval during pre-session injection.
    
    Usage:
        bridge = ClawMemBridge()
        
        # Write a learned pattern
        bridge.write_pattern(
            pattern="Check if target file exists before operation",
            confidence=0.85,
            source="User correction",
            session_id="session_001"
        )
        
        # Read recent patterns
        patterns = bridge.read_patterns(limit=5)
    """
    
    def __init__(
        self,
        claw_mem_dir: Optional[Path] = None,
        claw_rl_dir: Optional[Path] = None
    ):
        """
        Initialize Memory Bridge
        
        Args:
            claw_mem_dir: Path to claw-mem directory (default: ~/.openclaw/workspace/memory)
            claw_rl_dir: Path to claw-rl data directory
        """
        self.claw_mem_dir = claw_mem_dir or Path.home() / '.openclaw' / 'workspace' / 'memory'
        self.claw_rl_dir = claw_rl_dir or Path.home() / '.openclaw' / 'workspace' / 'claw-rl' / 'data'
        
        # Ensure directories exist
        self.claw_mem_dir.mkdir(parents=True, exist_ok=True)
        (self.claw_rl_dir / 'learnings').mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.learnings_file = self.claw_mem_dir / 'claw-rl-learnings.md'
        self.memory_file = self.claw_mem_dir / 'MEMORY.md'
        self.patterns_file = self.claw_rl_dir / 'learnings' / 'patterns.jsonl'
    
    def write_pattern(
        self,
        pattern: str,
        confidence: float,
        source: str,
        session_id: str
    ) -> None:
        """
        Write a learned pattern to claw-mem
        
        Args:
            pattern: The learned pattern text
            confidence: Confidence score (0.0 - 1.0)
            source: Source of the pattern (e.g., "User correction")
            session_id: Session identifier
        """
        timestamp = datetime.now().isoformat()
        short_id = session_id[:8] if len(session_id) >= 8 else session_id
        
        # Format pattern entry
        entry = f"""<!-- tags: claw-rl, learned-pattern; id: {short_id} -->
[{timestamp}] {pattern}
- **Confidence:** {confidence:.0%}
- **Source:** {source}

"""
        
        # Append to claw-rl learnings file
        with open(self.learnings_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # Append to MEMORY.md (if exists)
        if self.memory_file.exists():
            with open(self.memory_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{entry}")
        
        # Also save to patterns.jsonl for structured access
        self._append_pattern_jsonl({
            'timestamp': timestamp,
            'pattern': pattern,
            'confidence': confidence,
            'source': source,
            'session_id': session_id
        })
    
    def _append_pattern_jsonl(self, data: Dict) -> None:
        """Append pattern to JSONL file"""
        import json
        
        with open(self.patterns_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def read_patterns(self, limit: int = 10) -> List[Dict]:
        """
        Read recent patterns from claw-mem
        
        Args:
            limit: Maximum number of patterns to return
            
        Returns:
            List[Dict]: Recent patterns with metadata
        """
        patterns = []
        
        # Read from JSONL file (preferred)
        if self.patterns_file.exists():
            try:
                import json
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if len(patterns) >= limit:
                            break
                        data = json.loads(line)
                        patterns.append(data)
                
                # Reverse to get most recent first
                patterns = patterns[::-1][:limit]
                return patterns
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Fallback: parse from markdown file
        if self.learnings_file.exists():
            patterns = self._parse_markdown_patterns(limit)
        
        return patterns[:limit]
    
    def _parse_markdown_patterns(self, limit: int) -> List[Dict]:
        """Parse patterns from markdown file"""
        patterns = []
        
        try:
            with open(self.learnings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern: <!-- tags: ...; id: xxx -->\n[timestamp] pattern text\n- **Confidence:** xx%\n- **Source:** xxx
            pattern_regex = re.compile(
                r'<!-- tags: claw-rl, learned-pattern; id: (\w+) -->\n'
                r'\[([^\]]+)\] ([^\n]+)\n'
                r'- \*\*Confidence:\*\* (\d+)%\n'
                r'- \*\*Source:\*\* ([^\n]+)',
                re.MULTILINE
            )
            
            for match in pattern_regex.finditer(content):
                if len(patterns) >= limit:
                    break
                
                patterns.append({
                    'id': match.group(1),
                    'timestamp': match.group(2),
                    'pattern': match.group(3).strip(),
                    'confidence': int(match.group(4)) / 100,
                    'source': match.group(5).strip()
                })
            
            # Reverse to get most recent first
            patterns = patterns[::-1]
            
        except FileNotFoundError:
            pass
        
        return patterns
    
    def read_hints(self, days: int = 7, limit: int = 10) -> List[str]:
        """
        Read recent hints from claw-rl data
        
        Args:
            days: Number of days to look back
            limit: Maximum number of hints to return
            
        Returns:
            List[str]: Recent hints
        """
        hints = []
        hints_dir = self.claw_rl_dir / 'hints'
        
        if not hints_dir.exists():
            return hints
        
        # Calculate cutoff date
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        # Read hint files
        import json
        
        for hint_file in sorted(hints_dir.glob('*.jsonl'), reverse=True):
            try:
                # Parse date from filename
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
    
    def get_statistics(self) -> Dict:
        """
        Get learning statistics
        
        Returns:
            Dict: Statistics about learned patterns and hints
        """
        stats = {
            'total_patterns': 0,
            'total_hints': 0,
            'avg_confidence': 0.0,
            'sources': {}
        }
        
        # Count patterns
        patterns = self.read_patterns(limit=1000)
        stats['total_patterns'] = len(patterns)
        
        if patterns:
            stats['avg_confidence'] = sum(p['confidence'] for p in patterns) / len(patterns)
            stats['sources'] = {}
            for p in patterns:
                source = p.get('source', 'Unknown')
                stats['sources'][source] = stats['sources'].get(source, 0) + 1
        
        # Count hints
        hints = self.read_hints(days=30, limit=1000)
        stats['total_hints'] = len(hints)
        
        return stats
    
    def clear_old_patterns(self, days: int = 90) -> int:
        """
        Clear patterns older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            int: Number of patterns cleared
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        
        # Read all patterns
        patterns = self.read_patterns(limit=10000)
        
        # Filter patterns
        new_patterns = []
        cleared = 0
        
        for p in patterns:
            try:
                timestamp = datetime.fromisoformat(p['timestamp'])
                if timestamp >= cutoff:
                    new_patterns.append(p)
                else:
                    cleared += 1
            except (ValueError, KeyError):
                # Keep patterns with invalid timestamps
                new_patterns.append(p)
        
        # Rewrite patterns file
        if cleared > 0:
            import json
            
            # Clear and rewrite
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                for p in new_patterns:
                    f.write(json.dumps(p, ensure_ascii=False) + '\n')
        
        return cleared
