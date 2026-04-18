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
Tests for Rule Portability v2.0
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile

from claw_rl.rule_portability import (
    ExportedRule,
    RuleVersion,
    RuleLineage,
    RuleMergeStrategy,
)
from claw_rl.rule_portability_v2 import (
    RulePortabilityV2,
    export_rules_to_markdown,
)


class TestRulePortabilityV2:
    """Tests for enhanced Rule Portability"""
    
    @pytest.fixture
    def portability(self):
        """Create RulePortabilityV2 instance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield RulePortabilityV2(Path(tmpdir))
    
    @pytest.fixture
    def sample_rules(self):
        """Create sample rules for testing"""
        return [
            ExportedRule(
                rule_id="rule-001",
                rule_type="behavior",
                condition="操作文件前",
                action="检查目标路径是否存在",
                confidence=0.85,
                source="user_feedback",
                version=RuleVersion(
                    version="1.0.0",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    author="test",
                ),
                lineage=RuleLineage(
                    rule_id="rule-001",
                    parent_rules=["rule-parent-1"],
                    feedback_sources=["session-123"],
                ),
            ),
            ExportedRule(
                rule_id="rule-002",
                rule_type="prompt",
                condition="用户询问天气",
                action="使用 weather skill",
                confidence=0.92,
                source="opd",
            ),
        ]
    
    def test_init(self, portability):
        """Test initialization"""
        assert portability.EXPORT_FORMAT_VERSION == "2.1.0"
        assert portability.exports_dir.exists()
    
    def test_export_json(self, portability, sample_rules):
        """Test JSON export"""
        result = portability.export_rules(sample_rules, format="json")
        
        assert result.success
        assert result.rules_exported == 2
        assert result.format == "json"
        assert result.path is not None
    
    def test_export_markdown(self, portability, sample_rules):
        """Test Markdown export"""
        result = portability.export_rules(sample_rules, format="markdown")
        
        assert result.success
        assert result.rules_exported == 2
        assert result.format == "markdown"
        assert result.path is not None
        
        # Check content
        content = Path(result.path).read_text()
        assert "# claw-rl Rules Export" in content
        assert "rule-001" in content
        assert "检查目标路径是否存在" in content
    
    def test_export_yaml(self, portability, sample_rules):
        """Test YAML export"""
        result = portability.export_rules(sample_rules, format="yaml")
        
        assert result.success
        assert result.rules_exported == 2
        assert result.format == "yaml"
    
    def test_export_empty_rules(self, portability):
        """Test export with empty rules"""
        result = portability.export_rules([], format="json")
        
        assert result.success
        assert result.rules_exported == 0
    
    def test_validate_rules_valid(self, portability, sample_rules):
        """Test validation with valid rules"""
        errors = portability.validate_rules(sample_rules)
        
        assert len(errors) == 0
    
    def test_validate_rules_invalid(self, portability):
        """Test validation with invalid rules"""
        invalid_rule = ExportedRule(
            rule_id="",  # Missing
            rule_type="",  # Missing
            condition="",  # Missing
            action="test",
            confidence=1.5,  # Invalid range
        )
        
        errors = portability.validate_rules([invalid_rule])
        
        assert len(errors) > 0
        assert "unknown" in errors
    
    def test_migrate_format_same_version(self, portability):
        """Test migration with same version"""
        data = {
            "format_version": "2.1.0",
            "rules": [],
        }
        
        migrated = portability.migrate_format(data, "2.1.0")
        
        assert migrated["format_version"] == "2.1.0"
    
    def test_migrate_format_v1_to_v2(self, portability):
        """Test migration from v1.0.0 to v2.1.0"""
        data = {
            "format_version": "1.0.0",
            "exported_at": "2026-01-01T00:00:00",
            "rules": [
                {
                    "rule_id": "rule-001",
                    "rule_type": "behavior",
                    "condition": "test",
                    "action": "test",
                    "confidence": 0.8,
                    "source": "test",
                }
            ],
        }
        
        migrated = portability.migrate_format(data, "1.0.0")
        
        assert migrated["format_version"] == "2.1.0"
        assert "lineage" in migrated["rules"][0]
        assert "version" in migrated["rules"][0]
    
    def test_get_rule_diff_same(self, portability, sample_rules):
        """Test diff with identical rules"""
        diff = portability.get_rule_diff(sample_rules[0], sample_rules[0])
        
        assert diff["rule_id"] == "rule-001"
        assert len(diff["differences"]) == 0
    
    def test_get_rule_diff_different(self, portability, sample_rules):
        """Test diff with different rules"""
        modified = ExportedRule(
            rule_id="rule-001",
            rule_type="behavior",
            condition="modified condition",
            action="modified action",
            confidence=0.5,
            source="test",
        )
        
        diff = portability.get_rule_diff(sample_rules[0], modified)
        
        assert len(diff["differences"]) == 3
        fields = [d["field"] for d in diff["differences"]]
        assert "condition" in fields
        assert "action" in fields
        assert "confidence" in fields


class TestExportRulesToMarkdown:
    """Tests for convenience function"""
    
    def test_export_to_markdown(self):
        """Test convenience function"""
        rules = [
            ExportedRule(
                rule_id="test-rule",
                rule_type="behavior",
                condition="test condition",
                action="test action",
                confidence=0.8,
                source="test",
            )
        ]
        
        markdown = export_rules_to_markdown(rules)
        
        assert "# claw-rl Rules Export" in markdown
        assert "test-rule" in markdown
