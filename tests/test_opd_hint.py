"""
Tests for OPD Hint Extractor

Run with: pytest tests/test_opd_hint.py -v
"""

import pytest
from claw_rl.feedback.opd_hint import OPDHint, OPDHintExtractor


class TestOPDHint:
    """Test suite for OPDHint dataclass."""
    
    def test_hint_creation(self):
        """Test creating an OPDHint."""
        hint = OPDHint(
            hint_type='should',
            content='操作前检查文件',
            priority=3,
            confidence=0.9
        )
        assert hint.hint_type == 'should'
        assert hint.content == '操作前检查文件'
        assert hint.priority == 3
        assert hint.confidence == 0.9
    
    def test_hint_to_dict(self):
        """Test converting hint to dictionary."""
        hint = OPDHint('should', 'content', 3, 0.9)
        data = hint.to_dict()
        assert isinstance(data, dict)
        assert data['hint_type'] == 'should'
        assert data['content'] == 'content'
        assert data['priority'] == 3
        assert data['confidence'] == 0.9


class TestOPDHintExtractor:
    """Test suite for OPDHintExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create an OPDHintExtractor instance for testing."""
        return OPDHintExtractor()
    
    # Should pattern tests
    def test_should_pattern_simple(self, extractor):
        """Test simple '应该' pattern."""
        hint = extractor.extract("应该检查文件")
        assert hint is not None
        assert hint.hint_type == 'should'
        assert '检查文件' in hint.content
    
    def test_should_pattern_with_context(self, extractor):
        """Test '应该' pattern with context."""
        # Must START with "应该" to match
        hint = extractor.extract("应该先确认")
        assert hint is not None
        assert hint.hint_type == 'should'
    
    # Should not pattern tests
    def test_should_not_pattern(self, extractor):
        """Test '不要' pattern."""
        hint = extractor.extract("不要放到这里")
        assert hint is not None
        assert hint.hint_type == 'should_not'
        assert '放到这里' in hint.content
    
    # Sequence pattern tests
    def test_sequence_pattern(self, extractor):
        """Test '先 X 再 Y' pattern."""
        hint = extractor.extract("先确认目录,再创建文件")
        assert hint is not None
        assert hint.hint_type == 'sequence'
        assert '确认目录' in hint.content
        assert '创建文件' in hint.content
    
    def test_sequence_pattern_no_comma(self, extractor):
        """Test '先 X 再 Y' pattern without comma."""
        hint = extractor.extract("先检查再执行")
        assert hint is not None
        assert hint.hint_type == 'sequence'
    
    # Conditional pattern tests
    def test_conditional_pattern(self, extractor):
        """Test '如果 X,则 Y' pattern."""
        hint = extractor.extract("如果是配置文件,则放到 config 目录")
        assert hint is not None
        assert hint.hint_type == 'conditional'
        assert '配置文件' in hint.content
        assert 'config 目录' in hint.content
    
    # No match tests
    def test_no_match_simple(self, extractor):
        """Test feedback with no matching pattern."""
        hint = extractor.extract("谢谢")
        assert hint is None
    
    def test_no_match_empty(self, extractor):
        """Test empty feedback."""
        hint = extractor.extract("")
        assert hint is None
    
    def test_no_match_whitespace(self, extractor):
        """Test whitespace-only feedback."""
        hint = extractor.extract("   ")
        assert hint is None
    
    # Batch extraction tests
    def test_extract_all(self, extractor):
        """Test extracting hints from multiple feedbacks."""
        feedbacks = [
            "应该检查文件",
            "不要放这里",
            "谢谢",  # No hint
            "先确认再执行",
        ]
        hints = extractor.extract_all(feedbacks)
        assert len(hints) == 3  # "谢谢" should not produce a hint
    
    # Deduplication tests
    def test_deduplicate_same_content(self, extractor):
        """Test deduplication with same content."""
        hints = [
            OPDHint('should', '检查文件', 3, 0.9),
            OPDHint('should', '检查文件', 4, 0.95),  # Higher priority
        ]
        deduped = extractor.deduplicate(hints)
        assert len(deduped) == 1
        assert deduped[0].priority == 4  # Higher priority wins
    
    def test_deduplicate_different_content(self, extractor):
        """Test deduplication with different content."""
        hints = [
            OPDHint('should', '检查文件', 3, 0.9),
            OPDHint('should_not', '放这里', 4, 0.9),
        ]
        deduped = extractor.deduplicate(hints)
        assert len(deduped) == 2  # Both kept (different content)
    
    # Statistics test
    def test_get_statistics(self, extractor):
        """Test getting statistics."""
        stats = extractor.get_statistics()
        assert 'pattern_types' in stats
        assert stats['pattern_types'] == 4  # should, should_not, sequence, conditional
        assert 'patterns' in stats
        assert len(stats['patterns']) == 4
    
    # Edge cases
    def test_whitespace_handling(self, extractor):
        """Test whitespace handling in feedback."""
        hint1 = extractor.extract("  应该检查文件  ")
        hint2 = extractor.extract("应该检查文件")
        assert hint1 is not None
        assert hint2 is not None
        assert hint1.content == hint2.content
    
    def test_mixed_patterns_priority(self, extractor):
        """Test that sequence pattern has higher priority."""
        hint = extractor.extract("先确认目录,再创建文件")
        assert hint is not None
        assert hint.priority == 5  # Sequence has highest priority
    
    # Comprehensive test cases
    @pytest.mark.parametrize("feedback,expected_type", [
        ("应该检查", 'should'),
        ("应该先确认", 'should'),
        ("不要放这里", 'should_not'),
        ("不要这样做", 'should_not'),
        ("先 A 再 B", 'sequence'),
        ("先确认再执行", 'sequence'),
        ("如果 X,则 Y", 'conditional'),
        ("如果是这样,就那样", 'conditional'),
        ("谢谢", None),
        ("很好", None),
        ("", None),
    ])
    def test_comprehensive_patterns(self, extractor, feedback, expected_type):
        """Test comprehensive pattern coverage."""
        hint = extractor.extract(feedback)
        if expected_type is None:
            assert hint is None
        else:
            assert hint is not None
            assert hint.hint_type == expected_type
