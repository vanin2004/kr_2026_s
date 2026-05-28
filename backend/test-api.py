#!/usr/bin/env python3

"""
API Testing Suite
Comprehensive testing of all API endpoints
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, Tuple

import requests


class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.auth_token = None
        
    def log(self, message: str, color: str = 'reset'):
        """Print colored output"""
        colors = {
            'reset': '\033[0m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'cyan': '\033[36m',
        }
        print(f"{colors.get(color, '')}{message}{colors['reset']}")

    def test_endpoint(
        self, 
        method: str, 
        endpoint: str, 
        description: str, 
        expected_status: int,
        data: Dict[str, Any] | None = None,
        headers: Dict[str, str] | None = None
    ) -> Tuple[bool, requests.Response | None]:
        """Test a single API endpoint"""
        self.total_tests += 1
        
        self.log(f"\n[Test {self.total_tests}] {description}", 'blue')
        self.log(f"Request: {method} {self.base_url}{endpoint}")
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Prepare headers
            req_headers = {
                'Content-Type': 'application/json',
                **(headers or {})
            }
            
            if self.auth_token:
                req_headers['Authorization'] = f'Bearer {self.auth_token}'
            
            # Make request based on method
            if method == 'GET':
                response = self.session.get(url, headers=req_headers, timeout=10, allow_redirects=False)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=req_headers, timeout=10, allow_redirects=False)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=req_headers, timeout=10, allow_redirects=False)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=req_headers, timeout=10, allow_redirects=False)
            elif method == 'OPTIONS':
                response = self.session.options(url, headers=req_headers, timeout=10, allow_redirects=False)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            self.log(f"Response Status: {response.status_code}")
            
            # Try to parse JSON
            try:
                body = response.json()
                self.log(f"Response Body: {json.dumps(body, indent=2)}")
            except Exception:
                self.log(f"Response Body: {response.text[:500]}")
                body = response.text
            
            # Check status code
            if response.status_code == expected_status:
                self.log("✓ PASSED", 'green')
                self.passed_tests += 1
                return True, response
            else:
                self.log(f"✗ FAILED (expected {expected_status}, got {response.status_code})", 'red')
                self.failed_tests += 1
                return False, response
                
        except requests.exceptions.RequestException as e:
            self.log(f"✗ FAILED - {str(e)}", 'red')
            self.failed_tests += 1
            return False, None
        except Exception as e:
            self.log(f"✗ ERROR - {str(e)}", 'red')
            self.failed_tests += 1
            return False, None

    def run_all_tests(self):
        """Run the complete test suite"""
        self.log('=' * 50, 'yellow')
        self.log('API Testing Suite', 'yellow')
        self.log(f'Base URL: {self.base_url}', 'yellow')
        self.log(f'Timestamp: {datetime.now().isoformat()}', 'yellow')
        self.log('=' * 50, 'yellow')
        
        # Health Checks
        self.log('\n--- Health Checks ---', 'cyan')
        self.test_endpoint('GET', '/health', 'FastAPI Health Check', 200)
        self.test_endpoint('GET', '/', 'Root Endpoint (Gateway)', 200)
        
        # Database Check
        self.log('\n--- Database Connectivity ---', 'cyan')
        self.test_endpoint('GET', '/api/custom/db-check', 'FastAPI Database Check', 200)
        
        # PostgREST API (requires auth)
        self.log('\n--- PostgREST API (Protected) ---', 'cyan')
        self.test_endpoint(
            'GET', 
            '/api/data/health_check', 
            'PostgREST Health Check (no auth)', 
            401
        )
        self.test_endpoint(
            'GET',
            '/api/data/users',
            'PostgREST Users Table (no auth)',
            401
        )
        
        # Authentication
        self.log('\n--- Authentication ---', 'cyan')
        self.test_endpoint('GET', '/auth', 'Auth Endpoint', 301)
        
        # CORS
        self.log('\n--- CORS ---', 'cyan')
        self.test_endpoint(
            'OPTIONS',
            '/api/data/health_check',
            'CORS Preflight Request',
            204,
            headers={'Origin': 'http://localhost:3000'}
        )
        
        # Error Cases
        self.log('\n--- Error Cases ---', 'cyan')
        self.test_endpoint(
            'GET',
            '/api/nonexistent',
            'Non-existent Endpoint',
            200  # Nginx redirects to root endpoint
        )
        self.test_endpoint(
            'POST',
            '/api/custom/invalid',
            'POST to Invalid Endpoint',
            404,
            data={'test': 'data'}
        )
        
        # Custom Logic
        self.log('\n--- Custom Business Logic ---', 'cyan')
        self.test_endpoint(
            'GET',
            '/api/custom/health',
            'Custom Health Endpoint',
            200  # This endpoint exists now
        )
        
        # Test Summary
        self.log('\n' + '=' * 50, 'yellow')
        self.log('Test Summary', 'yellow')
        self.log('=' * 50, 'yellow')
        self.log(f'Total Tests: {self.total_tests}')
        self.log(f'Passed: {self.passed_tests}', 'green')
        self.log(f'Failed: {self.failed_tests}', 'red')
        self.log('=' * 50, 'yellow')
        
        return 0 if self.failed_tests == 0 else 1

def main():
    base_url = 'http://157.245.244.194:80'
    
    tester = APITester(base_url)
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
