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
Rule Versioner - 规then版本化管理
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class RuleVersioner:
    """规then版本管理器 - create/查询/回滚规then版本"""

    def __init__(self):
        # 存储规then版本历史: {rule_id: [versions]}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}

    def create_version(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """create新版本

        Args:
            rule: 规thendict

        Returns:
            Dict: 带有版本info的规then
        """
        rule_id = rule.get('id')
        if not rule_id:
            raise ValueError("Rule must have an ID")

        # getwhen前版本号
        current_version = self._get_current_version(rule_id)
        new_version = f"{float(current_version) + 0.1:.1f}"

        # create版本记录
        version_record = {
            **rule,
            'version': new_version,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_current': True
        }

        # update历史
        if rule_id not in self._versions:
            self._versions[rule_id] = []

        # 将之前的版本标记为非when前
        for v in self._versions[rule_id]:
            v['is_current'] = False

        # add新版本
        self._versions[rule_id].append(version_record)

        return version_record

    def get_history(self, rule_id: str) -> List[Dict[str, Any]]:
        """get规then历史版本

        Args:
            rule_id: 规thenID

        Returns:
            List[Dict]: 版本历史list
        """
        return self._versions.get(rule_id, [])

    def get_version(self, rule_id: str, version: str) -> Optional[Dict[str, Any]]:
        """get指定版本

        Args:
            rule_id: 规thenID
            version: 版本号

        Returns:
            Optional[Dict]: 规then版本，ifnot存在returnNone
        """
        versions = self._versions.get(rule_id, [])
        for v in versions:
            if v.get('version') == version:
                return v
        return None

    def rollback(self, rule_id: str, version: str) -> Optional[Dict[str, Any]]:
        """回滚到指定版本

        Args:
            rule_id: 规thenID
            version: objective版本号

        Returns:
            Optional[Dict]: 回滚后的规then，ifnot存在returnNone
        """
        target_version = self.get_version(rule_id, version)
        if not target_version:
            return None

        # create新版本（not回滚原版本，保留历史）
        new_rule = {
            **target_version,
            'version': self._get_next_version(rule_id),
            'rolled_back_from': version,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_current': True
        }

        # update历史
        for v in self._versions[rule_id]:
            v['is_current'] = False

        self._versions[rule_id].append(new_rule)

        return new_rule

    def get_current_version(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """getwhen前版本

        Args:
            rule_id: 规thenID

        Returns:
            Optional[Dict]: when前版本的规then
        """
        versions = self._versions.get(rule_id, [])
        for v in versions:
            if v.get('is_current', False):
                return v
        return None

    def list_all_versions(self) -> Dict[str, List[str]]:
        """列出所有规then的版本

        Returns:
            Dict: {rule_id: [versions]}
        """
        return {
            rule_id: [v.get('version') for v in versions]
            for rule_id, versions in self._versions.items()
        }

    def _get_current_version(self, rule_id: str) -> float:
        """getwhen前版本号

        Args:
            rule_id: 规thenID

        Returns:
            float: when前版本号
        """
        versions = self._versions.get(rule_id, [])
        if not versions:
            return 0.0

        # 找到最大的版本号
        max_version = 0.0
        for v in versions:
            try:
                version = float(v.get('version', '0'))
                if version > max_version:
                    max_version = version
            except (ValueError, TypeError):
                pass

        return max_version

    def _get_next_version(self, rule_id: str) -> str:
        """get下一个版本号

        Args:
            rule_id: 规thenID

        Returns:
            str: 下一个版本号
        """
        return f"{self._get_current_version(rule_id) + 0.1:.1f}"


__all__ = [
    'RuleVersioner',
]
