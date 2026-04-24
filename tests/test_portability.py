#!/usr/bin/env python3
"""
Tests for Portability Module (Export/Import/Convert)
"""

import pytest
import json
import tempfile
from pathlib import Path
from claw_rl.portability import RuleExporter, RuleImporter, RuleConverter


class TestRuleExporter:
    """Test RuleExporter"""

    @pytest.fixture
    def sample_rule(self):
        """Sample rule for testing"""
        return {
            "rule_id": "test-rule-001",
            "rule_type": "behavioral",
            "condition": "When user says hello",
            "action": "Respond with greeting",
            "confidence": 0.9,
            "source": "feedback",
            "metadata": {"tag": "test"},
            "lineage": {
                "parent_rules": [],
                "derived_from": [],
                "feedback_sources": ["user-123"]
            }
        }

    def test_to_json(self, sample_rule):
        """Test export to JSON"""
        exporter = RuleExporter()
        result = exporter.to_json(sample_rule)

        assert isinstance(result, str)
        data = json.loads(result)
        assert data["rule_id"] == "test-rule-001"
        assert data["rule_type"] == "behavioral"

    def test_to_json_contains_metadata(self, sample_rule):
        """Test JSON export contains export metadata"""
        exporter = RuleExporter()
        result = exporter.to_json(sample_rule)

        data = json.loads(result)
        assert "_export_format_version" in data
        assert "_exported_at" in data

    def test_to_yaml(self, sample_rule):
        """Test export to YAML"""
        pytest.importorskip("yaml")
        exporter = RuleExporter()
        result = exporter.to_yaml(sample_rule)

        assert isinstance(result, str)
        assert "test-rule-001" in result

    def test_to_markdown(self, sample_rule):
        """Test export to Markdown"""
        exporter = RuleExporter()
        result = exporter.to_markdown(sample_rule)

        assert isinstance(result, str)
        assert "# Rule: test-rule-001" in result
        assert "## Condition" in result
        assert "## Action" in result
        assert "When user says hello" in result

    def test_to_markdown_metadata(self, sample_rule):
        """Test Markdown export includes metadata"""
        exporter = RuleExporter()
        result = exporter.to_markdown(sample_rule)

        assert "**Type**: behavioral" in result
        assert "**Confidence**: 0.90" in result

    def test_export_to_file_json(self, sample_rule):
        """Test export to JSON file"""
        exporter = RuleExporter()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "rule.json"
            exporter.export_to_file(sample_rule, path, format="json")

            assert path.exists()
            data = json.loads(path.read_text())
            assert data["rule_id"] == "test-rule-001"

    def test_export_to_file_markdown(self, sample_rule):
        """Test export to Markdown file"""
        exporter = RuleExporter()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "rule.md"
            exporter.export_to_file(sample_rule, path, format="markdown")

            assert path.exists()
            content = path.read_text()
            assert "# Rule: test-rule-001" in content

    def test_export_invalid_format(self, sample_rule):
        """Test export with invalid format"""
        exporter = RuleExporter()

        with pytest.raises(ValueError, match="Unsupported format"):
            exporter.export_to_file(sample_rule, Path("/tmp/test.txt"), format="invalid")


class TestRuleImporter:
    """Test RuleImporter"""

    @pytest.fixture
    def sample_rule(self):
        """Sample rule for testing"""
        return {
            "rule_id": "test-rule-001",
            "rule_type": "behavioral",
            "condition": "When user says hello",
            "action": "Respond with greeting",
            "confidence": 0.9,
        }

    def test_from_json(self, sample_rule):
        """Test import from JSON"""
        importer = RuleImporter()
        json_str = json.dumps(sample_rule)

        result = importer.from_json(json_str)

        assert result["rule_id"] == "test-rule-001"
        assert result["rule_type"] == "behavioral"

    def test_from_json_invalid(self):
        """Test import from invalid JSON"""
        importer = RuleImporter()

        with pytest.raises(ValueError, match="Invalid JSON"):
            importer.from_json("{invalid json}")

    def test_from_yaml(self, sample_rule):
        """Test import from YAML"""
        pytest.importorskip("yaml")
        importer = RuleImporter()
        yaml_str = f"""
rule_id: test-rule-001
rule_type: behavioral
condition: When user says hello
action: Respond with greeting
confidence: 0.9
"""

        result = importer.from_yaml(yaml_str)

        assert result["rule_id"] == "test-rule-001"

    def test_from_markdown(self):
        """Test import from Markdown"""
        importer = RuleImporter()
        md_str = """# Rule: test-rule-001

## Metadata
- **Type**: behavioral
- **Confidence**: 0.90

## Condition

When user says hello

## Action

Respond with greeting
"""

        result = importer.from_markdown(md_str)

        assert result["rule_id"] == "test-rule-001"
        assert result["rule_type"] == "behavioral"
        assert result["condition"] == "When user says hello"
        assert result["action"] == "Respond with greeting"

    def test_from_markdown_with_lineage(self):
        """Test import from Markdown with lineage"""
        importer = RuleImporter()
        md_str = """# Rule: test-rule-001

## Metadata
- **Type**: behavioral

## Condition

Test condition

## Action

Test action

## Lineage
- **Parent Rules**: rule-1, rule-2
"""

        result = importer.from_markdown(md_str)

        assert result["rule_id"] == "test-rule-001"
        assert "lineage" in result

    def test_import_from_file_json(self, sample_rule):
        """Test import from JSON file"""
        importer = RuleImporter()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "rule.json"
            path.write_text(json.dumps(sample_rule))

            result = importer.import_from_file(path)

            assert result["rule_id"] == "test-rule-001"

    def test_import_from_file_markdown(self):
        """Test import from Markdown file"""
        importer = RuleImporter()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "rule.md"
            path.write_text("# Rule: test-001\n\n## Condition\n\nTest\n\n## Action\n\nTest")

            result = importer.import_from_file(path)

            assert result["rule_id"] == "test-001"

    def test_import_multiple_from_file(self):
        """Test import multiple rules from JSON file"""
        importer = RuleImporter()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "rules.json"
            path.write_text(json.dumps([
                {"rule_id": "rule-1", "rule_type": "general"},
                {"rule_id": "rule-2", "rule_type": "behavioral"}
            ]))

            results = importer.import_multiple_from_file(path)

            assert len(results) == 2
            assert results[0]["rule_id"] == "rule-1"
            assert results[1]["rule_id"] == "rule-2"

    def test_clean_imported_rule(self):
        """Test that export metadata is cleaned"""
        importer = RuleImporter()
        rule = {
            "rule_id": "test",
            "_export_format_version": "2.2.0",
            "_exported_at": "2026-01-01",
        }

        result = importer._clean_imported_rule(rule)

        assert "_export_format_version" not in result
        assert "_exported_at" not in result
        assert result["rule_id"] == "test"


class TestRuleConverter:
    """Test RuleConverter"""

    def test_detect_version_v1(self):
        """Test version detection for v1.0"""
        converter = RuleConverter()

        rule_v1 = {"id": "rule-1", "type": "behavior", "content": "test"}
        assert converter.detect_version(rule_v1) == "1.0"

    def test_detect_version_v2(self):
        """Test version detection for v2.0"""
        converter = RuleConverter()

        rule_v2 = {"rule_id": "rule-1", "rule_type": "behavioral", "condition": "test", "action": "test"}
        assert converter.detect_version(rule_v2) == "2.0"

    def test_detect_version_v2_2(self):
        """Test version detection for v2.2"""
        converter = RuleConverter()

        rule_v2_2 = {"rule_id": "rule-1", "_export_format_version": "2.2.0"}
        assert converter.detect_version(rule_v2_2) == "2.2"

    def test_detect_version_unknown(self):
        """Test version detection for unknown format"""
        converter = RuleConverter()

        rule = {"data": "test"}
        assert converter.detect_version(rule) == "unknown"

    def test_convert_v1_to_v2(self):
        """Test conversion from v1 to v2"""
        converter = RuleConverter()

        rule_v1 = {
            "id": "old-rule-001",
            "type": "behavior",
            "condition": "When user greets",
            "content": "Say hello",
            "score": 0.8
        }

        result = converter.convert_v1_to_v2(rule_v1)

        assert result["rule_id"] == "old-rule-001"
        assert result["rule_type"] == "behavioral"
        assert result["condition"] == "When user greets"
        assert result["action"] == "Say hello"
        assert result["confidence"] == 0.8
        assert result["source"] == "migrated_from_v1"
        assert result["version"]["version"] == "2.2"

    def test_convert_v2_to_v2_2(self):
        """Test conversion from v2.0 to v2.2"""
        converter = RuleConverter()

        rule_v2 = {
            "rule_id": "rule-001",
            "rule_type": "behavioral",
            "condition": "Test",
            "action": "Test action",
            "version": {"version": "2.0"}
        }

        result = converter.convert_v2_to_v2_2(rule_v2)

        assert result["version"]["version"] == "2.2"
        assert "lineage" in result
        assert "metadata" in result

    def test_convert_same_version(self):
        """Test conversion with same version"""
        converter = RuleConverter()

        rule = {"rule_id": "test", "rule_type": "general"}
        result = converter.convert(rule, from_version="2.2", to_version="2.2")

        assert result["rule_id"] == "test"

    def test_convert_unsupported(self):
        """Test unsupported conversion"""
        converter = RuleConverter()

        with pytest.raises(ValueError, match="not supported"):
            converter.convert({"data": "test"}, from_version="1.0", to_version="3.0")

    def test_convert_batch(self):
        """Test batch conversion"""
        converter = RuleConverter()

        rules = [
            {"id": "r1", "type": "behavior", "content": "test1"},
            {"id": "r2", "type": "prompt", "content": "test2"},
        ]

        results = converter.convert_batch(rules, to_version="2.2")

        assert len(results) == 2
        assert all(r["version"]["version"] == "2.2" for r in results)

    def test_convert_type_mapping(self):
        """Test type mapping in v1 to v2 conversion"""
        converter = RuleConverter()

        assert converter._convert_type("behavior") == "behavioral"
        assert converter._convert_type("prompt") == "prompt"
        assert converter._convert_type("unknown") == "general"


class TestPortabilityIntegration:
    """Integration tests for portability module"""

    def test_export_import_roundtrip_json(self):
        """Test export and import with JSON"""
        original_rule = {
            "rule_id": "roundtrip-test",
            "rule_type": "behavioral",
            "condition": "Test condition",
            "action": "Test action",
            "confidence": 0.85,
        }

        exporter = RuleExporter()
        importer = RuleImporter()

        # Export to JSON
        json_str = exporter.to_json(original_rule)

        # Import back
        imported = importer.from_json(json_str)

        assert imported["rule_id"] == original_rule["rule_id"]
        assert imported["rule_type"] == original_rule["rule_type"]
        assert imported["condition"] == original_rule["condition"]
        assert imported["action"] == original_rule["action"]

    def test_version_migration_workflow(self):
        """Test full version migration workflow"""
        # Start with v1 rule
        v1_rule = {
            "id": "legacy-rule",
            "type": "pattern",
            "condition": "Old trigger",
            "content": "Old response",
            "score": 0.7
        }

        # Convert to v2.2
        converter = RuleConverter()
        v2_rule = converter.convert(v1_rule, to_version="2.2")

        # Export
        exporter = RuleExporter()
        json_str = exporter.to_json(v2_rule)

        # Import
        importer = RuleImporter()
        imported = importer.from_json(json_str)

        assert imported["rule_id"] == "legacy-rule"
        assert imported["version"]["version"] == "2.2"
        assert imported["source"] == "migrated_from_v1"

    def test_concurrent_format_operations(self):
        """Test operations with different formats"""
        rule = {
            "rule_id": "format-test",
            "rule_type": "general",
            "condition": "Test",
            "action": "Test action",
        }

        exporter = RuleExporter()
        importer = RuleImporter()

        # JSON
        json_result = exporter.to_json(rule)
        json_imported = importer.from_json(json_result)
        assert json_imported["rule_id"] == "format-test"

        # Markdown
        md_result = exporter.to_markdown(rule)
        md_imported = importer.from_markdown(md_result)
        assert md_imported["rule_id"] == "format-test"
