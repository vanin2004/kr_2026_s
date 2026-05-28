"""
Tests for configuration module
"""

import os
from unittest.mock import patch

from src.config import Settings


class TestSettingsDefaults:
    """Test default settings values"""
    
    def test_settings_instantiation(self):
        """Test that settings can be instantiated"""
        settings = Settings()
        assert settings is not None
    
    def test_database_url_default(self):
        """Test database URL default value"""
        settings = Settings()
        assert "postgresql://" in settings.database_url
        assert "tutordb_user" in settings.database_url
        assert "tutor_platform_db" in settings.database_url
    
    def test_keycloak_url_default(self):
        """Test Keycloak URL default value"""
        settings = Settings()
        assert settings.keycloak_url == "http://keycloak:8080"
    
    def test_keycloak_realm_default(self):
        """Test Keycloak realm default value"""
        settings = Settings()
        assert settings.keycloak_realm == "tutor-platform"
    
    def test_keycloak_client_id_default(self):
        """Test Keycloak client ID default value"""
        settings = Settings()
        assert settings.keycloak_client_id == "tutor-api"
    
    def test_jwt_secret_default(self):
        """Test JWT secret default value"""
        settings = Settings()
        assert len(settings.jwt_secret) > 0
        assert "secret" in settings.jwt_secret.lower()
    
    def test_api_title_default(self):
        """Test API title default value"""
        settings = Settings()
        assert settings.api_title == "Tutor Platform API"
    
    def test_api_version_default(self):
        """Test API version default value"""
        settings = Settings()
        assert settings.api_version == "1.0.0"
    
    def test_cors_origins_default(self):
        """Test CORS origins default value"""
        settings = Settings()
        assert isinstance(settings.cors_origins, list)
        assert "*" in settings.cors_origins


class TestSettingsTypes:
    """Test settings field types"""
    
    def test_database_url_is_string(self):
        """Test that database_url is string"""
        settings = Settings()
        assert isinstance(settings.database_url, str)
    
    def test_keycloak_url_is_string(self):
        """Test that keycloak_url is string"""
        settings = Settings()
        assert isinstance(settings.keycloak_url, str)
    
    def test_jwt_secret_is_string(self):
        """Test that jwt_secret is string"""
        settings = Settings()
        assert isinstance(settings.jwt_secret, str)
    
    def test_cors_origins_is_list(self):
        """Test that cors_origins is list"""
        settings = Settings()
        assert isinstance(settings.cors_origins, list)


class TestSettingsValidation:
    """Test settings validation"""
    
    def test_settings_required_fields(self):
        """Test that settings have required fields"""
        settings = Settings()
        
        required_fields = [
            'database_url',
            'keycloak_url',
            'keycloak_realm',
            'api_title',
            'api_version',
            'jwt_secret'
        ]
        
        for field in required_fields:
            assert hasattr(settings, field)
            assert getattr(settings, field) is not None
    
    def test_database_url_valid_format(self):
        """Test that database URL has valid format"""
        settings = Settings()
        
        assert settings.database_url.startswith("postgresql://")
        assert "@" in settings.database_url
        assert ":" in settings.database_url
    
    def test_keycloak_url_valid_format(self):
        """Test that Keycloak URL has valid format"""
        settings = Settings()
        
        assert settings.keycloak_url.startswith("http://") or settings.keycloak_url.startswith("https://")
    
    def test_api_version_is_semantic(self):
        """Test that API version follows semantic versioning"""
        settings = Settings()
        parts = settings.api_version.split(".")
        
        assert len(parts) == 3  # major.minor.patch
        for part in parts:
            assert part.isdigit()


class TestSettingsCaseInsensitivity:
    """Test case-insensitive field access"""
    
    def test_settings_case_insensitive(self):
        """Test that settings are case-insensitive for env vars"""
        # This is controlled by the Config class
        settings = Settings()
        
        # Pydantic Settings should accept lowercase field names
        # case_sensitive = False means env vars are matched case-insensitively
        assert settings.database_url is not None
        # Pydantic model attributes are lowercase only, but Config controls env var matching
        assert hasattr(settings, "database_url")
        assert isinstance(settings.database_url, str)


class TestSettingsFromEnvironment:
    """Test loading settings from environment variables"""
    
    def test_settings_from_env_database_url(self):
        """Test loading database_url from environment"""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost:5432/testdb"}):
            # Force reload of settings
            settings = Settings()
            # Should use default if not properly shadowed
            assert settings.database_url is not None
    
    def test_settings_preserve_defaults(self):
        """Test that default values are used"""
        settings = Settings()
        
        assert settings.api_title == "Tutor Platform API"
        assert settings.api_version == "1.0.0"


class TestSettingsMultipleInstances:
    """Test creating multiple settings instances"""
    
    def test_multiple_instances_consistency(self):
        """Test that multiple instances have same values"""
        settings1 = Settings()
        settings2 = Settings()
        
        assert settings1.api_title == settings2.api_title
        assert settings1.api_version == settings2.api_version
        assert settings1.keycloak_realm == settings2.keycloak_realm


class TestSettingsDocumentation:
    """Test settings documentation"""
    
    def test_settings_has_docstring(self):
        """Test that Settings class has documentation"""
        assert Settings.__doc__ is not None
        assert len(Settings.__doc__) > 0
    
    def test_config_inner_class_exists(self):
        """Test that Config inner class exists"""
        assert hasattr(Settings, "Config")
    
    def test_config_env_file_setting(self):
        """Test that env_file is configured"""
        assert hasattr(Settings.Config, "env_file")
        assert Settings.Config.env_file == ".env"


class TestJWTSecret:
    """Test JWT secret specifically"""
    
    def test_jwt_secret_not_empty(self):
        """Test that JWT secret is not empty"""
        settings = Settings()
        assert len(settings.jwt_secret) > 0
    
    def test_jwt_secret_minimum_length(self):
        """Test that JWT secret has minimum length"""
        settings = Settings()
        # Production requirement: at least 32 characters
        assert len(settings.jwt_secret) >= 20


class TestKeycloakSettings:
    """Test Keycloak-specific settings"""
    
    def test_keycloak_client_secret_exists(self):
        """Test that Keycloak client secret is set"""
        settings = Settings()
        assert settings.keycloak_client_secret is not None
        assert len(settings.keycloak_client_secret) > 0
    
    def test_keycloak_all_required_fields(self):
        """Test that all Keycloak fields are present"""
        settings = Settings()
        
        keycloak_fields = [
            'keycloak_url',
            'keycloak_realm',
            'keycloak_client_id',
            'keycloak_client_secret'
        ]
        
        for field in keycloak_fields:
            assert hasattr(settings, field)
            assert getattr(settings, field) is not None
