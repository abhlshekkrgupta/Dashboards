"""
Application Configuration Management
Environment-specific settings, database connections, and API configurations.
"""
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json

@dataclass
class DatabaseConfig:
    """Database connection settings"""
    host: str = os.getenv("DB_HOST", "primary-db.enterprise.internal")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "analytics_production")
    user: str = os.getenv("DB_USER", "analytics_service")
    password: str = os.getenv("DB_PASSWORD", "")
    pool_min: int = 5
    pool_max: int = 25
    timeout: int = 30
    ssl_mode: str = "require"

@dataclass
class RedisConfig:
    """Redis cache settings"""
    host: str = os.getenv("REDIS_HOST", "cache.enterprise.internal")
    port: int = int(os.getenv("REDIS_PORT", "6379"))
    db: int = 0
    password: Optional[str] = os.getenv("REDIS_PASSWORD")
    ttl_default: int = 3600
    max_connections: int = 50

@dataclass
class APIConfig:
    """External API configurations"""
    base_url: str = os.getenv("API_BASE_URL", "https://api.enterprise.com")
    version: str = "v2"
    timeout: int = 60
    max_retries: int = 3
    rate_limit: int = 1000
    api_key: str = os.getenv("API_KEY", "")

@dataclass  
class MonitoringConfig:
    """Observability and monitoring settings"""
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    metrics_prefix: str = "enterprise_analytics"
    alert_webhook: Optional[str] = os.getenv("ALERT_WEBHOOK")

@dataclass
class FeatureFlags:
    """Feature flag configuration"""
    enable_real_time: bool = True
    enable_predictions: bool = True
    enable_export: bool = True
    enable_notifications: bool = False
    beta_features: List[str] = field(default_factory=lambda: [])

class AppConfig:
    """Centralized application configuration"""
    
    def __init__(self):
        self.app_name = "Enterprise Analytics Platform"
        self.version = "2.1.0"
        self.environment = os.getenv("ENV", "production")
        self.debug = self.environment == "development"
        
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.api = APIConfig()
        self.monitoring = MonitoringConfig()
        self.features = FeatureFlags()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary (excluding secrets)"""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "environment": self.environment,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "name": self.database.name
            },
            "api": {
                "base_url": self.api.base_url,
                "version": self.api.version
            },
            "monitoring": {
                "log_level": self.monitoring.log_level
            }
        }

# Global config instance
config = AppConfig()
