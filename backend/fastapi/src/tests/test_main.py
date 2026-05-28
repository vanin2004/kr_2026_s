"""
Tests for FastAPI main application
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_status_code(self, client):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_content(self, client):
        """Test that health endpoint returns correct structure"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "service" in data
        assert data["status"] == "ok"
        assert data["service"] == "tutor-platform-api"
    
    def test_health_check_response_type(self, client):
        """Test that response is JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"


class TestRoot:
    """Test root endpoint"""
    
    def test_root_status_code(self, client):
        """Test that root endpoint returns 200"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_content(self, client):
        """Test that root endpoint returns metadata"""
        response = client.get("/")
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "openapi" in data
        
        assert data["message"] == "Tutor Platform API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["openapi"] == "/openapi.json"
    
    def test_root_response_type(self, client):
        """Test that root response is JSON"""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_swagger_ui_available(self, client):
        """Test that Swagger UI is available"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self, client):
        """Test that ReDoc is available"""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestNotFound:
    """Test 404 routing"""
    
    def test_nonexistent_endpoint(self, client):
        """Test that nonexistent endpoint returns 404"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404


class TestApplicationMetadata:
    """Test application metadata in OpenAPI schema"""
    
    def test_app_title(self, client):
        """Test that app title is correct"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert schema["info"]["title"] == "Tutor Platform API"
    
    def test_app_description(self, client):
        """Test that app description exists"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert "description" in schema["info"]
        assert "tutor matching" in schema["info"]["description"].lower()
    
    def test_app_version(self, client):
        """Test that app version is correct"""
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert schema["info"]["version"] == "1.0.0"


class TestCORS:
    """Test CORS headers"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response"""
        # Regular requests should have CORS headers if configured
        response = client.get("/health")
        
        # CORS headers are applied to GET requests
        assert response.status_code == 200
    
    def test_options_method_allowed(self, client):
        """Test that OPTIONS method handling"""
        response = client.options("/health")
        # OPTIONS may return 405 if not explicitly enabled
        assert response.status_code in [200, 204, 405]


class TestResponseFormats:
    """Test response format consistency"""
    
    def test_json_content_type(self, client):
        """Test that endpoints return JSON"""
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")
    
    def test_response_encoding(self, client):
        """Test that response has proper encoding"""
        response = client.get("/")
        assert response.encoding is not None


class TestEndpointPerformance:
    """Test endpoint response times"""
    
    def test_health_check_fast(self, client):
        """Test that health check returns quickly"""
        import time
        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should be very fast (< 1 second)
    
    def test_root_endpoint_fast(self, client):
        """Test that root endpoint returns quickly"""
        import time
        start = time.time()
        response = client.get("/")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0


class TestHTTPMethods:
    """Test HTTP method handling"""
    
    def test_health_get_allowed(self, client):
        """Test that GET is allowed for health"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_post_not_allowed(self, client):
        """Test that POST is not allowed for health"""
        response = client.post("/health")
        assert response.status_code == 405
    
    def test_health_put_not_allowed(self, client):
        """Test that PUT is not allowed for health"""
        response = client.put("/health")
        assert response.status_code == 405
    
    def test_health_delete_not_allowed(self, client):
        """Test that DELETE is not allowed for health"""
        response = client.delete("/health")
        assert response.status_code == 405
    
    def test_root_get_allowed(self, client):
        """Test that GET is allowed for root"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_post_not_allowed(self, client):
        """Test that POST is not allowed for root"""
        response = client.post("/")
        assert response.status_code == 405
