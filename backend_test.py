#!/usr/bin/env python3
"""
Backend API Testing for Clone App (OnlyFans + TikTok Hybrid)
Tests all major API endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class CloneAppTester:
    def __init__(self, base_url="https://mediasort-3.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })

    def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text, "status_code": response.status_code}

            return success, response_data

        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        success, data = self.make_request('GET', '/')
        self.log_result(
            "API Root Endpoint", 
            success and "Clone App API" in str(data),
            f"Response: {data}" if not success else ""
        )
        return success

    def test_system_stats(self):
        """Test system stats endpoint"""
        success, data = self.make_request('GET', '/system/stats')
        self.log_result(
            "System Stats", 
            success and isinstance(data, dict),
            f"Response: {data}" if not success else ""
        )
        return success

    def test_register_user(self):
        """Test user registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        test_user = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@test.com",
            "password": "test123456",
            "display_name": f"Test User {timestamp}"
        }

        success, data = self.make_request('POST', '/auth/register', test_user, 200)
        
        if success and 'token' in data:
            self.token = data['token']
            self.user_id = data.get('user', {}).get('id')
            self.log_result("User Registration", True)
        else:
            self.log_result("User Registration", False, f"Response: {data}")
        
        return success

    def test_login_user(self):
        """Test user login with test credentials"""
        login_data = {
            "email": "test@test.com",
            "password": "test123"
        }

        success, data = self.make_request('POST', '/auth/login', login_data, 200)
        
        if success and 'token' in data:
            self.token = data['token']
            self.user_id = data.get('user', {}).get('id')
            self.log_result("User Login (Test Credentials)", True)
        else:
            # Try with different credentials or create user first
            self.log_result("User Login (Test Credentials)", False, f"Response: {data}")
        
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        if not self.token:
            self.log_result("Get Current User", False, "No token available")
            return False

        success, data = self.make_request('GET', '/auth/me')
        self.log_result(
            "Get Current User", 
            success and 'id' in data,
            f"Response: {data}" if not success else ""
        )
        return success

    def test_get_feed(self):
        """Test getting video/media feed"""
        success, data = self.make_request('GET', '/feed?limit=10')
        self.log_result(
            "Get Feed", 
            success and 'items' in data,
            f"Response: {data}" if not success else ""
        )
        return success

    def test_get_creators(self):
        """Test getting creators list"""
        success, data = self.make_request('GET', '/creators?limit=10')
        self.log_result(
            "Get Creators", 
            success and 'creators' in data,
            f"Response: {data}" if not success else ""
        )
        return success

    def test_scraper_analyze(self):
        """Test URL analysis for scraping"""
        test_url = {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }

        success, data = self.make_request('POST', '/scraper/analyze', test_url)
        self.log_result(
            "Scraper URL Analysis", 
            success and (isinstance(data, dict)),
            f"Response: {data}" if not success else ""
        )
        return success

    def test_file_browser(self):
        """Test file browser functionality"""
        success, data = self.make_request('GET', '/files/browse?path=/')
        self.log_result(
            "File Browser", 
            success and 'items' in data,
            f"Response: {data}" if not success else ""
        )
        return success

    def test_cli_execute(self):
        """Test CLI command execution"""
        if not self.token:
            self.log_result("CLI Execute", False, "No token available")
            return False

        test_command = {
            "command": "echo 'Hello World'"
        }

        success, data = self.make_request('POST', '/cli/execute', test_command)
        self.log_result(
            "CLI Execute", 
            success and 'stdout' in data,
            f"Response: {data}" if not success else ""
        )
        return success

    def test_scraper_tasks(self):
        """Test getting scraper task history"""
        if not self.token:
            self.log_result("Scraper Tasks", False, "No token available")
            return False

        success, data = self.make_request('GET', '/scraper/tasks?limit=10')
        self.log_result(
            "Scraper Tasks", 
            success and 'tasks' in data,
            f"Response: {data}" if not success else ""
        )
        return success

    def test_legacy_media_scan(self):
        """Test legacy media scanning"""
        success, data = self.make_request('GET', '/files/scan?limit=5')
        self.log_result(
            "Legacy Media Scan", 
            success and 'creators' in data,
            f"Response: {data}" if not success else ""
        )
        return success

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Clone App Backend API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)

        # Basic connectivity tests
        print("\n📋 Basic API Tests:")
        self.test_root_endpoint()
        self.test_system_stats()

        # Authentication tests
        print("\n🔐 Authentication Tests:")
        auth_success = self.test_register_user()
        if not auth_success:
            # Try login with existing test user
            auth_success = self.test_login_user()
        
        if auth_success:
            self.test_get_current_user()

        # Content tests
        print("\n📱 Content & Feed Tests:")
        self.test_get_feed()
        self.test_get_creators()

        # Scraper tests
        print("\n🔍 Scraper Tests:")
        self.test_scraper_analyze()
        if self.token:
            self.test_scraper_tasks()

        # File management tests
        print("\n📁 File Management Tests:")
        self.test_file_browser()
        self.test_legacy_media_scan()

        # CLI tests (protected)
        print("\n💻 CLI Tests:")
        if self.token:
            self.test_cli_execute()

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return 1

def main():
    """Main test runner"""
    tester = CloneAppTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())