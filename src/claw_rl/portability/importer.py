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
Rule Importer - 规则导入器
"""

import json
import re
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class RuleImporter:
    """规则导入器 - 支持多种格式导入"""

    def from_json(self, json_str: str) -> Dict[str, Any]:
        """从 JSON 格式导入

        Args:
            json_str: JSON 格式的规则字符串

        Returns:
            Dict: 规则字典

        Raises:
            ValueError: JSON 解析错误
        """
        try:
            rule = json.loads(json_str)
            return self._clean_imported_rule(rule)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    def from_yaml(self, yaml_str: str) -> Dict[str, Any]:
        """从 YAML 格式导入

        Args:
            yaml_str: YAML 格式的规则字符串

        Returns:
            Dict: 规则字典

        Raises:
            ImportError: PyYAML 未安装
            ValueError: YAML 解析错误
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML is required for YAML import. Install with: pip install pyyaml")

        try:
            rule = yaml.safe_load(yaml_str)
            return self._clean_imported_rule(rule)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

    def from_markdown(self, md_str: str) -> Dict[str, Any]:
        """从 Markdown 格式导入

        Args:
            md_str: Markdown 格式的规则字符串

        Returns:
            Dict: 规则字典
        """
        rule: Dict[str, Any] = {}

        # Extract rule ID from title
        title_match = re.search(r'^#\s+Rule:\s*(.+)$', md_str, re.MULTILINE)
        if title_match:
            rule['rule_id'] = title_match.group(1).strip()

        # Extract metadata section
        metadata_pattern = r'\*\*(\w+)\*\*:\s*(.+?)(?=\n|$)'
        for match in re.finditer(metadata_pattern, md_str):
            key = match.group(1).strip().lower()
            value = match.group(2).strip()

            if key == "type":
                rule['rule_type'] = value
            elif key == "confidence":
                try:
                    rule['confidence'] = float(value)
                except ValueError:
                    rule['confidence'] = 0.0
            elif key == "source":
                rule['source'] = value
            elif key == "version":
                rule['version'] = {"version": value}
            elif key == "created":
                rule['created_at'] = value

        # Extract Condition section
        condition_match = re.search(
            r'^##\s+Condition\s*\n\n(.+?)(?=\n##|\Z)',
            md_str,
            re.DOTALL | re.MULTILINE
        )
        if condition_match:
            rule['condition'] = condition_match.group(1).strip()

        # Extract Action section
        action_match = re.search(
            r'^##\s+Action\s*\n\n(.+?)(?=\n##|\Z)',
            md_str,
            re.DOTALL | re.MULTILINE
        )
        if action_match:
            rule['action'] = action_match.group(1).strip()

        # Extract lineage if exists
        lineage: Dict[str, List[str]] = {}
        parent_match = re.search(r'\*\*Parent Rules\*\*:\s*(.+)', md_str)
        if parent_match:
            lineage['parent_rules'] = [r.strip() for r in parent_match.group(1).split(',')]

        derived_match = re.search(r'\*\*Derived From\*\*:\s*(.+)', md_str)
        if derived_match:
            lineage['derived_from'] = [r.strip() for r in derived_match.group(1).split(',')]

        if lineage:
            rule['lineage'] = lineage

        return rule

    def import_from_file(self, path: Path) -> Dict[str, Any]:
        """从文件导入规则

        Args:
            path: 规则文件路径

        Returns:
            Dict: 规则字典
        """
        content = path.read_text(encoding="utf-8")
        suffix = path.suffix.lower()

        if suffix == ".json":
            return self.from_json(content)
        elif suffix in (".yaml", ".yml"):
            return self.from_yaml(content)
        elif suffix == ".md":
            return self.from_markdown(content)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    def import_multiple_from_file(self, path: Path) -> List[Dict[str, Any]]:
        """从文件导入多个规则（JSON 数组格式）

        Args:
            path: 规则文件路径

        Returns:
            List[Dict]: 规则字典列表
        """
        content = path.read_text(encoding="utf-8")
        suffix = path.suffix.lower()

        if suffix == ".json":
            rules = json.loads(content)
            if not isinstance(rules, list):
                return [self._clean_imported_rule(rules)]
            return [self._clean_imported_rule(r) for r in rules]
        else:
            raise ValueError(f"Multiple import only supports JSON: {suffix}")

    def _clean_imported_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """清理导入的规则数据

        Args:
            rule: 导入的规则字典

        Returns:
            Dict: 清理后的规则
        """
        # Remove export metadata
        cleaned = {k: v for k, v in rule.items() if not k.startswith('_')}
        return cleaned


__all__ = ["RuleImporter"]
