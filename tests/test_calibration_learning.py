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
Tests for claw-rl Calibration Error Learning
"""

import pytest
import tempfile
import shutil
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from claw_rl.learning.calibration import CalibrationLearner, CalibrationRecord


class TestCalibrationLearner:
    """Test Calibration Learner"""
    
    @pytest.fixture
    def temp_learner(self):
        """Create temporary learner"""
        temp_dir = tempfile.mkdtemp()
        learner = CalibrationLearner(data_dir=temp_dir)
        yield learner
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_learner):
        """Test initialization"""
        assert len(temp_learner.calibrations) == 6
        assert "intent_understanding" in temp_learner.calibrations
    
    def test_record_calibration(self, temp_learner):
        """Test recording calibration"""
        record = CalibrationRecord(
            id="test_001",
            capability="intent_understanding",
            predicted_confidence=0.9,
            actual_outcome=True
        )
        temp_learner.record_calibration(record)
        
        # Check calibration was updated
        calib = temp_learner.calibrations["intent_understanding"]
        assert calib.total_predictions == 1
        assert calib.correct_predictions == 1
    
    def test_overconfidence_detection(self, temp_learner):
        """Test overconfidence detection"""
        # Record overconfident predictions (high confidence, wrong)
        for i in range(5):
            record = CalibrationRecord(
                id=f"test_{i}",
                capability="intent_understanding",
                predicted_confidence=0.9,
                actual_outcome=False
            )
            temp_learner.record_calibration(record)
        
        calib = temp_learner.calibrations["intent_understanding"]
        assert calib.overconfidence_count == 5
    
    def test_get_calibrated_confidence(self, temp_learner):
        """Test getting calibrated confidence"""
        # Record some data first
        for i in range(10):
            record = CalibrationRecord(
                id=f"test_{i}",
                capability="intent_understanding",
                predicted_confidence=0.8,
                actual_outcome=(i < 8)  # 80% accuracy
            )
            temp_learner.record_calibration(record)
        
        # Get calibrated confidence
        calibrated = temp_learner.get_calibrated_confidence("intent_understanding", 0.8)
        assert 0.0 <= calibrated <= 1.0
    
    def test_calibration_quality(self, temp_learner):
        """Test calibration quality assessment"""
        quality = temp_learner.get_calibration_quality("intent_understanding")
        assert quality in ["insufficient_data", "excellent", "good", "fair", "poor"]
    
    def test_calibration_report(self, temp_learner):
        """Test calibration report"""
        report = temp_learner.get_calibration_report("intent_understanding")
        assert "status" in report
        assert "capability" in report
        assert "total_predictions" in report
    
    def test_learning_statistics(self, temp_learner):
        """Test learning statistics"""
        stats = temp_learner.get_learning_statistics()
        assert "total_capabilities" in stats
        assert "total_records" in stats
        assert "excellent_calibration" in stats
        assert "good_calibration" in stats
        assert "avg_calibration_error" in stats
    
    def test_multiple_capabilities(self, temp_learner):
        """Test multiple capabilities"""
        capabilities = ["intent_understanding", "memory_retrieval", "task_planning"]
        
        for cap in capabilities:
            for i in range(5):
                record = CalibrationRecord(
                    id=f"test_{cap}_{i}",
                    capability=cap,
                    predicted_confidence=0.7,
                    actual_outcome=(i % 2 == 0)
                )
                temp_learner.record_calibration(record)
        
        # Check that all capabilities have data
        stats = temp_learner.get_learning_statistics()
        assert stats["total_records"] == 15
    
    def test_calibration_error_calculation(self, temp_learner):
        """Test calibration error calculation"""
        # Perfect calibration
        record1 = CalibrationRecord(
            id="test_perfect",
            capability="intent_understanding",
            predicted_confidence=0.8,
            actual_outcome=True
        )
        # Should have small error when confidence matches outcome
        assert record1.calibration_error >= 0.0
        
        # Poor calibration
        record2 = CalibrationRecord(
            id="test_poor",
            capability="intent_understanding",
            predicted_confidence=0.9,
            actual_outcome=False
        )
        # Should have large error when confidence doesn't match outcome
        assert record2.calibration_error > record1.calibration_error
    
    def test_empty_learner(self, temp_learner):
        """Test learner with no data"""
        stats = temp_learner.get_learning_statistics()
        assert stats["total_records"] == 0
    
    def test_confidence_bounds(self, temp_learner):
        """Test confidence bounds"""
        # Record calibration with bounds testing
        for conf in [0.0, 0.5, 1.0]:
            record = CalibrationRecord(
                id=f"test_{conf}",
                capability="intent_understanding",
                predicted_confidence=conf,
                actual_outcome=True
            )
            temp_learner.record_calibration(record)
        
        # All confidences should be in [0, 1]
        stats = temp_learner.get_learning_statistics()
        assert stats["total_records"] == 3
    
    def test_overconfidence_adjustment(self, temp_learner):
        """Test overconfidence adjustment"""
        # Record many overconfident predictions
        for i in range(20):
            record = CalibrationRecord(
                id=f"test_{i}",
                capability="intent_understanding",
                predicted_confidence=0.9,
                actual_outcome=False  # Wrong but high confidence
            )
            temp_learner.record_calibration(record)
        
        # Check calibration
        cal = temp_learner.calibrations.get("intent_understanding")
        assert cal is not None
        assert cal.overconfidence_count > 0
    
    def test_underconfidence_adjustment(self, temp_learner):
        """Test underconfidence adjustment"""
        # Record many underconfident predictions
        for i in range(20):
            record = CalibrationRecord(
                id=f"test_{i}",
                capability="intent_understanding",
                predicted_confidence=0.3,
                actual_outcome=True  # Correct but low confidence
            )
            temp_learner.record_calibration(record)
        
        # Check calibration
        cal = temp_learner.calibrations.get("intent_understanding")
        assert cal is not None
        assert cal.underconfidence_count > 0
    
    def test_calibration_quality_levels(self, temp_learner):
        """Test calibration quality levels"""
        # Record calibrations with different patterns
        for i in range(10):
            record = CalibrationRecord(
                id=f"test_{i}",
                capability="intent_understanding",
                predicted_confidence=0.8,
                actual_outcome=(i < 8)  # 80% accuracy
            )
            temp_learner.record_calibration(record)
        
        quality = temp_learner.get_calibration_quality("intent_understanding")
        
        # Quality should be one of the valid levels
        assert quality in ["insufficient_data", "excellent", "good", "fair", "poor", "unknown"]
    
    def test_get_calibration_report(self, temp_learner):
        """Test getting calibration report"""
        # Record some calibrations
        for i in range(5):
            record = CalibrationRecord(
                id=f"test_{i}",
                capability="intent_understanding",
                predicted_confidence=0.7,
                actual_outcome=True
            )
            temp_learner.record_calibration(record)
        
        report = temp_learner.get_calibration_report("intent_understanding")
        
        # Report should have required fields
        assert "capability" in report
        assert "total_predictions" in report
    
    def test_capability_not_found(self, temp_learner):
        """Test getting calibration for non-existent capability"""
        quality = temp_learner.get_calibration_quality("non_existent_capability")
        
        # Should return unknown for unknown capability
        assert quality in ["insufficient_data", "unknown"]
    
    def test_record_with_metadata(self, temp_learner):
        """Test recording calibration with metadata"""
        record = CalibrationRecord(
            id="test_metadata",
            capability="intent_understanding",
            predicted_confidence=0.8,
            actual_outcome=True
        )
        
        temp_learner.record_calibration(record)
        
        stats = temp_learner.get_learning_statistics()
        assert stats["total_records"] == 1
