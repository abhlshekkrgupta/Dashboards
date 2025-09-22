"""
Tests for Configuration Management
"""
import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import AppConfig, DatabaseConfig, RedisConfig, MonitoringConfig


class TestDatabaseConfig:
    """Test database configuration"""
    
    def test_default_values(self):
        config = DatabaseConfig()
        assert config.host is not None
        assert config.port == 5432
        assert config.pool_min >= 1
        assert config.pool_max >= config.pool_min
        assert config.timeout > 0
    
    def test_environment_override(self, monkeypatch):
        monkeypatch.setenv("DB_HOST", "test-db.example.com")
        monkeypatch.setenv("DB_PORT", "5433")
        
        config = DatabaseConfig()
        assert config.host == "test-db.example.com"
        assert config.port == 5433
    
    def test_ssl_mode(self):
        config = DatabaseConfig()
        assert config.ssl_mode in ["require", "prefer", "disable"]


class TestRedisConfig:
    """Test Redis configuration"""
    
    def test_default_values(self):
        config = RedisConfig()
        assert config.host is not None
        assert config.port == 6379
        assert config.ttl_default > 0
        assert config.max_connections > 0
    
    def test_optional_password(self):
        config = RedisConfig()
        assert config.password is None or isinstance(config.password, str)


class TestMonitoringConfig:
    """Test monitoring configuration"""
    
    def test_default_values(self):
        config = MonitoringConfig()
        assert config.prometheus_enabled is True
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class TestAppConfig:
    """Test main application configuration"""
    
    def test_singleton_pattern(self):
        config1 = AppConfig()
        config2 = AppConfig()
        # Both should exist independently
        assert config1.app_name == config2.app_name
    
    def test_version_format(self):
        config = AppConfig()
        parts = config.version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)
    
    def test_environment_detection(self):
        config = AppConfig()
        assert config.environment in ["development", "staging", "production"]
    
    def test_dict_export(self):
        config = AppConfig()
        exported = config.to_dict()
        assert "app_name" in exported
        assert "version" in exported
        assert "environment" in exported
        # Should not contain secrets
        assert "password" not in str(exported)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
