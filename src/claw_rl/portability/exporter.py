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
Rule Exporter - 规thenexport器
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class RuleExporter:
    """规thenexport器 - 支持多种formatexport"""

    def __init__(self):
        self.export_format_version = "2.2.0"

    def to_json(self, rule: Dict[str, Any]) -> str:
        """export为 JSON format

        Args:
            rule: 规thendict

        Returns:
            str: JSON format的规then
        """
        export_data = self._prepare_rule_for_export(rule)
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def to_yaml(self, rule: Dict[str, Any]) -> str:
        """export为 YAML format

        Args:
            rule: 规thendict

        Returns:
            str: YAML format的规then
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML export. Install with: pip install pyyaml")

        export_data = self._prepare_rule_for_export(rule)
        return yaml.dump(export_data, allow_unicode=True, default_flow_style=False)

    def to_markdown(self, rule: Dict[str, Any]) -> str:
        """export为 Markdown 文档format

        Args:
            rule: 规thendict

        Returns:
            str: Markdown format的规then文档
        """
        export_data = self._prepare_rule_for_export(rule)

        md_lines = [
            f"# Rule: {export_data.get('rule_id', 'Unknown')}",
            "",
            "## Metadata",
            f"- **Type**: {export_data.get('rule_type', 'unknown')}",
            f"- **Confidence**: {export_data.get('confidence', 0.0):.2f}",
            f"- **Source**: {export_data.get('source', 'unknown')}",
            f"- **Version**: {export_data.get('version', {}).get('version', 'N/A')}",
            f"- **Created**: {export_data.get('created_at', 'N/A')}",
            "",
            "## Condition",
            "",
            export_data.get('condition', 'No condition defined'),
            "",
            "## Action",
            "",
            export_data.get('action', 'No action defined'),
            "",
        ]

        # Add metadata if exists
        if export_data.get('metadata'):
            md_lines.extend([
                "## Metadata",
                ""
            ])
            for key, value in export_data['metadata'].items():
                md_lines.append(f"- **{key}**: {value}")
            md_lines.append("")

        # Add lineage if exists
        if export_data.get('lineage'):
            lineage = export_data['lineage']
            md_lines.extend([
                "## Lineage",
                ""
            ])
            if lineage.get('parent_rules'):
                md_lines.append(f"- **Parent Rules**: {', '.join(lineage['parent_rules'])}")
            if lineage.get('derived_from'):
                md_lines.append(f"- **Derived From**: {', '.join(lineage['derived_from'])}")
            md_lines.append("")

        return "\n".join(md_lines)

    def export_to_file(self, rule: Dict[str, Any], path: Path, format: str = "json") -> None:
        """export规then到file

        Args:
            rule: 规thendict
            path: objectivefilepath
            format: exportformat (json/yaml/markdown)
        """
        if format == "json":
            content = self.to_json(rule)
        elif format == "yaml":
            content = self.to_yaml(rule)
        elif format == "markdown":
            content = self.to_markdown(rule)
        else:
            raise ValueError(f"Unsupported format: {format}")

        path.write_text(content, encoding="utf-8")

    def _prepare_rule_for_export(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """准备规thendata用于export

        Args:
            rule: 原始规thendict

        Returns:
            Dict: add了export元data的规then
        """
        export_data = {
            **rule,
            "_export_format_version": self.export_format_version,
            "_exported_at": datetime.now(timezone.utc).isoformat(),
        }
        return export_data


__all__ = ["RuleExporter"]
