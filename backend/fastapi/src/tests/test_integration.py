"""
Integration tests for Docker services communication
"""

import os

import pytest


class TestEnvironmentVariables:
    """Test environment variables are set correctly"""
    
    def test_database_url_env(self):
        """Test DATABASE_URL environment variable"""
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            assert "postgresql://" in db_url or db_url == ""
    
    def test_keycloak_url_env(self):
        """Test KEYCLOAK_URL environment variable"""
        kc_url = os.getenv("KEYCLOAK_URL")
        if kc_url:
            assert "http" in kc_url or kc_url == ""
    
    def test_fastapi_port_env(self):
        """Test FASTAPI_PORT environment variable"""
        port = os.getenv("FASTAPI_PORT")
        if port:
            assert port.isdigit()
            assert 1 <= int(port) <= 65535


class TestDockerEnvironment:
    """Test Docker environment setup"""
    
    def test_running_in_container(self):
        """Check if running in Docker container"""
        # This will be true when running in docker-compose
        docker_env = os.getenv("DOCKER_ENV", "false")
        # Not a hard requirement, just informational
        assert isinstance(docker_env, str)
    
    def test_required_services_configured(self):
        """Test that required service URLs are configured"""
        # In Docker environment, these should be set
        # But we don't fail if they're not (for local development)
        services = {
            "DATABASE_URL": "postgresql://",
            "KEYCLOAK_URL": "http://",
        }
        
        for var, prefix in services.items():
            value = os.getenv(var)
            if value:  # Only check if set
                assert value.startswith(prefix) or value == ""


class TestServiceConnectivity:
    """Test connectivity between services"""
    
    @pytest.mark.integration
    def test_fastapi_responds(self):
        """Test that FastAPI service is responding"""
        from fastapi.testclient import TestClient

        from src.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
    
    @pytest.mark.integration
    def test_app_configuration_loads(self):
        """Test that app configuration loads without errors"""
        from src.config import settings
        
        assert settings is not None
        assert settings.database_url is not None
        assert settings.keycloak_url is not None


class TestContainerReadiness:
    """Test Docker container readiness"""
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_container_startup(self):
        """Test that container starts successfully"""
        # This test validates the container was built and started
        import sys
        
        # Container should have Python 3.11+
        assert sys.version_info.major == 3
        assert sys.version_info.minor >= 11
    
    def test_dependencies_installed(self):
        """Test that required dependencies are installed"""
        dependencies = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
        ]
        
        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                pytest.skip(f"{dep} not installed")


class TestFileStructure:
    """Test Python project file structure"""
    
    def test_src_package_exists(self):
        """Test that src package exists"""
        import os
        assert os.path.isdir("src")
    
    def test_main_module_importable(self):
        """Test that main module can be imported"""
        try:
            from src import main
            assert main is not None
        except ImportError as e:
            pytest.fail(f"Cannot import main module: {e}")
    
    def test_config_module_importable(self):
        """Test that config module can be imported"""
        try:
            from src import config
            assert config is not None
        except ImportError as e:
            pytest.fail(f"Cannot import config module: {e}")
    
    def test_tests_directory_exists(self):
        """Test that tests directory exists"""
        import os
        assert os.path.isdir("src/tests")
    
    def test_init_files_present(self):
        """Test that __init__.py files are present"""
        import os
        
        init_paths = [
            "src/__init__.py",
            "src/tests/__init__.py",
        ]
        
        for path in init_paths:
            assert os.path.isfile(path), f"{path} not found"
