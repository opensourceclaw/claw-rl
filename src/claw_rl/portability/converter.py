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
Rule Converter - 规thenformatconvert器
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional


class RuleConverter:
    """规thenformatconvert器 - 支持版本迁移"""

    # 版本标识
    VERSION_PATTERNS = {
        "1.0": ["_rule_version", "v1"],
        "2.0": ["_export_format_version", "2.0"],
        "2.1": ["_export_format_version", "2.1"],
        "2.2": ["_export_format_version", "2.2"],
    }

    def detect_version(self, rule: Dict[str, Any]) -> str:
        """自动检测规then版本

        Args:
            rule: 规thendict

        Returns:
            str: 版本号 (1.0, 2.0, 2.1, 2.2) 或 "unknown"
        """
        # Check for v1.0 markers
        if "_rule_version" in rule:
            return "1.0"

        # Check if version field is a string "1.0"
        version_val = rule.get("version")
        if isinstance(version_val, str) and version_val == "1.0":
            return "1.0"

        # Check for v2.x markers
        export_version = rule.get("_export_format_version", "")
        if export_version.startswith("2.2"):
            return "2.2"
        elif export_version.startswith("2.1"):
            return "2.1"
        elif export_version.startswith("2."):
            return "2.0"

        # Try to infer from structure
        if "rule_type" in rule and "condition" in rule:
            return "2.0"

        if "type" in rule and "content" in rule:
            return "1.0"

        return "unknown"

    def convert_v1_to_v2(self, rule_v1: Dict[str, Any]) -> Dict[str, Any]:
        """将 v1.0 format迁移到 v2.2

        Args:
            rule_v1: v1.0 format的规then

        Returns:
            Dict: v2.2 format的规then
        """
        rule_v2: Dict[str, Any] = {}

        # Map v1 fields to v2 fields
        rule_v2['rule_id'] = rule_v1.get('id') or rule_v1.get('rule_id') or self._generate_id()
        rule_v2['rule_type'] = self._convert_type(rule_v1.get('type', 'general'))
        rule_v2['condition'] = rule_v1.get('condition') or rule_v1.get('trigger') or ""
        rule_v2['action'] = rule_v1.get('content') or rule_v1.get('action') or rule_v1.get('response', '')
        rule_v2['confidence'] = rule_v1.get('score', rule_v1.get('confidence', 0.5))
        rule_v2['source'] = 'migrated_from_v1'

        # Handle metadata
        rule_v2['metadata'] = {
            'original_id': rule_v1.get('id'),
            'migrated_at': datetime.now(timezone.utc).isoformat(),
            'original_fields': {k: v for k, v in rule_v1.items()
                               if k not in ['id', 'type', 'condition', 'content', 'trigger', 'response', 'score', 'confidence']}
        }

        # Add version info
        rule_v2['version'] = {
            'version': '2.2',
            'migrated_from': '1.0',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }

        # Add lineage
        rule_v2['lineage'] = {
            'parent_rules': [],
            'derived_from': [rule_v1.get('id', 'unknown')],
            'feedback_sources': []
        }

        return rule_v2

    def convert_v2_to_v2_2(self, rule_v2: Dict[str, Any]) -> Dict[str, Any]:
        """将 v2.0/v2.1 format升级到 v2.2

        Args:
            rule_v2: v2.0 或 v2.1 format的规then

        Returns:
            Dict: v2.2 format的规then
        """
        rule_v2_2 = {**rule_v2}

        # Update version info
        if 'version' in rule_v2_2 and isinstance(rule_v2_2['version'], dict):
            rule_v2_2['version'] = {
                **rule_v2_2['version'],
                'version': '2.2',
                'updated_at': datetime.now(timezone.utc).isoformat(),
            }
        else:
            rule_v2_2['version'] = {
                'version': '2.2',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
            }

        # Ensure lineage exists
        if 'lineage' not in rule_v2_2:
            rule_v2_2['lineage'] = {
                'parent_rules': [],
                'derived_from': [],
                'feedback_sources': []
            }

        # Ensure metadata exists
        if 'metadata' not in rule_v2_2:
            rule_v2_2['metadata'] = {}

        rule_v2_2['metadata']['upgraded_to'] = '2.2'
        rule_v2_2['metadata']['upgraded_at'] = datetime.now(timezone.utc).isoformat()

        return rule_v2_2

    def convert(self, rule: Dict[str, Any], from_version: Optional[str] = None, to_version: str = "2.2") -> Dict[str, Any]:
        """通用convertmethod

        Args:
            rule: 规thendict
            from_version: 源版本 (None 表示自动检测)
            to_version: objective版本

        Returns:
            Dict: convert后的规then
        """
        if from_version is None:
            from_version = self.detect_version(rule)

        if from_version == to_version:
            return rule

        if from_version == "1.0" and to_version == "2.2":
            return self.convert_v1_to_v2(rule)

        if from_version in ("2.0", "2.1") and to_version == "2.2":
            return self.convert_v2_to_v2_2(rule)

        raise ValueError(f"Conversion from {from_version} to {to_version} is not supported")

    def convert_batch(self, rules: list[Dict[str, Any]], to_version: str = "2.2") -> list[Dict[str, Any]]:
        """批量convert规then

        Args:
            rules: 规thenlist
            to_version: objective版本

        Returns:
            List[Dict]: convert后的规thenlist
        """
        return [self.convert(rule, to_version=to_version) for rule in rules]

    def _convert_type(self, v1_type: str) -> str:
        """convertclass型标识

        Args:
            v1_type: v1 class型

        Returns:
            str: v2 class型
        """
        type_mapping = {
            'behavior': 'behavioral',
            'prompt': 'prompt',
            'response': 'response',
            'general': 'general',
            'pattern': 'behavioral',
        }
        return type_mapping.get(v1_type.lower(), 'general')

    def _generate_id(self) -> str:
        """生成规then ID"""
        import uuid
        return f"migrated_{uuid.uuid4().hex[:8]}"


__all__ = ["RuleConverter"]
