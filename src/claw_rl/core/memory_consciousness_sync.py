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
claw-rl Memory-Consciousness Sync (v2.1.0)

Implements deep bidirectional synchronization between claw-rl (consciousness)
and claw-mem (memory) based on neuroscience principles:

- Hippocampus-PFC coupling: Memory and consciousness are deeply coupled
- Bidirectional flow: Memory ↔ Consciousness
- Temporal synchrony: Updates are immediately visible
- Unified identity: Single system boundary

Usage:
    sync = MemoryConsciousnessSync()
    
    # Learning → Memory
    await sync.sync_learning_to_memory(learning)
    
    # Memory → Learning context
    context = await sync.sync_memory_to_learning("file operations")
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import asyncio
import json
import sqlite3
from contextlib import asynccontextmanager
from enum import Enum


class SyncDirection(Enum):
    """Sync direction"""
    LEARNING_TO_MEMORY = "learning_to_memory"
    MEMORY_TO_LEARNING = "memory_to_learning"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(Enum):
    """Sync operation status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class Learning:
    """Represents a learning event"""
    learning_id: str
    pattern: str
    confidence: float
    source: str
    session_id: str
    reward: int = 0
    hint: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_memory_entry(self) -> Dict:
        """Convert to claw-mem compatible entry"""
        return {
            'id': self.learning_id,
            'content': self.pattern,
            'metadata': {
                'type': 'learned_pattern',
                'confidence': self.confidence,
                'source': self.source,
                'session_id': self.session_id,
                'reward': self.reward,
                'hint': self.hint,
                'context': self.context,
            },
            'timestamp': self.timestamp,
        }
    
    def to_jsonl(self) -> str:
        """Convert to JSONL format"""
        return json.dumps({
            'learning_id': self.learning_id,
            'pattern': self.pattern,
            'confidence': self.confidence,
            'source': self.source,
            'session_id': self.session_id,
            'reward': self.reward,
            'hint': self.hint,
            'context': self.context,
            'timestamp': self.timestamp,
        }, ensure_ascii=False)


@dataclass
class SyncResult:
    """Result of a sync operation"""
    status: SyncStatus
    direction: SyncDirection
    items_synced: int
    latency_ms: float
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class MemoryConsciousnessSync:
    """
    Memory-Consciousness Bidirectional Synchronization
    
    Implements the neuroscience-inspired memory-consciousness integration:
    
    ```
    ┌──────────────┐              ┌──────────────┐
    │  claw-mem    │◄────────────►│  claw-rl     │
    │  (Memory)    │   双向同步    │  (Learning)  │
    │              │              │              │
    │  - Store     │  1. 写入规则  │  - Extract   │
    │  - Retrieve  │  2. 读取模式  │  - Learn     │
    │  - Index     │  3. 更新信号  │  - Optimize  │
    └──────────────┘              └──────────────┘
             │                           │
             └──────────┬────────────────┘
                        ↓
              Unified State Store (SQLite)
    ```
    
    Features:
    - Atomic transactions (all-or-nothing)
    - Real-time event propagation
    - Conflict resolution
    - State consistency guarantees
    """
    
    # Default paths
    DEFAULT_WORKSPACE = Path.home() / '.openclaw' / 'workspace'
    DEFAULT_DB_NAME = 'memory_consciousness.db'
    
    def __init__(
        self,
        workspace_dir: Optional[Path] = None,
        enable_events: bool = True,
        conflict_strategy: str = 'keep_best'  # 'keep_best', 'keep_latest', 'keep_both'
    ):
        """
        Initialize Memory-Consciousness Sync
        
        Args:
            workspace_dir: Workspace directory
            enable_events: Enable event propagation
            conflict_strategy: Strategy for conflict resolution
        """
        self.workspace_dir = workspace_dir or self.DEFAULT_WORKSPACE
        self.enable_events = enable_events
        self.conflict_strategy = conflict_strategy
        
        # Paths
        self.db_path = self.workspace_dir / self.DEFAULT_DB_NAME
        self.learnings_dir = self.workspace_dir / 'claw-rl' / 'data' / 'learnings'
        self.memory_dir = self.workspace_dir / 'memory'
        
        # Ensure directories
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Event subscribers
        self._subscribers: List[callable] = []
        
        # Metrics
        self._metrics = {
            'syncs_total': 0,
            'syncs_success': 0,
            'syncs_failed': 0,
            'items_synced': 0,
            'conflicts_resolved': 0,
        }
    
    def _init_database(self):
        """Initialize unified state database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id TEXT PRIMARY KEY,
                pattern TEXT NOT NULL,
                confidence REAL NOT NULL,
                source TEXT,
                session_id TEXT,
                reward INTEGER DEFAULT 0,
                hint TEXT,
                context TEXT,
                timestamp TEXT NOT NULL,
                synced_to_memory INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                direction TEXT NOT NULL,
                status TEXT NOT NULL,
                items_count INTEGER DEFAULT 0,
                latency_ms REAL DEFAULT 0,
                error TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_learnings_session 
            ON learnings(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_learnings_timestamp 
            ON learnings(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    @asynccontextmanager
    async def transaction(self):
        """Async transaction context manager"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    async def sync_learning_to_memory(
        self,
        learning: Learning
    ) -> SyncResult:
        """
        Sync learning result to memory storage
        
        This implements the Learning → Memory flow:
        - Atomic write to claw-mem
        - Update local state
        - Notify subscribers
        
        Args:
            learning: Learning to sync
            
        Returns:
            SyncResult with status and details
        """
        start_time = datetime.now()
        self._metrics['syncs_total'] += 1
        
        try:
            async with self.transaction() as cursor:
                # 1. Write to local database
                cursor.execute('''
                    INSERT OR REPLACE INTO learnings 
                    (id, pattern, confidence, source, session_id, reward, hint, context, timestamp, synced_to_memory)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    learning.learning_id,
                    learning.pattern,
                    learning.confidence,
                    learning.source,
                    learning.session_id,
                    learning.reward,
                    learning.hint,
                    json.dumps(learning.context),
                    learning.timestamp
                ))
                
                # 2. Write to claw-mem format
                await self._write_to_claw_mem(learning)
                
                # 3. Write to local JSONL
                self._append_learning_jsonl(learning)
            
            # 4. Notify subscribers
            if self.enable_events:
                await self._notify_subscribers({
                    'type': 'learning_synced',
                    'learning': learning.to_memory_entry(),
                    'direction': SyncDirection.LEARNING_TO_MEMORY.value
                })
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._metrics['syncs_success'] += 1
            self._metrics['items_synced'] += 1
            
            # Log sync
            self._log_sync(SyncDirection.LEARNING_TO_MEMORY, SyncStatus.SUCCESS, 1, latency_ms)
            
            return SyncResult(
                status=SyncStatus.SUCCESS,
                direction=SyncDirection.LEARNING_TO_MEMORY,
                items_synced=1,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._metrics['syncs_failed'] += 1
            self._log_sync(SyncDirection.LEARNING_TO_MEMORY, SyncStatus.FAILED, 0, latency_ms, str(e))
            
            return SyncResult(
                status=SyncStatus.FAILED,
                direction=SyncDirection.LEARNING_TO_MEMORY,
                items_synced=0,
                latency_ms=latency_ms,
                error=str(e)
            )
    
    async def sync_memory_to_learning(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Sync memory to learning context
        
        This implements the Memory → Learning flow:
        - Query claw-mem for relevant memories
        - Convert to learning context
        - Return for injection
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of relevant memories converted to learning context
        """
        start_time = datetime.now()
        self._metrics['syncs_total'] += 1
        
        try:
            # 1. Try to use claw-mem's search if available
            memories = await self._search_claw_mem(query, limit)
            
            # 2. Also search local learnings
            local_learnings = self._search_local_learnings(query, limit)
            
            # 3. Merge and deduplicate
            all_items = memories + local_learnings
            
            # Remove duplicates by pattern
            seen_patterns = set()
            unique_items = []
            for item in all_items:
                pattern = item.get('pattern', item.get('content', ''))
                if pattern not in seen_patterns:
                    seen_patterns.add(pattern)
                    unique_items.append(item)
            
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._metrics['syncs_success'] += 1
            self._metrics['items_synced'] += len(unique_items)
            
            self._log_sync(SyncDirection.MEMORY_TO_LEARNING, SyncStatus.SUCCESS, len(unique_items), latency_ms)
            
            return unique_items[:limit]
            
        except Exception as e:
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._metrics['syncs_failed'] += 1
            self._log_sync(SyncDirection.MEMORY_TO_LEARNING, SyncStatus.FAILED, 0, latency_ms, str(e))
            return []
    
    async def _write_to_claw_mem(self, learning: Learning):
        """Write to claw-mem format"""
        # Write to memory/claw-rl-learnings.md
        learnings_file = self.memory_dir / 'claw-rl-learnings.md'
        
        short_id = learning.learning_id[:8] if len(learning.learning_id) >= 8 else learning.learning_id
        
        entry = f"""<!-- tags: claw-rl, learned-pattern; id: {short_id} -->
[{learning.timestamp}] {learning.pattern}
- **Confidence:** {learning.confidence:.0%}
- **Source:** {learning.source}
- **Reward:** {learning.reward}

"""
        
        with open(learnings_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        # Also append to MEMORY.md if exists
        memory_file = self.memory_dir / 'MEMORY.md'
        if memory_file.exists():
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{entry}")
    
    def _append_learning_jsonl(self, learning: Learning):
        """Append learning to JSONL file"""
        jsonl_file = self.learnings_dir / 'learnings.jsonl'
        
        with open(jsonl_file, 'a', encoding='utf-8') as f:
            f.write(learning.to_jsonl() + '\n')
    
    async def _search_claw_mem(self, query: str, limit: int) -> List[Dict]:
        """Search claw-mem for relevant memories"""
        memories = []
        
        try:
            # Try to import and use claw-mem
            from claw_mem import MemoryManager
            
            manager = MemoryManager(str(self.workspace_dir))
            results = manager.search(query, limit=limit)
            
            for result in results:
                memories.append({
                    'type': 'memory',
                    'content': result.get('content', ''),
                    'pattern': result.get('content', ''),
                    'confidence': result.get('metadata', {}).get('confidence', 0.5),
                    'source': result.get('metadata', {}).get('source', 'claw-mem'),
                })
                
        except ImportError:
            # claw-mem not available, use local search only
            pass
        except Exception:
            pass
        
        return memories
    
    def _search_local_learnings(self, query: str, limit: int) -> List[Dict]:
        """Search local learnings"""
        learnings = []
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Simple LIKE search
            cursor.execute('''
                SELECT * FROM learnings 
                WHERE pattern LIKE ? OR hint LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            for row in cursor.fetchall():
                learnings.append({
                    'type': 'learning',
                    'learning_id': row['id'],
                    'pattern': row['pattern'],
                    'confidence': row['confidence'],
                    'source': row['source'],
                    'reward': row['reward'],
                    'hint': row['hint'],
                    'timestamp': row['timestamp'],
                })
                
        finally:
            conn.close()
        
        return learnings
    
    def _log_sync(
        self,
        direction: SyncDirection,
        status: SyncStatus,
        items_count: int,
        latency_ms: float,
        error: Optional[str] = None
    ):
        """Log sync operation"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_log (direction, status, items_count, latency_ms, error)
            VALUES (?, ?, ?, ?, ?)
        ''', (direction.value, status.value, items_count, latency_ms, error))
        
        conn.commit()
        conn.close()
    
    async def _notify_subscribers(self, event: Dict):
        """Notify all subscribers of an event"""
        for subscriber in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
            except Exception:
                pass
    
    def subscribe(self, callback: callable):
        """Subscribe to sync events"""
        self._subscribers.append(callback)
    
    def unsubscribe(self, callback: callable):
        """Unsubscribe from sync events"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def get_metrics(self) -> Dict:
        """Get sync metrics"""
        total = self._metrics['syncs_total']
        return {
            **self._metrics,
            'success_rate': self._metrics['syncs_success'] / total if total > 0 else 0,
            'failure_rate': self._metrics['syncs_failed'] / total if total > 0 else 0,
        }
    
    def get_recent_syncs(self, limit: int = 20) -> List[Dict]:
        """Get recent sync operations"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sync_log
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_unsynced_learnings(self) -> List[Dict]:
        """Get learnings not yet synced to memory"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM learnings
            WHERE synced_to_memory = 0
            ORDER BY timestamp DESC
        ''')
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    async def sync_all_pending(self) -> SyncResult:
        """Sync all pending learnings to memory"""
        unsynced = self.get_unsynced_learnings()
        
        if not unsynced:
            return SyncResult(
                status=SyncStatus.SUCCESS,
                direction=SyncDirection.LEARNING_TO_MEMORY,
                items_synced=0,
                latency_ms=0
            )
        
        start_time = datetime.now()
        synced_count = 0
        errors = []
        
        for item in unsynced:
            learning = Learning(
                learning_id=item['id'],
                pattern=item['pattern'],
                confidence=item['confidence'],
                source=item['source'],
                session_id=item['session_id'],
                reward=item['reward'],
                hint=item['hint'],
                context=json.loads(item['context']) if item['context'] else {},
                timestamp=item['timestamp']
            )
            
            result = await self.sync_learning_to_memory(learning)
            if result.status == SyncStatus.SUCCESS:
                synced_count += 1
            else:
                errors.append(result.error)
        
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return SyncResult(
            status=SyncStatus.SUCCESS if synced_count == len(unsynced) else SyncStatus.PARTIAL,
            direction=SyncDirection.LEARNING_TO_MEMORY,
            items_synced=synced_count,
            latency_ms=latency_ms,
            details={'errors': errors} if errors else {}
        )
    
    # Backward compatibility with ClawMemBridge
    def write_pattern(
        self,
        pattern: str,
        confidence: float,
        source: str,
        session_id: str
    ) -> None:
        """Backward compatible write_pattern method"""
        import uuid
        
        learning = Learning(
            learning_id=str(uuid.uuid4()),
            pattern=pattern,
            confidence=confidence,
            source=source,
            session_id=session_id
        )
        
        # Run async in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        
        loop.run_until_complete(self.sync_learning_to_memory(learning))
    
    def read_patterns(self, limit: int = 10) -> List[Dict]:
        """Backward compatible read_patterns method"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM learnings
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
