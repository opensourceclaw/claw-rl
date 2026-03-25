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
claw-rl Calibration Error Learning

Learns confidence calibration from prediction vs outcome.
Improves meta-cognitive accuracy over time.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class CalibrationRecord:
    """Calibration record for learning"""
    id: str
    capability: str  # intent_understanding, memory_retrieval, etc.
    predicted_confidence: float  # 0.0-1.0
    actual_outcome: bool  # True=correct, False=incorrect
    calibration_error: float = 0.0  # |predicted - actual|
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        # Calculate calibration error
        actual = 1.0 if self.actual_outcome else 0.0
        self.calibration_error = abs(self.predicted_confidence - actual)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "capability": self.capability,
            "predicted_confidence": self.predicted_confidence,
            "actual_outcome": self.actual_outcome,
            "calibration_error": self.calibration_error,
            "timestamp": self.timestamp
        }


@dataclass
class CapabilityCalibration:
    """Calibration data for a capability"""
    capability: str
    total_predictions: int = 0
    correct_predictions: int = 0
    avg_calibration_error: float = 0.0
    overconfidence_count: int = 0  # High confidence but wrong
    underconfidence_count: int = 0  # Low confidence but right
    calibration_adjustment: float = 0.0  # Suggested adjustment
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "capability": self.capability,
            "total_predictions": self.total_predictions,
            "correct_predictions": self.correct_predictions,
            "avg_calibration_error": self.avg_calibration_error,
            "overconfidence_count": self.overconfidence_count,
            "underconfidence_count": self.underconfidence_count,
            "calibration_adjustment": self.calibration_adjustment,
            "last_updated": self.last_updated
        }


class CalibrationLearner:
    """
    Calibration Error Learner
    
    Learns confidence calibration from:
    - Predicted confidence vs actual outcomes
    - Overconfidence detection
    - Underconfidence detection
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize Calibration Learner
        
        Args:
            data_dir: Directory for storing learning data
        """
        self.data_dir = data_dir or os.path.expanduser("~/.openclaw/workspace/claw-rl/data")
        self.calibrations: Dict[str, CapabilityCalibration] = {}
        self.calibration_history: List[CalibrationRecord] = []
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing calibrations
        self._load_calibrations()
    
    def _load_calibrations(self) -> None:
        """Load calibrations from disk"""
        calib_file = os.path.join(self.data_dir, "calibrations.json")
        
        if os.path.exists(calib_file):
            try:
                with open(calib_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for cap, calib_data in data.items():
                    self.calibrations[cap] = CapabilityCalibration(
                        capability=calib_data['capability'],
                        total_predictions=calib_data['total_predictions'],
                        correct_predictions=calib_data['correct_predictions'],
                        avg_calibration_error=calib_data['avg_calibration_error'],
                        overconfidence_count=calib_data['overconfidence_count'],
                        underconfidence_count=calib_data['underconfidence_count'],
                        calibration_adjustment=calib_data['calibration_adjustment'],
                        last_updated=calib_data.get('last_updated', datetime.now().isoformat())
                    )
                
                print(f"✅ Loaded {len(self.calibrations)} capability calibrations")
            except Exception as e:
                print(f"⚠️  Could not load calibrations: {e}")
                self._initialize_default_calibrations()
        else:
            self._initialize_default_calibrations()
    
    def _initialize_default_calibrations(self) -> None:
        """Initialize default calibrations"""
        default_capabilities = [
            "intent_understanding",
            "memory_retrieval",
            "collaboration",
            "value_judgment",
            "domain_knowledge",
            "emotional_intelligence"
        ]
        
        for cap in default_capabilities:
            self.calibrations[cap] = CapabilityCalibration(capability=cap)
        
        self._save_calibrations()
    
    def _save_calibrations(self) -> None:
        """Save calibrations to disk"""
        calib_file = os.path.join(self.data_dir, "calibrations.json")
        
        data = {cap: calib.to_dict() for cap, calib in self.calibrations.items()}
        
        with open(calib_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(self.calibrations)} capability calibrations")
    
    def record_calibration(self, record: CalibrationRecord) -> None:
        """
        Record a calibration data point
        
        Args:
            record: Calibration record
        """
        self.calibration_history.append(record)
        
        # Limit history size
        if len(self.calibration_history) > 1000:
            self.calibration_history = self.calibration_history[-1000:]
        
        # Save record
        self._save_record(record)
        
        # Update calibration
        self._update_calibration(record)
    
    def _save_record(self, record: CalibrationRecord) -> None:
        """Save calibration record to disk"""
        records_file = os.path.join(self.data_dir, "calibration_records.jsonl")
        
        with open(records_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + '\n')
    
    def _update_calibration(self, record: CalibrationRecord) -> None:
        """
        Update calibration based on record
        
        Args:
            record: Calibration record
        """
        if record.capability not in self.calibrations:
            self.calibrations[record.capability] = CapabilityCalibration(
                capability=record.capability
            )
        
        calib = self.calibrations[record.capability]
        
        # Update counts
        calib.total_predictions += 1
        if record.actual_outcome:
            calib.correct_predictions += 1
        
        # Update average calibration error (running average)
        n = calib.total_predictions
        old_avg = calib.avg_calibration_error
        calib.avg_calibration_error = old_avg + (record.calibration_error - old_avg) / n
        
        # Detect overconfidence/underconfidence
        if record.predicted_confidence > 0.8 and not record.actual_outcome:
            calib.overconfidence_count += 1
        elif record.predicted_confidence < 0.5 and record.actual_outcome:
            calib.underconfidence_count += 1
        
        # Calculate calibration adjustment
        calib.calibration_adjustment = self._calculate_adjustment(calib)
        
        # Update timestamp
        calib.last_updated = datetime.now().isoformat()
        
        print(f"✅ Updated calibration for '{record.capability}': error={calib.avg_calibration_error:.2f}")
        
        self._save_calibrations()
    
    def _calculate_adjustment(self, calib: CapabilityCalibration) -> float:
        """
        Calculate suggested calibration adjustment
        
        Args:
            calib: Capability calibration
            
        Returns:
            float: Suggested adjustment
        """
        if calib.total_predictions < 10:
            return 0.0  # Not enough data
        
        # Calculate accuracy
        accuracy = calib.correct_predictions / calib.total_predictions
        
        # Calculate overconfidence rate
        overconfidence_rate = calib.overconfidence_count / calib.total_predictions
        
        # Calculate underconfidence rate
        underconfidence_rate = calib.underconfidence_count / calib.total_predictions
        
        # Suggest adjustment
        if overconfidence_rate > 0.2:
            # Too overconfident: suggest reducing confidence
            return -0.1
        elif underconfidence_rate > 0.2:
            # Too underconfident: suggest increasing confidence
            return +0.1
        elif accuracy < 0.7:
            # Low accuracy: suggest reducing confidence
            return -0.05
        elif accuracy > 0.9:
            # High accuracy: suggest increasing confidence
            return +0.05
        
        return 0.0
    
    def get_calibrated_confidence(self, capability: str, raw_confidence: float) -> float:
        """
        Get calibrated confidence for a capability
        
        Args:
            capability: Capability name
            raw_confidence: Raw confidence score (0.0-1.0)
            
        Returns:
            float: Calibrated confidence
        """
        if capability not in self.calibrations:
            return raw_confidence
        
        calib = self.calibrations[capability]
        
        # Apply adjustment
        adjusted = raw_confidence + calib.calibration_adjustment
        
        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, adjusted))
    
    def get_calibration_quality(self, capability: str) -> str:
        """
        Get calibration quality assessment
        
        Args:
            capability: Capability name
            
        Returns:
            str: Quality assessment (excellent/good/fair/poor)
        """
        if capability not in self.calibrations:
            return "unknown"
        
        calib = self.calibrations[capability]
        
        if calib.total_predictions < 10:
            return "insufficient_data"
        
        if calib.avg_calibration_error < 0.1:
            return "excellent"
        elif calib.avg_calibration_error < 0.2:
            return "good"
        elif calib.avg_calibration_error < 0.3:
            return "fair"
        else:
            return "poor"
    
    def get_calibration_report(self, capability: str = None) -> Dict:
        """
        Get calibration report
        
        Args:
            capability: Specific capability (None for all)
            
        Returns:
            Dict: Calibration report
        """
        if capability:
            if capability not in self.calibrations:
                return {"status": "unknown_capability"}
            
            calib = self.calibrations[capability]
            return {
                "status": "ok",
                "capability": capability,
                "total_predictions": calib.total_predictions,
                "accuracy": calib.correct_predictions / calib.total_predictions if calib.total_predictions > 0 else 0.0,
                "avg_calibration_error": calib.avg_calibration_error,
                "overconfidence_rate": calib.overconfidence_count / calib.total_predictions if calib.total_predictions > 0 else 0.0,
                "underconfidence_rate": calib.underconfidence_count / calib.total_predictions if calib.total_predictions > 0 else 0.0,
                "calibration_adjustment": calib.calibration_adjustment,
                "quality": self.get_calibration_quality(capability)
            }
        else:
            # Report for all capabilities
            reports = {}
            for cap in self.calibrations:
                reports[cap] = self.get_calibration_report(cap)
            return {
                "status": "ok",
                "capabilities": reports,
                "total_records": len(self.calibration_history)
            }
    
    def get_learning_statistics(self) -> Dict:
        """
        Get learning statistics
        
        Returns:
            Dict: Learning statistics
        """
        excellent = sum(1 for c in self.calibrations.values() if self.get_calibration_quality(c.capability) == "excellent")
        good = sum(1 for c in self.calibrations.values() if self.get_calibration_quality(c.capability) == "good")
        
        return {
            "total_capabilities": len(self.calibrations),
            "total_records": len(self.calibration_history),
            "excellent_calibration": excellent,
            "good_calibration": good,
            "avg_calibration_error": sum(c.avg_calibration_error for c in self.calibrations.values()) / len(self.calibrations) if self.calibrations else 0.0
        }
