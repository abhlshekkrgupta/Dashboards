"""
Pytest configuration and shared fixtures
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture(scope="session")
def random_seed():
    """Set random seed for reproducibility"""
    np.random.seed(42)
    return 42


@pytest.fixture
def date_range():
    """Common date range for tests"""
    return pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')


@pytest.fixture
def numeric_data():
    """Sample numeric data"""
    return np.random.normal(100, 15, 100)


@pytest.fixture
def categorical_data():
    """Sample categorical data"""
    return np.random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'], 100)


@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    class MockConnection:
        def execute(self, query):
            return pd.DataFrame({'id': [1, 2, 3], 'value': [100, 200, 300]})
        
        def close(self):
            pass
    
    return MockConnection()


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m "not slow"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
