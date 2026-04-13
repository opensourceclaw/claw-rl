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
Tests for Rule Portability Module
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import json

from claw_rl.rule_portability import (
    RulePortability,
    ExportedRule,
    RuleVersion,
    RuleLineage,
    RuleMergeStrategy,
    RuleExportResult,
    RuleImportResult,
)


class TestRuleVersion:
    """Tests for RuleVersion"""
    
    def test_create_version(self):
        """Test creating a version"""
        version = RuleVersion(
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        assert version.version == "1.0.0"
        assert version.author == "claw-rl"
    
    def test_version_to_dict(self):
        """Test version serialization"""
        version = RuleVersion(
            version="1.0.0",
            created_at=datetime(2026, 4, 7, 12, 0, 0),
            updated_at=datetime(2026, 4, 7, 12, 0, 0),
            author="test",
            changes=["Initial version"],
        )
        
        data = version.to_dict()
        
        assert data["version"] == "1.0.0"
        assert data["author"] == "test"
        assert "Initial version" in data["changes"]
    
    def test_version_from_dict(self):
        """Test version deserialization"""
        data = {
            "version": "2.0.0",
            "created_at": "2026-04-07T12:00:00",
            "updated_at": "2026-04-07T13:00:00",
            "author": "test",
            "changes": ["Update 1", "Update 2"],
        }
        
        version = RuleVersion.from_dict(data)
        
        assert version.version == "2.0.0"
        assert version.author == "test"
        assert len(version.changes) == 2


class TestRuleLineage:
    """Tests for RuleLineage"""
    
    def test_create_lineage(self):
        """Test creating lineage"""
        lineage = RuleLineage(
            rule_id="rule_001",
            parent_rules=["rule_000"],
            derived_from=["feedback_001"],
        )
        
        assert lineage.rule_id == "rule_001"
        assert "rule_000" in lineage.parent_rules
    
    def test_lineage_to_dict(self):
        """Test lineage serialization"""
        lineage = RuleLineage(
            rule_id="rule_001",
            parent_rules=["rule_000"],
            feedback_sources=["user_feedback"],
        )
        
        data = lineage.to_dict()
        
        assert data["rule_id"] == "rule_001"
        assert "user_feedback" in data["feedback_sources"]
    
    def test_lineage_from_dict(self):
        """Test lineage deserialization"""
        data = {
            "rule_id": "rule_002",
            "parent_rules": ["rule_001"],
            "derived_from": ["opd_001"],
            "feedback_sources": ["feedback_001", "feedback_002"],
        }
        
        lineage = RuleLineage.from_dict(data)
        
        assert lineage.rule_id == "rule_002"
        assert len(lineage.feedback_sources) == 2


class TestExportedRule:
    """Tests for ExportedRule"""
    
    def test_create_rule(self):
        """Test creating an exported rule"""
        rule = ExportedRule(
            rule_id="rule_001",
            rule_type="behavior",
            condition="user_prefers_concise",
            action="use_short_responses",
            confidence=0.9,
            source="feedback",
        )
        
        assert rule.rule_id == "rule_001"
        assert rule.confidence == 0.9
    
    def test_rule_to_dict(self):
        """Test rule serialization"""
        rule = ExportedRule(
            rule_id="rule_001",
            rule_type="prompt",
            condition="task_is_coding",
            action="use_code_template",
            confidence=0.8,
            metadata={"template": "python"},
        )
        
        data = rule.to_dict()
        
        assert data["rule_id"] == "rule_001"
        assert data["rule_type"] == "prompt"
        assert data["metadata"]["template"] == "python"
    
    def test_rule_from_dict(self):
        """Test rule deserialization"""
        data = {
            "rule_id": "rule_003",
            "rule_type": "parameter",
            "condition": "model_response_slow",
            "action": "reduce_temperature",
            "confidence": 0.7,
            "source": "calibration",
        }
        
        rule = ExportedRule.from_dict(data)
        
        assert rule.rule_id == "rule_003"
        assert rule.confidence == 0.7
    
    def test_rule_with_version(self):
        """Test rule with version"""
        version = RuleVersion(
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        rule = ExportedRule(
            rule_id="rule_004",
            rule_type="behavior",
            condition="test",
            action="test",
            version=version,
        )
        
        data = rule.to_dict()
        assert "version" in data
        assert data["version"]["version"] == "1.0.0"
    
    def test_rule_with_lineage(self):
        """Test rule with lineage"""
        lineage = RuleLineage(
            rule_id="rule_005",
            parent_rules=["rule_004"],
        )
        
        rule = ExportedRule(
            rule_id="rule_005",
            rule_type="behavior",
            condition="test",
            action="test",
            lineage=lineage,
        )
        
        data = rule.to_dict()
        assert "lineage" in data
        assert "rule_004" in data["lineage"]["parent_rules"]


class TestRulePortability:
    """Tests for RulePortability"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def rp(self, temp_workspace):
        """Create RulePortability instance"""
        return RulePortability(temp_workspace)
    
    def test_export_empty_rules(self, rp):
        """Test exporting empty rules list"""
        result = rp.export_rules([])
        
        assert result.success is True
        assert result.rules_exported == 0
    
    def test_export_single_rule(self, rp):
        """Test exporting a single rule"""
        rule = ExportedRule(
            rule_id="rule_001",
            rule_type="behavior",
            condition="user_likes_concise",
            action="use_short_responses",
            confidence=0.9,
        )
        
        result = rp.export_rules([rule])
        
        assert result.success is True
        assert result.rules_exported == 1
        assert result.path is not None
    
    def test_export_multiple_rules(self, rp):
        """Test exporting multiple rules"""
        rules = [
            ExportedRule(
                rule_id=f"rule_{i:03d}",
                rule_type="behavior",
                condition=f"condition_{i}",
                action=f"action_{i}",
                confidence=0.8,
            )
            for i in range(5)
        ]
        
        result = rp.export_rules(rules)
        
        assert result.success is True
        assert result.rules_exported == 5
    
    def test_export_to_custom_path(self, rp, temp_workspace):
        """Test exporting to custom path"""
        custom_path = str(temp_workspace / "custom_export.json")
        
        rule = ExportedRule(
            rule_id="rule_001",
            rule_type="behavior",
            condition="test",
            action="test",
        )
        
        result = rp.export_rules([rule], output_path=custom_path)
        
        assert result.success is True
        assert result.path == custom_path
        assert Path(custom_path).exists()
    
    def test_export_without_lineage(self, rp):
        """Test exporting without lineage"""
        lineage = RuleLineage(rule_id="rule_001")
        rule = ExportedRule(
            rule_id="rule_001",
            rule_type="behavior",
            condition="test",
            action="test",
            lineage=lineage,
        )
        
        result = rp.export_rules([rule], include_lineage=False)
        
        assert result.success is True
        
        # Verify lineage not included
        with open(result.path, "r") as f:
            data = json.load(f)
        
        assert "lineage" not in data["rules"][0]
    
    def test_import_rules(self, rp):
        """Test importing rules"""
        # First export
        rules = [
            ExportedRule(
                rule_id=f"rule_{i:03d}",
                rule_type="behavior",
                condition=f"condition_{i}",
                action=f"action_{i}",
            )
            for i in range(3)
        ]
        
        export_result = rp.export_rules(rules)
        assert export_result.success is True
        
        # Then import
        import_result = rp.import_rules(export_result.path)
        
        assert import_result.success is True
        assert import_result.rules_imported == 3
    
    def test_import_with_merge(self, rp):
        """Test importing with merge strategy"""
        # Export rules
        rules = [
            ExportedRule(
                rule_id="rule_001",
                rule_type="behavior",
                condition="test",
                action="test",
            )
        ]
        
        export_result = rp.export_rules(rules)
        
        # Import with MERGE strategy
        import_result = rp.import_rules(
            export_result.path,
            merge_strategy=RuleMergeStrategy.MERGE,
        )
        
        assert import_result.success is True
    
    def test_import_with_skip(self, rp):
        """Test importing with skip strategy"""
        # Create rule
        rule = ExportedRule(
            rule_id="rule_001",
            rule_type="behavior",
            condition="test",
            action="test",
        )
        
        # Export
        export_result = rp.export_rules([rule])
        
        # Create existing rule dict
        existing_rules = [{"rule_id": "rule_001"}]
        
        # Import with SKIP strategy
        import_result = rp.import_rules(
            export_result.path,
            existing_rules=existing_rules,
            merge_strategy=RuleMergeStrategy.SKIP,
        )
        
        assert import_result.success is True
        assert import_result.rules_skipped == 1
    
    def test_import_invalid_format(self, rp, temp_workspace):
        """Test importing invalid format"""
        invalid_path = str(temp_workspace / "invalid.json")
        
        with open(invalid_path, "w") as f:
            json.dump({"invalid": "data"}, f)
        
        result = rp.import_rules(invalid_path)
        
        assert result.success is False
        assert "Invalid import format" in result.errors
    
    def test_import_missing_file(self, rp):
        """Test importing missing file"""
        result = rp.import_rules("/nonexistent/path.json")
        
        assert result.success is False
    
    def test_list_exports(self, rp):
        """Test listing exports"""
        # Create export with distinct rules each time
        all_rules = []
        for i in range(3):
            rule = ExportedRule(
                rule_id=f"rule_{i:03d}",
                rule_type="behavior",
                condition="test",
                action="test",
            )
            all_rules.append(rule)
        
        # Export all rules together
        rp.export_rules(all_rules)
        
        exports = rp.list_exports()
        
        # Should have at least 1 export
        assert len(exports) >= 1
        assert exports[0]["rules_count"] == 3
    
    def test_get_rule_lineage(self, rp):
        """Test getting rule lineage"""
        lineage = RuleLineage(
            rule_id="rule_001",
            parent_rules=["rule_000"],
        )
        
        rp.save_rule_lineage(lineage)
        
        retrieved = rp.get_rule_lineage("rule_001")
        
        assert retrieved is not None
        assert retrieved.rule_id == "rule_001"
        assert "rule_000" in retrieved.parent_rules
    
    def test_get_missing_lineage(self, rp):
        """Test getting missing lineage"""
        lineage = rp.get_rule_lineage("nonexistent")
        
        assert lineage is None
    
    def test_save_rule_lineage(self, rp):
        """Test saving rule lineage"""
        lineage = RuleLineage(
            rule_id="rule_002",
            derived_from=["opd_001"],
        )
        
        result = rp.save_rule_lineage(lineage)
        
        assert result is True
    
    def test_export_import_roundtrip(self, rp):
        """Test export-import roundtrip"""
        # Create rules with full metadata
        rules = [
            ExportedRule(
                rule_id=f"rule_{i:03d}",
                rule_type="behavior",
                condition=f"condition_{i}",
                action=f"action_{i}",
                confidence=0.8 + i * 0.05,
                source="feedback",
                version=RuleVersion(
                    version="1.0.0",
                    created_at=datetime(2026, 4, 7, 12, 0, 0),
                    updated_at=datetime(2026, 4, 7, 13, 0, 0),
                ),
                lineage=RuleLineage(
                    rule_id=f"rule_{i:03d}",
                    parent_rules=[f"rule_{i-1:03d}"] if i > 0 else [],
                ),
                metadata={"index": i},
            )
            for i in range(5)
        ]
        
        # Export
        export_result = rp.export_rules(rules, include_lineage=True, include_metadata=True)
        assert export_result.success is True
        
        # Import
        import_result = rp.import_rules(export_result.path)
        assert import_result.success is True
        assert import_result.rules_imported == 5
        
        # Verify file contents
        with open(export_result.path, "r") as f:
            data = json.load(f)
        
        assert data["format_version"] == "2.0.0"
        assert data["rules_count"] == 5
        
        # Check first rule
        first_rule = data["rules"][0]
        assert first_rule["rule_id"] == "rule_000"
        assert "version" in first_rule
        assert "lineage" in first_rule
