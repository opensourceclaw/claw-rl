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
Tests for claw-rl Memory-Consciousness Sync (v2.1.0)
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from claw_rl.core.memory_consciousness_sync import (
    MemoryConsciousnessSync,
    Learning,
    SyncResult,
    SyncDirection,
    SyncStatus,
)


class TestLearning:
    """Tests for Learning dataclass"""
    
    def test_to_memory_entry(self):
        """Test conversion to memory entry"""
        learning = Learning(
            learning_id='test-001',
            pattern='操作前先检查目标文件',
            confidence=0.85,
            source='User correction',
            session_id='session-abc'
        )
        
        entry = learning.to_memory_entry()
        
        assert entry['id'] == 'test-001'
        assert entry['content'] == '操作前先检查目标文件'
        assert entry['metadata']['confidence'] == 0.85
        assert entry['metadata']['source'] == 'User correction'
    
    def test_to_jsonl(self):
        """Test conversion to JSONL"""
        learning = Learning(
            learning_id='test-002',
            pattern='Test pattern',
            confidence=0.9,
            source='Test',
            session_id='sess-123'
        )
        
        jsonl = learning.to_jsonl()
        
        assert '"learning_id": "test-002"' in jsonl
        assert '"pattern": "Test pattern"' in jsonl


class TestMemoryConsciousnessSync:
    """Tests for MemoryConsciousnessSync"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sync(self, temp_workspace):
        """Create sync instance with temp workspace"""
        return MemoryConsciousnessSync(workspace_dir=temp_workspace)
    
    def test_init(self, sync, temp_workspace):
        """Test initialization"""
        assert sync.workspace_dir == temp_workspace
        assert sync.db_path.exists()
        assert sync.learnings_dir.exists()
    
    def test_init_creates_database(self, sync):
        """Test database creation"""
        assert sync.db_path.exists()
        
        # Check tables exist
        import sqlite3
        conn = sqlite3.connect(str(sync.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        assert 'learnings' in tables
        assert 'sync_log' in tables
        
        conn.close()
    
    @pytest.mark.asyncio
    async def test_sync_learning_to_memory(self, sync):
        """Test learning → memory sync"""
        learning = Learning(
            learning_id='test-sync-001',
            pattern='测试模式',
            confidence=0.9,
            source='Test',
            session_id='session-001'
        )
        
        result = await sync.sync_learning_to_memory(learning)
        
        assert result.status == SyncStatus.SUCCESS
        assert result.items_synced == 1
        assert result.direction == SyncDirection.LEARNING_TO_MEMORY
    
    @pytest.mark.asyncio
    async def test_sync_learning_writes_to_db(self, sync):
        """Test learning is written to database"""
        learning = Learning(
            learning_id='test-db-001',
            pattern='数据库测试',
            confidence=0.8,
            source='Test',
            session_id='session-002'
        )
        
        await sync.sync_learning_to_memory(learning)
        
        # Check database
        import sqlite3
        conn = sqlite3.connect(str(sync.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM learnings WHERE id = ?", ('test-db-001',))
        row = cursor.fetchone()
        
        assert row is not None
        assert row[1] == '数据库测试'  # pattern
        
        conn.close()
    
    @pytest.mark.asyncio
    async def test_sync_learning_writes_to_claw_mem(self, sync):
        """Test learning is written to claw-mem format"""
        learning = Learning(
            learning_id='test-mem-001',
            pattern='记忆测试',
            confidence=0.85,
            source='Test',
            session_id='session-003'
        )
        
        await sync.sync_learning_to_memory(learning)
        
        # Check claw-mem file
        learnings_file = sync.memory_dir / 'claw-rl-learnings.md'
        assert learnings_file.exists()
        
        content = learnings_file.read_text()
        assert '记忆测试' in content
        assert '85%' in content
    
    @pytest.mark.asyncio
    async def test_sync_learning_writes_jsonl(self, sync):
        """Test learning is written to JSONL"""
        learning = Learning(
            learning_id='test-jsonl-001',
            pattern='JSONL测试',
            confidence=0.75,
            source='Test',
            session_id='session-004'
        )
        
        await sync.sync_learning_to_memory(learning)
        
        jsonl_file = sync.learnings_dir / 'learnings.jsonl'
        assert jsonl_file.exists()
        
        content = jsonl_file.read_text()
        assert 'test-jsonl-001' in content
        assert 'JSONL测试' in content
    
    @pytest.mark.asyncio
    async def test_sync_memory_to_learning(self, sync):
        """Test memory → learning sync"""
        # First, add a learning
        learning = Learning(
            learning_id='test-retrieve-001',
            pattern='检索测试模式',
            confidence=0.9,
            source='Test',
            session_id='session-005'
        )
        
        await sync.sync_learning_to_memory(learning)
        
        # Now search for it
        results = await sync.sync_memory_to_learning('检索测试')
        
        assert len(results) > 0
        assert any('检索测试模式' in r.get('pattern', '') for r in results)
    
    @pytest.mark.asyncio
    async def test_sync_memory_to_learning_empty(self, sync):
        """Test memory → learning with no results"""
        results = await sync.sync_memory_to_learning('nonexistent_pattern_xyz')
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_event_notification(self, sync):
        """Test event notification on sync"""
        events = []
        
        def callback(event):
            events.append(event)
        
        sync.subscribe(callback)
        
        learning = Learning(
            learning_id='test-event-001',
            pattern='事件测试',
            confidence=0.8,
            source='Test',
            session_id='session-006'
        )
        
        await sync.sync_learning_to_memory(learning)
        
        assert len(events) == 1
        assert events[0]['type'] == 'learning_synced'
    
    def test_subscribe_unsubscribe(self, sync):
        """Test subscribe and unsubscribe"""
        def callback(event):
            pass
        
        sync.subscribe(callback)
        assert callback in sync._subscribers
        
        sync.unsubscribe(callback)
        assert callback not in sync._subscribers
    
    def test_get_metrics(self, sync):
        """Test metrics retrieval"""
        metrics = sync.get_metrics()
        
        assert 'syncs_total' in metrics
        assert 'syncs_success' in metrics
        assert 'syncs_failed' in metrics
        assert 'items_synced' in metrics
    
    @pytest.mark.asyncio
    async def test_get_recent_syncs(self, sync):
        """Test recent sync log retrieval"""
        learning = Learning(
            learning_id='test-log-001',
            pattern='日志测试',
            confidence=0.8,
            source='Test',
            session_id='session-007'
        )
        
        await sync.sync_learning_to_memory(learning)
        
        recent = sync.get_recent_syncs(limit=10)
        
        assert len(recent) > 0
        assert recent[0]['direction'] == 'learning_to_memory'
        assert recent[0]['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_get_unsynced_learnings(self, sync):
        """Test getting unsynced learnings"""
        # Direct database insert without sync
        import sqlite3
        conn = sqlite3.connect(str(sync.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learnings (id, pattern, confidence, source, session_id, timestamp, synced_to_memory)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', ('unsynced-001', '未同步模式', 0.8, 'Test', 'session-008', '2026-04-18T00:00:00'))
        
        conn.commit()
        conn.close()
        
        unsynced = sync.get_unsynced_learnings()
        
        assert len(unsynced) > 0
        assert any(u['id'] == 'unsynced-001' for u in unsynced)
    
    @pytest.mark.asyncio
    async def test_sync_all_pending(self, sync):
        """Test syncing all pending learnings"""
        # Add unsynced learning directly to DB
        import sqlite3
        conn = sqlite3.connect(str(sync.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learnings (id, pattern, confidence, source, session_id, timestamp, synced_to_memory)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', ('pending-001', '待同步模式', 0.9, 'Test', 'session-009', '2026-04-18T00:00:00'))
        
        conn.commit()
        conn.close()
        
        result = await sync.sync_all_pending()
        
        assert result.status == SyncStatus.SUCCESS
        assert result.items_synced >= 1
    
    # Backward compatibility tests
    
    def test_write_pattern_backward_compat(self, sync):
        """Test backward compatible write_pattern"""
        sync.write_pattern(
            pattern='兼容性测试',
            confidence=0.85,
            source='Test',
            session_id='session-compat'
        )
        
        # Check it was written
        patterns = sync.read_patterns(limit=10)
        
        assert any('兼容性测试' in p.get('pattern', '') for p in patterns)
    
    def test_read_patterns_backward_compat(self, sync):
        """Test backward compatible read_patterns"""
        import asyncio
        
        learning = Learning(
            learning_id='compat-read-001',
            pattern='读取测试',
            confidence=0.8,
            source='Test',
            session_id='session-read'
        )
        
        # Use proper event loop handling
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        loop.run_until_complete(sync.sync_learning_to_memory(learning))
        
        patterns = sync.read_patterns(limit=10)
        
        assert isinstance(patterns, list)


class TestSyncResult:
    """Tests for SyncResult dataclass"""
    
    def test_default_values(self):
        """Test default values"""
        result = SyncResult(
            status=SyncStatus.SUCCESS,
            direction=SyncDirection.LEARNING_TO_MEMORY,
            items_synced=1,
            latency_ms=10.5
        )
        
        assert result.error is None
        assert result.details == {}
    
    def test_with_error(self):
        """Test with error"""
        result = SyncResult(
            status=SyncStatus.FAILED,
            direction=SyncDirection.MEMORY_TO_LEARNING,
            items_synced=0,
            latency_ms=5.0,
            error='Connection failed'
        )
        
        assert result.status == SyncStatus.FAILED
        assert result.error == 'Connection failed'


class TestEdgeCases:
    """Tests for edge cases"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sync(self, temp_workspace):
        """Create sync instance"""
        return MemoryConsciousnessSync(workspace_dir=temp_workspace)
    
    @pytest.mark.asyncio
    async def test_duplicate_learning_id(self, sync):
        """Test handling duplicate learning ID"""
        learning1 = Learning(
            learning_id='duplicate-001',
            pattern='原始模式',
            confidence=0.8,
            source='Test',
            session_id='session-001'
        )
        
        learning2 = Learning(
            learning_id='duplicate-001',  # Same ID
            pattern='更新模式',
            confidence=0.9,
            source='Test',
            session_id='session-002'
        )
        
        result1 = await sync.sync_learning_to_memory(learning1)
        result2 = await sync.sync_learning_to_memory(learning2)
        
        assert result1.status == SyncStatus.SUCCESS
        assert result2.status == SyncStatus.SUCCESS
        
        # Should have updated, not duplicated
        patterns = sync.read_patterns()
        matching = [p for p in patterns if p['id'] == 'duplicate-001']
        
        assert len(matching) <= 1
    
    @pytest.mark.asyncio
    async def test_long_pattern(self, sync):
        """Test handling long pattern"""
        long_pattern = '这是一个非常长的模式描述' * 100
        
        learning = Learning(
            learning_id='long-001',
            pattern=long_pattern,
            confidence=0.8,
            source='Test',
            session_id='session-long'
        )
        
        result = await sync.sync_learning_to_memory(learning)
        
        assert result.status == SyncStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_special_characters(self, sync):
        """Test handling special characters"""
        learning = Learning(
            learning_id='special-001',
            pattern='特殊字符测试 !@#$%^&*(){}[]|\\:";\'<>?,./~`',
            confidence=0.8,
            source='Test',
            session_id='session-special'
        )
        
        result = await sync.sync_learning_to_memory(learning)
        
        assert result.status == SyncStatus.SUCCESS
    
    @pytest.mark.asyncio
    async def test_unicode_pattern(self, sync):
        """Test handling unicode pattern"""
        learning = Learning(
            learning_id='unicode-001',
            pattern='日本語テスト 한국어 테스트 العربية',
            confidence=0.8,
            source='Test',
            session_id='session-unicode'
        )
        
        result = await sync.sync_learning_to_memory(learning)
        
        assert result.status == SyncStatus.SUCCESS
        
        # Verify retrieval
        patterns = sync.read_patterns()
        assert any('日本語' in p.get('pattern', '') for p in patterns)
