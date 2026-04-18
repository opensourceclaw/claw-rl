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
Rule Portability v2.0 (Enhanced)

Enhanced export/import capabilities with:
- Multiple format support (JSON, YAML, Markdown)
- Rule validation and migration
- Backward compatibility
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json
import logging

# Import from base module
from .rule_portability import (
    RulePortability,
    ExportedRule,
    RuleVersion,
    RuleLineage,
    RuleMergeStrategy,
    RuleExportResult,
    RuleImportResult,
)

logger = logging.getLogger(__name__)


class RulePortabilityV2(RulePortability):
    """
    Enhanced Rule Portability (v2.1.0)
    
    Adds:
    - YAML export format
    - Markdown export format
    - Rule validation
    - Format migration
    """
    
    EXPORT_FORMAT_VERSION = "2.1.0"
    
    def export_rules(
        self,
        rules: List[Any],
        output_path: Optional[str] = None,
        include_lineage: bool = True,
        include_metadata: bool = True,
        format: str = "json",
    ) -> RuleExportResult:
        """
        Export rules to specified format.
        
        Args:
            rules: List of rules to export
            output_path: Optional output file path
            include_lineage: Include lineage information
            include_metadata: Include metadata
            format: Export format (json, yaml, markdown)
            
        Returns:
            RuleExportResult with export details
        """
        if format == "markdown":
            return self._export_markdown(rules, output_path, include_lineage, include_metadata)
        elif format == "yaml":
            return self._export_yaml(rules, output_path, include_lineage, include_metadata)
        else:
            return super().export_rules(rules, output_path, include_lineage, include_metadata)
    
    def _export_markdown(
        self,
        rules: List[Any],
        output_path: Optional[str],
        include_lineage: bool,
        include_metadata: bool,
    ) -> RuleExportResult:
        """Export rules as Markdown documentation"""
        if not rules:
            return RuleExportResult(
                success=True,
                rules_exported=0,
                errors=["No rules to export"],
            )
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.exports_dir / f"rules_export_{timestamp}.md")
        
        try:
            lines = [
                "# claw-rl Rules Export",
                "",
                f"**Exported:** {datetime.now().isoformat()}",
                f"**Rules Count:** {len(rules)}",
                f"**Format Version:** {self.EXPORT_FORMAT_VERSION}",
                "",
                "---",
                "",
            ]
            
            for i, rule in enumerate(rules, 1):
                exported = self._convert_rule(rule, include_lineage, include_metadata)
                
                lines.append(f"## Rule {i}: `{exported.rule_id}`")
                lines.append("")
                lines.append(f"**Type:** {exported.rule_type}")
                lines.append(f"**Confidence:** {exported.confidence:.2%}")
                lines.append(f"**Source:** {exported.source}")
                lines.append("")
                lines.append("### Condition")
                lines.append("")
                lines.append(f"```\n{exported.condition}\n```")
                lines.append("")
                lines.append("### Action")
                lines.append("")
                lines.append(f"```\n{exported.action}\n```")
                lines.append("")
                
                if include_lineage and exported.lineage:
                    lines.append("### Lineage")
                    lines.append("")
                    if exported.lineage.parent_rules:
                        lines.append(f"**Parents:** {', '.join(exported.lineage.parent_rules)}")
                    if exported.lineage.feedback_sources:
                        lines.append(f"**Sources:** {', '.join(exported.lineage.feedback_sources)}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
            
            content = "\n".join(lines)
            Path(output_path).write_text(content, encoding="utf-8")
            
            size_bytes = Path(output_path).stat().st_size
            
            return RuleExportResult(
                success=True,
                path=output_path,
                rules_exported=len(rules),
                format="markdown",
                size_bytes=size_bytes,
            )
            
        except Exception as e:
            logger.error(f"Markdown export failed: {e}")
            return RuleExportResult(
                success=False,
                errors=[str(e)],
            )
    
    def _export_yaml(
        self,
        rules: List[Any],
        output_path: Optional[str],
        include_lineage: bool,
        include_metadata: bool,
    ) -> RuleExportResult:
        """Export rules as YAML"""
        if not rules:
            return RuleExportResult(
                success=True,
                rules_exported=0,
                errors=["No rules to export"],
            )
        
        try:
            import yaml
        except ImportError:
            return RuleExportResult(
                success=False,
                errors=["PyYAML not installed. Run: pip install pyyaml"],
            )
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.exports_dir / f"rules_export_{timestamp}.yaml")
        
        try:
            exported_rules = []
            for rule in rules:
                exported = self._convert_rule(rule, include_lineage, include_metadata)
                exported_rules.append(exported.to_dict())
            
            export_data = {
                "format_version": self.EXPORT_FORMAT_VERSION,
                "exported_at": datetime.now().isoformat(),
                "source": "claw-rl",
                "rules_count": len(exported_rules),
                "rules": exported_rules,
            }
            
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
            
            size_bytes = Path(output_path).stat().st_size
            
            return RuleExportResult(
                success=True,
                path=output_path,
                rules_exported=len(rules),
                format="yaml",
                size_bytes=size_bytes,
            )
            
        except Exception as e:
            logger.error(f"YAML export failed: {e}")
            return RuleExportResult(
                success=False,
                errors=[str(e)],
            )
    
    def validate_rules(self, rules: List[ExportedRule]) -> Dict[str, List[str]]:
        """
        Validate imported rules.
        
        Args:
            rules: Rules to validate
            
        Returns:
            Dictionary of rule_id -> list of validation errors
        """
        errors = {}
        
        for rule in rules:
            rule_errors = []
            
            # Check required fields
            if not rule.rule_id:
                rule_errors.append("Missing rule_id")
            if not rule.rule_type:
                rule_errors.append("Missing rule_type")
            if not rule.condition:
                rule_errors.append("Missing condition")
            
            # Check confidence range
            if not (0 <= rule.confidence <= 1):
                rule_errors.append(f"Invalid confidence: {rule.confidence}")
            
            if rule_errors:
                errors[rule.rule_id or "unknown"] = rule_errors
        
        return errors
    
    def migrate_format(self, data: Dict, from_version: str) -> Dict:
        """
        Migrate import data from older format version.
        
        Args:
            data: Import data
            from_version: Source format version
            
        Returns:
            Migrated data
        """
        if from_version == self.EXPORT_FORMAT_VERSION:
            return data
        
        # Migration from v1.0.0
        if from_version.startswith("1."):
            if "rules" in data:
                for rule in data["rules"]:
                    # Add missing fields
                    if "lineage" not in rule:
                        rule["lineage"] = {
                            "rule_id": rule["rule_id"],
                            "parent_rules": [],
                            "derived_from": [],
                            "feedback_sources": [],
                        }
                    if "version" not in rule:
                        rule["version"] = {
                            "version": "1.0.0",
                            "created_at": data.get("exported_at", datetime.now().isoformat()),
                            "updated_at": datetime.now().isoformat(),
                            "author": "migration",
                            "changes": ["Migrated from v1.0.0"],
                        }
            
            data["format_version"] = self.EXPORT_FORMAT_VERSION
        
        return data
    
    def get_rule_diff(self, rule1: ExportedRule, rule2: ExportedRule) -> Dict[str, Any]:
        """
        Compare two rules and return differences.
        
        Args:
            rule1: First rule
            rule2: Second rule
            
        Returns:
            Dictionary of differences
        """
        diff = {
            "rule_id": rule1.rule_id,
            "differences": [],
        }
        
        if rule1.condition != rule2.condition:
            diff["differences"].append({
                "field": "condition",
                "before": rule1.condition,
                "after": rule2.condition,
            })
        
        if rule1.action != rule2.action:
            diff["differences"].append({
                "field": "action",
                "before": rule1.action,
                "after": rule2.action,
            })
        
        if rule1.confidence != rule2.confidence:
            diff["differences"].append({
                "field": "confidence",
                "before": rule1.confidence,
                "after": rule2.confidence,
            })
        
        return diff


def export_rules_to_markdown(rules: List[Any], output_path: Optional[str] = None) -> str:
    """
    Convenience function to export rules as Markdown.
    
    Args:
        rules: Rules to export
        output_path: Optional output path
        
    Returns:
        Markdown content
    """
    from pathlib import Path
    import tempfile
    
    if output_path is None:
        output_path = str(Path(tempfile.gettempdir()) / "rules_export.md")
    
    portability = RulePortabilityV2(Path(tempfile.gettempdir()))
    result = portability.export_rules(rules, output_path, format="markdown")
    
    if result.success:
        return Path(output_path).read_text()
    else:
        return f"# Export Failed\n\nErrors: {result.errors}"
