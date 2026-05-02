# Copyright 2026 Peter Cheng
#
# Licensed under the Apache License, Version 2.0 (the "License");
"""Tests for portability/converter.py and portability/exporter.py"""

import json
import pytest
from pathlib import Path
from claw_rl.portability.converter import RuleConverter
from claw_rl.portability.exporter import RuleExporter


class TestRuleConverter:
    def test_detect_version_v1_0_marker(self):
        rc = RuleConverter()
        v = rc.detect_version({"_rule_version": "1.0"})
        assert v == "1.0"

    def test_detect_version_v1_0_string(self):
        rc = RuleConverter()
        v = rc.detect_version({"version": "1.0"})
        assert v == "1.0"

    def test_detect_version_v2_2(self):
        rc = RuleConverter()
        v = rc.detect_version({"_export_format_version": "2.2"})
        assert v == "2.2"

    def test_detect_version_v2_1(self):
        rc = RuleConverter()
        v = rc.detect_version({"_export_format_version": "2.1.0"})
        assert v == "2.1"

    def test_detect_version_v2_0(self):
        rc = RuleConverter()
        v = rc.detect_version({"_export_format_version": "2.0.0"})
        assert v == "2.0"

    def test_detect_version_v2_unknown_prefix(self):
        rc = RuleConverter()
        v = rc.detect_version({})
        assert v == "unknown"

    def test_detect_version_structure_v1(self):
        rc = RuleConverter()
        v = rc.detect_version({"type": "general", "content": "do something"})
        assert v == "1.0"

    def test_detect_version_structure_v2(self):
        rc = RuleConverter()
        v = rc.detect_version({"rule_type": "general", "condition": "x > 0"})
        assert v == "2.0"

    def test_convert_v1_to_v2_basic(self):
        rc = RuleConverter()
        v1 = {
            "id": "rule_0001",
            "type": "behavior",
            "condition": "print",
            "content": "use logging",
            "score": 0.85,
        }
        v2 = rc.convert_v1_to_v2(v1)
        assert v2["rule_id"] == "rule_0001"
        assert v2["rule_type"] == "behavioral"
        assert v2["condition"] == "print"
        assert v2["action"] == "use logging"
        assert v2["confidence"] == 0.85
        assert v2["source"] == "migrated_from_v1"
        assert "version" in v2
        assert v2["version"]["version"] == "2.2"
        assert "lineage" in v2
        assert "metadata" in v2

    def test_convert_v1_to_v2_minimal(self):
        rc = RuleConverter()
        v1 = {}
        v2 = rc.convert_v1_to_v2(v1)
        assert "rule_id" in v2
        assert v2["rule_type"] == "general"
        assert v2["confidence"] == 0.5

    def test_convert_v1_to_v2_alternate_fields(self):
        rc = RuleConverter()
        v1 = {
            "rule_id": "r1",
            "trigger": "error",
            "response": "fix error",
            "confidence": 0.9,
        }
        v2 = rc.convert_v1_to_v2(v1)
        assert v2["rule_id"] == "r1"
        assert v2["condition"] == "error"
        assert v2["action"] == "fix error"
        assert v2["confidence"] == 0.9

    def test_convert_v2_to_v2_2_with_version_dict(self):
        rc = RuleConverter()
        v2 = {
            "rule_id": "r1",
            "version": {"version": "2.0", "created_at": "2024-01-01"},
        }
        result = rc.convert_v2_to_v2_2(v2)
        assert result["version"]["version"] == "2.2"
        assert "updated_at" in result["version"]
        assert "lineage" in result
        assert "metadata" in result

    def test_convert_v2_to_v2_2_without_version_dict(self):
        rc = RuleConverter()
        v2 = {"rule_id": "r1"}
        result = rc.convert_v2_to_v2_2(v2)
        assert result["version"]["version"] == "2.2"
        assert result["metadata"]["upgraded_to"] == "2.2"

    def test_convert_v2_to_v2_2_preserves_existing(self):
        rc = RuleConverter()
        v2 = {
            "rule_id": "r1",
            "lineage": {"parent_rules": ["p1"]},
            "metadata": {"key": "val"},
        }
        result = rc.convert_v2_to_v2_2(v2)
        assert result["lineage"]["parent_rules"] == ["p1"]
        assert result["metadata"]["key"] == "val"

    def test_convert_same_version(self):
        rc = RuleConverter()
        rule = {"rule_id": "r1", "version": "2.2"}
        result = rc.convert(rule, from_version="2.2", to_version="2.2")
        assert result is rule

    def test_convert_v1_to_v2_2(self):
        rc = RuleConverter()
        v1 = {"id": "rule_0001", "type": "general", "content": "action"}
        result = rc.convert(v1, from_version="1.0", to_version="2.2")
        assert result["source"] == "migrated_from_v1"

    def test_convert_v2_0_to_v2_2(self):
        rc = RuleConverter()
        v2 = {"rule_id": "r1"}
        result = rc.convert(v2, from_version="2.0", to_version="2.2")
        assert result["version"]["version"] == "2.2"

    def test_convert_v2_1_to_v2_2(self):
        rc = RuleConverter()
        v2 = {"rule_id": "r1"}
        result = rc.convert(v2, from_version="2.1", to_version="2.2")
        assert result["version"]["version"] == "2.2"

    def test_convert_unsupported(self):
        rc = RuleConverter()
        with pytest.raises(ValueError, match="not supported"):
            rc.convert({}, from_version="3.0", to_version="4.0")

    def test_convert_auto_detect(self):
        rc = RuleConverter()
        v1 = {"type": "general", "content": "test"}
        result = rc.convert(v1, to_version="2.2")
        assert result["source"] == "migrated_from_v1"

    def test_convert_batch(self):
        rc = RuleConverter()
        rules = [
            {"id": "r1", "type": "general", "content": "a1"},
            {"id": "r2", "type": "general", "content": "a2"},
        ]
        results = rc.convert_batch(rules, to_version="2.2")
        assert len(results) == 2
        assert results[0]["source"] == "migrated_from_v1"

    def test_convert_type_mapping(self):
        rc = RuleConverter()
        assert rc._convert_type("behavior") == "behavioral"
        assert rc._convert_type("prompt") == "prompt"
        assert rc._convert_type("response") == "response"
        assert rc._convert_type("general") == "general"
        assert rc._convert_type("pattern") == "behavioral"
        assert rc._convert_type("unknown_type") == "general"
        assert rc._convert_type("GENeral") == "general"

    def test_generate_id(self):
        rc = RuleConverter()
        rid = rc._generate_id()
        assert rid.startswith("migrated_")
        assert len(rid) > 9


class TestRuleExporter:
    def test_to_json_basic(self):
        rexp = RuleExporter()
        rule = {"rule_id": "r1", "rule_type": "general"}
        result = rexp.to_json(rule)
        data = json.loads(result)
        assert data["rule_id"] == "r1"
        assert "_export_format_version" in data
        assert "_exported_at" in data

    def test_to_markdown_basic(self):
        rexp = RuleExporter()
        rule = {
            "rule_id": "r1",
            "rule_type": "warning",
            "confidence": 0.75,
            "source": "test",
            "condition": "x > 0",
            "action": "notify user",
            "created_at": "2024-01-01",
        }
        result = rexp.to_markdown(rule)
        assert "# Rule: r1" in result
        assert "warning" in result
        assert "0.75" in result
        assert "x > 0" in result
        assert "notify user" in result

    def test_to_markdown_with_metadata(self):
        rexp = RuleExporter()
        rule = {
            "rule_id": "r1",
            "rule_type": "general",
            "confidence": 1.0,
            "source": "test",
            "condition": "test",
            "action": "test",
            "metadata": {"author": "Peter"},
        }
        result = rexp.to_markdown(rule)
        assert "author" in result

    def test_to_markdown_with_lineage(self):
        rexp = RuleExporter()
        rule = {
            "rule_id": "r1",
            "rule_type": "general",
            "confidence": 1.0,
            "source": "test",
            "condition": "test",
            "action": "test",
            "lineage": {
                "parent_rules": ["p1", "p2"],
                "derived_from": ["d1"],
            },
        }
        result = rexp.to_markdown(rule)
        assert "p1" in result
        assert "d1" in result

    def test_to_markdown_minimal(self):
        rexp = RuleExporter()
        rule = {}
        result = rexp.to_markdown(rule)
        assert "# Rule: Unknown" in result

    def test_to_markdown_no_metadata_no_lineage(self):
        rexp = RuleExporter()
        rule = {"rule_id": "r1", "rule_type": "test", "confidence": 0.5,
                "source": "test", "condition": "x", "action": "y"}
        result = rexp.to_markdown(rule)
        assert "# Rule: r1" in result
        # Metadata section should NOT appear when empty
        assert "## Metadata\n\n- **author**" not in result.replace("## Metadata\n\n", "").replace("**Type**", "").strip()

    def test_export_to_file_json(self, tmp_path):
        rexp = RuleExporter()
        rule = {"rule_id": "r1"}
        path = tmp_path / "rule.json"
        rexp.export_to_file(rule, path, format="json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["rule_id"] == "r1"

    def test_export_to_file_markdown(self, tmp_path):
        rexp = RuleExporter()
        rule = {"rule_id": "r1", "rule_type": "test", "confidence": 1.0,
                "source": "test", "condition": "x", "action": "y"}
        path = tmp_path / "rule.md"
        rexp.export_to_file(rule, path, format="markdown")
        assert path.exists()
        content = path.read_text()
        assert "# Rule: r1" in content

    def test_export_to_file_unsupported_format(self, tmp_path):
        rexp = RuleExporter()
        with pytest.raises(ValueError, match="Unsupported format"):
            rexp.export_to_file({}, tmp_path / "rule.xml", format="xml")

    def test_to_yaml_not_available(self):
        rexp = RuleExporter()
        # PyYAML may or may not be installed
        try:
            import yaml  # noqa
            yaml_available = True
        except ImportError:
            yaml_available = False

        if not yaml_available:
            with pytest.raises(ImportError):
                rexp.to_yaml({"rule_id": "r1"})
        else:
            result = rexp.to_yaml({"rule_id": "r1"})
            assert "r1" in result

    def test_prepare_rule_for_export(self):
        rexp = RuleExporter()
        rule = {"rule_id": "r1", "custom": "value"}
        result = rexp._prepare_rule_for_export(rule)
        assert result["rule_id"] == "r1"
        assert result["custom"] == "value"
        assert result["_export_format_version"] == "2.2.0"
        assert "_exported_at" in result
