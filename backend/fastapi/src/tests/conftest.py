"""
Pytest configuration and shared fixtures
"""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_app_root():
    """Get test application root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def test_settings_dict():
    """Provide test settings as dictionary"""
    return {
        "database_url": "postgresql://test:test@localhost:5432/test_db",
        "keycloak_url": "http://localhost:8080",
        "keycloak_realm": "test-realm",
        "keycloak_client_id": "test-client",
        "keycloak_client_secret": "test-secret",
        "jwt_secret": "test-jwt-secret-key-min-32-chars-long",
        "api_title": "Test API",
        "api_version": "1.0.0",
        "cors_origins": ["http://localhost:3000"]
    }


@pytest.fixture
def mock_env_vars(test_settings_dict, monkeypatch):
    """Mock environment variables for testing"""
    for key, value in test_settings_dict.items():
        env_key = key.upper()
        monkeypatch.setenv(env_key, str(value))
    return test_settings_dict


# Pytest configuration and markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test collection options
def pytest_collection_modifyitems(config, items):
    """Modify items during test collection"""
    for item in items:
        # Mark all tests as unit by default
        if "test_" in item.nodeid:
            item.add_marker(pytest.mark.unit)


# Custom assert rewrites
pytest.register_assert_rewrite("tests.helpers")
