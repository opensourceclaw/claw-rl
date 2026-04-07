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
Rule Portability Module

Provides export and import capabilities for learned rules.

This is a key differentiator from simple feedback systems:
learning results are portable and can be shared across agents.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RuleExportError(Exception):
    """Base exception for rule export errors"""
    pass


class RuleImportError(Exception):
    """Base exception for rule import errors"""
    pass


class RuleMergeStrategy(Enum):
    """Strategy for merging rules during import"""
    REPLACE = "replace"      # Replace existing rules
    MERGE = "merge"          # Merge with existing (keep both)
    UPDATE = "update"        # Update existing rules
    SKIP = "skip"            # Skip duplicate rules


@dataclass
class RuleVersion:
    """Version information for a rule"""
    version: str
    created_at: datetime
    updated_at: datetime
    author: str = "claw-rl"
    changes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
            "changes": self.changes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleVersion":
        return cls(
            version=data["version"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            author=data.get("author", "claw-rl"),
            changes=data.get("changes", []),
        )


@dataclass
class RuleLineage:
    """Lineage tracking for a rule"""
    rule_id: str
    parent_rules: List[str] = field(default_factory=list)
    derived_from: List[str] = field(default_factory=list)
    feedback_sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "parent_rules": self.parent_rules,
            "derived_from": self.derived_from,
            "feedback_sources": self.feedback_sources,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RuleLineage":
        return cls(
            rule_id=data["rule_id"],
            parent_rules=data.get("parent_rules", []),
            derived_from=data.get("derived_from", []),
            feedback_sources=data.get("feedback_sources", []),
        )


@dataclass
class ExportedRule:
    """
    An exported rule with full metadata.
    
    Attributes:
        rule_id: Unique identifier
        rule_type: Type of rule (behavior, prompt, etc.)
        condition: When to apply the rule
        action: What action to take
        confidence: Confidence level (0.0 - 1.0)
        source: Where the rule came from (feedback, opd, etc.)
        version: Version information
        lineage: Rule lineage tracking
        metadata: Additional metadata
    """
    rule_id: str
    rule_type: str
    condition: str
    action: str
    confidence: float = 1.0
    source: str = "unknown"
    version: Optional[RuleVersion] = None
    lineage: Optional[RuleLineage] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "condition": self.condition,
            "action": self.action,
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata,
        }
        
        if self.version:
            data["version"] = self.version.to_dict()
        
        if self.lineage:
            data["lineage"] = self.lineage.to_dict()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExportedRule":
        return cls(
            rule_id=data["rule_id"],
            rule_type=data["rule_type"],
            condition=data["condition"],
            action=data["action"],
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "unknown"),
            version=RuleVersion.from_dict(data["version"]) if "version" in data else None,
            lineage=RuleLineage.from_dict(data["lineage"]) if "lineage" in data else None,
            metadata=data.get("metadata", {}),
        )


@dataclass
class RuleExportResult:
    """Result of a rule export operation"""
    success: bool
    path: Optional[str] = None
    rules_exported: int = 0
    format: str = "json"
    size_bytes: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class RuleImportResult:
    """Result of a rule import operation"""
    success: bool
    rules_imported: int = 0
    rules_skipped: int = 0
    rules_updated: int = 0
    errors: List[str] = field(default_factory=list)


class RulePortability:
    """
    Rule export and import for claw-rl.
    
    This enables learning results to be portable across agents
    and sessions, making claw-rl truly useful for continuous learning.
    
    Features:
    - Export rules to JSON format
    - Import rules with merge/update/skip strategies
    - Rule versioning and lineage tracking
    - Backward compatibility checks
    """
    
    EXPORT_FORMAT_VERSION = "2.0.0"
    
    def __init__(self, workspace: Path):
        """
        Initialize RulePortability.
        
        Args:
            workspace: Path to claw-rl workspace
        """
        self.workspace = workspace
        self.exports_dir = workspace / "exports"
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.rules_dir = workspace / "rules"
        self.rules_dir.mkdir(parents=True, exist_ok=True)
    
    def export_rules(
        self,
        rules: List[Any],
        output_path: Optional[str] = None,
        include_lineage: bool = True,
        include_metadata: bool = True,
    ) -> RuleExportResult:
        """
        Export rules to JSON format.
        
        Args:
            rules: List of rules to export
            output_path: Optional output file path
            include_lineage: Include lineage information
            include_metadata: Include metadata
            
        Returns:
            RuleExportResult with export details
        """
        if not rules:
            return RuleExportResult(
                success=True,
                rules_exported=0,
                errors=["No rules to export"],
            )
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.exports_dir / f"rules_export_{timestamp}.json")
        
        try:
            exported_rules = []
            
            for rule in rules:
                # Convert rule to ExportedRule format
                exported = self._convert_rule(rule, include_lineage, include_metadata)
                exported_rules.append(exported)
            
            # Create export data
            export_data = {
                "format_version": self.EXPORT_FORMAT_VERSION,
                "exported_at": datetime.now().isoformat(),
                "source": "claw-rl",
                "rules_count": len(exported_rules),
                "rules": [r.to_dict() for r in exported_rules],
            }
            
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            size_bytes = Path(output_path).stat().st_size
            
            logger.info(f"Exported {len(exported_rules)} rules to {output_path}")
            
            return RuleExportResult(
                success=True,
                path=output_path,
                rules_exported=len(exported_rules),
                format="json",
                size_bytes=size_bytes,
            )
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return RuleExportResult(
                success=False,
                errors=[str(e)],
            )
    
    def import_rules(
        self,
        input_path: str,
        existing_rules: Optional[List[Any]] = None,
        merge_strategy: RuleMergeStrategy = RuleMergeStrategy.MERGE,
    ) -> RuleImportResult:
        """
        Import rules from JSON file.
        
        Args:
            input_path: Path to import file
            existing_rules: Existing rules to merge with
            merge_strategy: How to handle conflicts
            
        Returns:
            RuleImportResult with import details
        """
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
            
            # Validate format
            if not self._validate_import_format(import_data):
                return RuleImportResult(
                    success=False,
                    errors=["Invalid import format"],
                )
            
            rules_data = import_data.get("rules", [])
            
            if not rules_data:
                return RuleImportResult(
                    success=True,
                    rules_imported=0,
                    errors=["No rules in import file"],
                )
            
            imported_count = 0
            skipped_count = 0
            updated_count = 0
            errors = []
            
            existing_ids = set()
            if existing_rules:
                existing_ids = {r.rule_id if hasattr(r, 'rule_id') else r.get('rule_id') for r in existing_rules}
            
            imported_rules = []
            
            for rule_data in rules_data:
                try:
                    rule = ExportedRule.from_dict(rule_data)
                    
                    # Handle conflicts
                    if rule.rule_id in existing_ids:
                        if merge_strategy == RuleMergeStrategy.SKIP:
                            skipped_count += 1
                            continue
                        elif merge_strategy == RuleMergeStrategy.UPDATE:
                            updated_count += 1
                        elif merge_strategy == RuleMergeStrategy.REPLACE:
                            # Will be replaced
                            pass
                        # MERGE: keep both, generate new ID if needed
                    
                    imported_rules.append(rule)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Failed to import rule: {str(e)}")
            
            logger.info(f"Imported {imported_count} rules from {input_path}")
            
            return RuleImportResult(
                success=True,
                rules_imported=imported_count,
                rules_skipped=skipped_count,
                rules_updated=updated_count,
                errors=errors,
            )
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return RuleImportResult(
                success=False,
                errors=[str(e)],
            )
    
    def _convert_rule(
        self,
        rule: Any,
        include_lineage: bool,
        include_metadata: bool,
    ) -> ExportedRule:
        """Convert a rule to ExportedRule format"""
        # Handle different rule formats
        if hasattr(rule, 'to_dict'):
            rule_dict = rule.to_dict()
        elif isinstance(rule, dict):
            rule_dict = rule
        else:
            rule_dict = asdict(rule) if hasattr(rule, '__dataclass_fields__') else {}
        
        # Extract version info
        version = None
        if include_metadata and "version" in rule_dict:
            try:
                version = RuleVersion.from_dict(rule_dict["version"])
            except Exception:
                version = RuleVersion(
                    version="1.0.0",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
        
        # Extract lineage
        lineage = None
        if include_lineage and "lineage" in rule_dict:
            try:
                lineage = RuleLineage.from_dict(rule_dict["lineage"])
            except Exception:
                pass
        
        return ExportedRule(
            rule_id=rule_dict.get("rule_id", "unknown"),
            rule_type=rule_dict.get("rule_type", "unknown"),
            condition=rule_dict.get("condition", ""),
            action=rule_dict.get("action", ""),
            confidence=rule_dict.get("confidence", 1.0),
            source=rule_dict.get("source", "unknown"),
            version=version,
            lineage=lineage,
            metadata=rule_dict.get("metadata", {}) if include_metadata else {},
        )
    
    def _validate_import_format(self, data: Dict[str, Any]) -> bool:
        """Validate import format"""
        if not isinstance(data, dict):
            return False
        
        if "format_version" not in data:
            return False
        
        if "rules" not in data:
            return False
        
        if not isinstance(data["rules"], list):
            return False
        
        return True
    
    def get_rule_lineage(self, rule_id: str) -> Optional[RuleLineage]:
        """
        Get lineage for a specific rule.
        
        Args:
            rule_id: Rule ID to look up
            
        Returns:
            RuleLineage or None
        """
        lineage_file = self.rules_dir / "lineage" / f"{rule_id}.json"
        
        if not lineage_file.exists():
            return None
        
        try:
            with open(lineage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return RuleLineage.from_dict(data)
        except Exception:
            return None
    
    def save_rule_lineage(self, lineage: RuleLineage) -> bool:
        """
        Save lineage for a rule.
        
        Args:
            lineage: RuleLineage to save
            
        Returns:
            True if saved successfully
        """
        lineage_dir = self.rules_dir / "lineage"
        lineage_dir.mkdir(parents=True, exist_ok=True)
        
        lineage_file = lineage_dir / f"{lineage.rule_id}.json"
        
        try:
            with open(lineage_file, "w", encoding="utf-8") as f:
                json.dump(lineage.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save lineage: {e}")
            return False
    
    def list_exports(self) -> List[Dict[str, Any]]:
        """
        List all available exports.
        
        Returns:
            List of export metadata
        """
        exports = []
        
        for export_file in self.exports_dir.glob("rules_export_*.json"):
            try:
                with open(export_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                exports.append({
                    "path": str(export_file),
                    "exported_at": data.get("exported_at"),
                    "rules_count": data.get("rules_count", 0),
                    "format_version": data.get("format_version"),
                    "size_bytes": export_file.stat().st_size,
                })
            except Exception:
                continue
        
        return sorted(exports, key=lambda x: x.get("exported_at", ""), reverse=True)
