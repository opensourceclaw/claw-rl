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
Rule Exporter - 规则导出器
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
    """规则导出器 - 支持多种格式导出"""

    def __init__(self):
        self.export_format_version = "2.2.0"

    def to_json(self, rule: Dict[str, Any]) -> str:
        """导出为 JSON 格式

        Args:
            rule: 规则字典

        Returns:
            str: JSON 格式的规则
        """
        export_data = self._prepare_rule_for_export(rule)
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    def to_yaml(self, rule: Dict[str, Any]) -> str:
        """导出为 YAML 格式

        Args:
            rule: 规则字典

        Returns:
            str: YAML 格式的规则
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML export. Install with: pip install pyyaml")

        export_data = self._prepare_rule_for_export(rule)
        return yaml.dump(export_data, allow_unicode=True, default_flow_style=False)

    def to_markdown(self, rule: Dict[str, Any]) -> str:
        """导出为 Markdown 文档格式

        Args:
            rule: 规则字典

        Returns:
            str: Markdown 格式的规则文档
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
        """导出规则到文件

        Args:
            rule: 规则字典
            path: 目标文件路径
            format: 导出格式 (json/yaml/markdown)
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
        """准备规则数据用于导出

        Args:
            rule: 原始规则字典

        Returns:
            Dict: 添加了导出元数据的规则
        """
        export_data = {
            **rule,
            "_export_format_version": self.export_format_version,
            "_exported_at": datetime.now(timezone.utc).isoformat(),
        }
        return export_data


__all__ = ["RuleExporter"]
