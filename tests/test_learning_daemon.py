# LearningDaemon Integration Test

import pytest
from claw_rl.core.learning_daemon import LearningDaemon

def test_learning_daemon_initialization():
    """Test LearningDaemon initialization"""
    daemon = LearningDaemon()
    assert daemon is not None
    assert hasattr(daemon, 'is_running')
    assert hasattr(daemon, 'start')
    assert hasattr(daemon, 'stop')

def test_learning_daemon_start_stop():
    """Test LearningDaemon start/stop functionality"""
    daemon = LearningDaemon()
    
    # Test start
    daemon.start()
    assert daemon.is_running() == True
    
    # Test stop
    daemon.stop()
    assert daemon.is_running() == False

def test_learning_daemon_health_check():
    """Test LearningDaemon health check"""
    daemon = LearningDaemon()
    
    # Test health check
    health = daemon.get_health_status()
    assert health is not None
    assert 'status' in health
    assert 'uptime' in health
    assert 'memory_usage' in health

def test_learning_daemon_metrics_collection():
    """Test LearningDaemon metrics collection"""
    daemon = LearningDaemon()
    
    # Test metrics collection
    metrics = daemon.collect_metrics()
    assert metrics is not None
    assert 'learning_rate' in metrics
    assert 'feedback_count' in metrics
    assert 'error_rate' in metrics

def test_learning_daemon_complete_lifecycle():
    """Test complete LearningDaemon lifecycle"""
    daemon = LearningDaemon()
    
    try:
        # Complete lifecycle
        daemon.start()
        # Let it run for a moment
        import time
        time.sleep(0.1)
        daemon.stop()
        
        assert True  # Success if no exception
        
    except Exception as e:
        assert False, f"LearningDaemon lifecycle failed: {e}"
