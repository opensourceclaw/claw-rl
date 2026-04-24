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
Rule Versioner - 规则版本化管理
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class RuleVersioner:
    """规则版本管理器 - 创建/查询/回滚规则版本"""

    def __init__(self):
        # 存储规则版本历史: {rule_id: [versions]}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}

    def create_version(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """创建新版本

        Args:
            rule: 规则字典

        Returns:
            Dict: 带有版本信息的规则
        """
        rule_id = rule.get('id')
        if not rule_id:
            raise ValueError("Rule must have an ID")

        # 获取当前版本号
        current_version = self._get_current_version(rule_id)
        new_version = f"{float(current_version) + 0.1:.1f}"

        # 创建版本记录
        version_record = {
            **rule,
            'version': new_version,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_current': True
        }

        # 更新历史
        if rule_id not in self._versions:
            self._versions[rule_id] = []

        # 将之前的版本标记为非当前
        for v in self._versions[rule_id]:
            v['is_current'] = False

        # 添加新版本
        self._versions[rule_id].append(version_record)

        return version_record

    def get_history(self, rule_id: str) -> List[Dict[str, Any]]:
        """获取规则历史版本

        Args:
            rule_id: 规则ID

        Returns:
            List[Dict]: 版本历史列表
        """
        return self._versions.get(rule_id, [])

    def get_version(self, rule_id: str, version: str) -> Optional[Dict[str, Any]]:
        """获取指定版本

        Args:
            rule_id: 规则ID
            version: 版本号

        Returns:
            Optional[Dict]: 规则版本，如果不存在返回None
        """
        versions = self._versions.get(rule_id, [])
        for v in versions:
            if v.get('version') == version:
                return v
        return None

    def rollback(self, rule_id: str, version: str) -> Optional[Dict[str, Any]]:
        """回滚到指定版本

        Args:
            rule_id: 规则ID
            version: 目标版本号

        Returns:
            Optional[Dict]: 回滚后的规则，如果不存在返回None
        """
        target_version = self.get_version(rule_id, version)
        if not target_version:
            return None

        # 创建新版本（不回滚原版本，保留历史）
        new_rule = {
            **target_version,
            'version': self._get_next_version(rule_id),
            'rolled_back_from': version,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_current': True
        }

        # 更新历史
        for v in self._versions[rule_id]:
            v['is_current'] = False

        self._versions[rule_id].append(new_rule)

        return new_rule

    def get_current_version(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """获取当前版本

        Args:
            rule_id: 规则ID

        Returns:
            Optional[Dict]: 当前版本的规则
        """
        versions = self._versions.get(rule_id, [])
        for v in versions:
            if v.get('is_current', False):
                return v
        return None

    def list_all_versions(self) -> Dict[str, List[str]]:
        """列出所有规则的版本

        Returns:
            Dict: {rule_id: [versions]}
        """
        return {
            rule_id: [v.get('version') for v in versions]
            for rule_id, versions in self._versions.items()
        }

    def _get_current_version(self, rule_id: str) -> float:
        """获取当前版本号

        Args:
            rule_id: 规则ID

        Returns:
            float: 当前版本号
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
        """获取下一个版本号

        Args:
            rule_id: 规则ID

        Returns:
            str: 下一个版本号
        """
        return f"{self._get_current_version(rule_id) + 0.1:.1f}"


__all__ = [
    'RuleVersioner',
]
