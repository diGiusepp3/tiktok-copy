import requests
import sys
import json
from datetime import datetime

class UnrestrictedAITester:
    def __init__(self, base_url="https://unrestricted-ai-70.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session_id = None
        self.message_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json() if response.content else {}
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_create_session(self):
        """Test creating a new chat session"""
        success, response = self.run_test(
            "Create New Session",
            "POST",
            "sessions",
            200,
            data={"title": "Test Chat Session"}
        )
        if success and 'id' in response:
            self.session_id = response['id']
            print(f"   Created session ID: {self.session_id}")
            return True
        return False

    def test_get_sessions(self):
        """Test getting all sessions"""
        success, response = self.run_test(
            "Get All Sessions",
            "GET",
            "sessions",
            200
        )
        if success:
            print(f"   Found {len(response)} sessions")
        return success

    def test_get_session_by_id(self):
        """Test getting a specific session"""
        if not self.session_id:
            print("❌ No session ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Session by ID",
            "GET",
            f"sessions/{self.session_id}",
            200
        )
        return success

    def test_update_session_title(self):
        """Test updating session title"""
        if not self.session_id:
            print("❌ No session ID available for testing")
            return False
            
        success, response = self.run_test(
            "Update Session Title",
            "PUT",
            f"sessions/{self.session_id}",
            200,
            data={"title": "Updated Test Title"}
        )
        return success

    def test_send_message(self):
        """Test sending a message to get AI response"""
        if not self.session_id:
            print("❌ No session ID available for testing")
            return False
            
        success, response = self.run_test(
            "Send Message (AI Response)",
            "POST",
            f"sessions/{self.session_id}/messages",
            200,
            data={"content": "Hello, this is a test message. Please respond with 'Test successful'."}
        )
        if success and 'id' in response:
            self.message_id = response['id']
            print(f"   AI Response: {response.get('content', 'No content')[:100]}...")
        return success

    def test_get_messages(self):
        """Test getting messages for a session"""
        if not self.session_id:
            print("❌ No session ID available for testing")
            return False
            
        success, response = self.run_test(
            "Get Session Messages",
            "GET",
            f"sessions/{self.session_id}/messages",
            200
        )
        if success:
            print(f"   Found {len(response)} messages")
        return success

    def test_export_json(self):
        """Test exporting session as JSON"""
        if not self.session_id:
            print("❌ No session ID available for testing")
            return False
            
        success, response = self.run_test(
            "Export Session as JSON",
            "GET",
            f"sessions/{self.session_id}/export",
            200,
            params={"format": "json"}
        )
        return success

    def test_export_txt(self):
        """Test exporting session as TXT"""
        if not self.session_id:
            print("❌ No session ID available for testing")
            return False
            
        success, response = self.run_test(
            "Export Session as TXT",
            "GET",
            f"sessions/{self.session_id}/export",
            200,
            params={"format": "txt"}
        )
        return success

    def test_delete_session(self):
        """Test deleting a session"""
        if not self.session_id:
            print("❌ No session ID available for testing")
            return False
            
        success, response = self.run_test(
            "Delete Session",
            "DELETE",
            f"sessions/{self.session_id}",
            200
        )
        return success

    def test_code_syntax_message(self):
        """Test sending a message with code to verify syntax highlighting support"""
        # Create a new session for this test
        success, response = self.run_test(
            "Create Session for Code Test",
            "POST",
            "sessions",
            200,
            data={"title": "Code Test Session"}
        )
        
        if not success or 'id' not in response:
            return False
            
        code_session_id = response['id']
        
        # Send a message requesting code
        success, response = self.run_test(
            "Send Code Request Message",
            "POST",
            f"sessions/{code_session_id}/messages",
            200,
            data={"content": "Please write a simple Python function that adds two numbers. Use proper code formatting."}
        )
        
        # Clean up
        self.run_test("Delete Code Test Session", "DELETE", f"sessions/{code_session_id}", 200)
        
        return success

def main():
    print("🚀 Starting Unrestricted AI Backend API Tests")
    print("=" * 60)
    
    tester = UnrestrictedAITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Create Session", tester.test_create_session),
        ("Get All Sessions", tester.test_get_sessions),
        ("Get Session by ID", tester.test_get_session_by_id),
        ("Update Session Title", tester.test_update_session_title),
        ("Send Message & AI Response", tester.test_send_message),
        ("Get Session Messages", tester.test_get_messages),
        ("Export as JSON", tester.test_export_json),
        ("Export as TXT", tester.test_export_txt),
        ("Code Syntax Test", tester.test_code_syntax_message),
        ("Delete Session", tester.test_delete_session),
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if failed_tests:
        print(f"❌ Failed tests: {', '.join(failed_tests)}")
        return 1
    else:
        print("✅ All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())