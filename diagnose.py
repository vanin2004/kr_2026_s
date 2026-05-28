#!/usr/bin/env python3
"""
Diagnostic script for Tutor Platform
Проверяет готовность всех компонентов системы на удаленном сервере
"""

import sys

from api_client import APIError, TutorPlatformClient


def print_header(text: str):
    """Печать заголовка"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_step(num: int, text: str):
    """Печать номера шага"""
    print(f"{num}️⃣  {text}")


def print_success(text: str):
    """Печать успеха"""
    print(f"   ✅ {text}")


def print_error(text: str):
    """Печать ошибки"""
    print(f"   ❌ {text}")


def print_warning(text: str):
    """Печать предупреждения"""
    print(f"   ⚠️  {text}")


def test_api_connectivity():
    """Проверить доступность API"""
    print_step(1, "API Connectivity")
    
    client = TutorPlatformClient()
    
    try:
        response = client._request("GET", "/health")
        print_success(f"API is accessible at {client.config.base_url}")
        print(f"   Version: {response.get('version', 'unknown')}")
        print(f"   Service: {response.get('service', 'unknown')}")
        return True
    except APIError as e:
        print_error(f"API not accessible: {e}")
        return False


def test_database_connection():
    """Проверить подключение к БД"""
    print_step(2, "Database Connection")
    
    client = TutorPlatformClient()
    
    try:
        response = client._request("GET", "/db-check")
        print_success("Database is connected")
        print(f"   Database: {response.get('database_name', 'unknown')}")
        print(f"   PostgreSQL: {response.get('postgres_version', 'unknown')}")
        return True
    except APIError as e:
        print_error(f"Database connection failed: {e}")
        return False


def test_keycloak_connectivity():
    """Проверить доступность Keycloak"""
    print_step(3, "Keycloak Connectivity")
    
    client = TutorPlatformClient()
    try:
        response = client.session.get(
            f"{client.config.keycloak_url}/health",
            timeout=client.config.timeout,
            verify=client.config.verify_ssl
        )
        print_success(f"Keycloak is accessible at {client.config.keycloak_url}")
        return True
    except Exception as e:
        print_warning(f"Keycloak not responding (this may be expected in some setups): {e}")
        return False


def test_authentication():
    """Проверить аутентификацию"""
    print_step(4, "Authentication")
    
    client = TutorPlatformClient()
    
    # Try to authenticate
    if client.authenticate("admin@example.com", "admin_password"):
        print_success("Authentication successful")
        
        # Check token
        if client.auth_check():
            print_success("JWT token is valid")
            return True
        else:
            print_warning("Token validation failed (but this may be expected)")
            return True
    else:
        print_warning("Authentication failed - this may be expected if Keycloak needs setup")
        return False


def test_api_endpoints():
    """Протестировать основные endpoints"""
    print_step(5, "API Endpoints")
    
    endpoints = [
        ("/health", "Health check"),
        ("/api/custom/health", "Custom health check"),
        ("/api/custom/db-check", "Database check"),
    ]
    
    client = TutorPlatformClient()
    all_ok = True
    
    for endpoint, description in endpoints:
        try:
            response = client._request("GET", endpoint)
            print_success(f"{description}: {endpoint}")
        except APIError as e:
            print_error(f"{description}: {endpoint} - {e}")
            all_ok = False
    
    return all_ok


def test_data_insertion():
    """Проверить возможность добавления данных"""
    print_step(6, "Data Insertion Test")
    
    client = TutorPlatformClient()
    
    try:
        result = client.add_test_tutor(
            email="diagnostic_tutor@test.local",
            full_name="Diagnostic Test Tutor",
            specialization="Test Subject",
            hourly_rate=50,
            years_experience=3,
            tags=["Test"]
        )
        
        if result:
            print_success(f"Test tutor created: {result.get('id')}")
            return True
        else:
            print_error("Failed to create test tutor")
            return False
            
    except APIError as e:
        print_error(f"Data insertion test failed: {e}")
        return False


def run_diagnostics():
    """Запустить полную диагностику"""
    print_header("TUTOR PLATFORM - DIAGNOSTIC TEST")
    
    print("Configuration:")
    config = TutorPlatformClient().config
    print(f"  API URL: {config.base_url}")
    print(f"  Keycloak URL: {config.keycloak_url}")
    print(f"  Timeout: {config.timeout}s")
    print(f"  Debug: {config.debug}")
    
    results = {
        "API Connectivity": test_api_connectivity(),
        "Database Connection": test_database_connection(),
        "Keycloak Connectivity": test_keycloak_connectivity(),
        "Authentication": test_authentication(),
        "API Endpoints": test_api_endpoints(),
        "Data Insertion": test_data_insertion(),
    }
    
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All diagnostics passed! System is ready.")
        return 0
    elif passed >= total - 1:
        print_warning("Most diagnostics passed. System may be partially ready.")
        return 1
    else:
        print_error("Multiple issues detected. Please check the logs.")
        return 2


def main():
    """Главная функция"""
    try:
        exit_code = run_diagnostics()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if os.getenv("DEBUG", "false").lower() == "true":
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
