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
Rule Store - 规then存储
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


class RuleStore:
    """规then存储 - 本地 JSON file存储"""

    def __init__(self, storage_path: str = None):
        """initialize规then存储

        Args:
            storage_path: 存储path,default ~/.claw_rl/rules.json
        """
        if storage_path is None:
            home = Path.home()
            storage_path = home / '.claw_rl' / 'rules.json'

        self.storage_path = Path(storage_path)
        self._rules: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """从fileload规then"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._rules = data.get('rules', {})
            except (json.JSONDecodeError, IOError):
                self._rules = {}

    def _save(self) -> None:
        """save规then到file"""
        # 确保directory存在
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # savedata
        data = {
            'version': '1.0',
            'rules': self._rules,
            'updated_at': self._get_timestamp()
        }

        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_rule(self, rule: Dict[str, Any]) -> bool:
        """save规then

        Args:
            rule: 规thendict

        Returns:
            bool: 是否savesuccess
        """
        rule_id = rule.get('id')
        if not rule_id:
            return False

        self._rules[rule_id] = rule
        self._save()
        return True

    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """get规then

        Args:
            rule_id: 规thenID

        Returns:
            Optional[Dict]: 规then,ifnot存在returnNone
        """
        return self._rules.get(rule_id)

    def list_rules(
        self,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """列出规then

        Args:
            filters: filtercondition (type, severity, version)

        Returns:
            List[Dict]: 规thenlist
        """
        rules = list(self._rules.values())

        if not filters:
            return rules

        # 应用filtercondition
        filtered = []
        for rule in rules:
            match = True

            if 'type' in filters and rule.get('type') != filters['type']:
                match = False

            if 'severity' in filters and rule.get('severity') != filters['severity']:
                match = True

            if 'version' in filters and rule.get('version') != filters['version']:
                match = False

            if match:
                filtered.append(rule)

        return filtered

    def delete_rule(self, rule_id: str) -> bool:
        """delete规then

        Args:
            rule_id: 规thenID

        Returns:
            bool: 是否deletesuccess
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
            self._save()
            return True
        return False

    def count_rules(self) -> int:
        """get规thencount

        Returns:
            int: 规thencount
        """
        return len(self._rules)

    def clear(self) -> None:
        """清空所有规then"""
        self._rules = {}
        self._save()

    def get_statistics(self) -> Dict[str, Any]:
        """get规thenstatisticsinfo

        Returns:
            Dict: statisticsinfo
        """
        stats = {
            'total': len(self._rules),
            'by_type': {},
            'by_severity': {},
            'by_version': {}
        }

        for rule in self._rules.values():
            # 按class型statistics
            rule_type = rule.get('type', 'unknown')
            stats['by_type'][rule_type] = stats['by_type'].get(rule_type, 0) + 1

            # 按严重程degreestatistics
            severity = rule.get('severity', 'unknown')
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1

            # 按版本statistics
            version = rule.get('version', 'unknown')
            stats['by_version'][version] = stats['by_version'].get(version, 0) + 1

        return stats

    @staticmethod
    def _get_timestamp() -> str:
        """getwhen前间戳

        Returns:
            str: ISO format间戳
        """
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


__all__ = [
    'RuleStore',
]
