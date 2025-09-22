"""
Utility Functions and Helpers
Common utilities used across the enterprise analytics platform.
"""
import hashlib
import json
import time
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# ============================================
# Retry Utilities
# ============================================

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for exponential backoff retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.1f}s")
                        time.sleep(wait_time)
            raise last_exception
        return wrapper
    return decorator

# ============================================
# Caching Utilities
# ============================================

def generate_cache_key(*args, **kwargs) -> str:
    """Generate a deterministic cache key from arguments"""
    key_data = json.dumps({'args': str(args), 'kwargs': str(sorted(kwargs.items()))}, sort_keys=True)
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]

class SimpleCache:
    """In-memory cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry > time.time():
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
        
        expiry = time.time() + (ttl or self.default_ttl)
        self._cache[key] = (value, expiry)

# ============================================
# Data Formatting Utilities
# ============================================

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency values for display"""
    if abs(amount) >= 1_000_000_000:
        return f"{currency} {amount/1_000_000_000:,.2f}B"
    elif abs(amount) >= 1_000_000:
        return f"{currency} {amount/1_000_000:,.2f}M"
    elif abs(amount) >= 1_000:
        return f"{currency} {amount/1_000:,.2f}K"
    return f"{currency} {amount:,.2f}"

def format_number(value: Union[int, float], precision: int = 2) -> str:
    """Format large numbers with suffixes"""
    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.{precision}f}B"
    elif abs(value) >= 1_000_000:
        return f"{value/1_000_000:.{precision}f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.{precision}f}K"
    return f"{value:.{precision}f}"

def format_duration(seconds: float) -> str:
    """Format duration in human-readable form"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

# ============================================
# Validation Utilities
# ============================================

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_date_range(start_date: str, end_date: str) -> bool:
    """Validate that start_date is before end_date"""
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        return start <= end
    except ValueError:
        return False

# ============================================
# Logging Utilities
# ============================================

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Configure logger with consistent formatting"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, level.upper()))
    return logger

class Timer:
    """Context manager for performance timing"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.debug(f"Starting: {self.name}")
        return self
    
    def __exit__(self, *args):
        elapsed = time.perf_counter() - self.start_time
        logger.info(f"{self.name} completed in {format_duration(elapsed)}")
