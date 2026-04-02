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
