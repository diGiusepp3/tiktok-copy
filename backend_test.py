#!/usr/bin/env python3
"""
ChatGPT Clone Backend API Test Suite
Tests all backend endpoints thoroughly including database operations and OpenAI integration
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://chatty-clone-14.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_conversation_id = None
        self.test_message_id = None
        self.results = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    def test_get_conversations(self) -> bool:
        """Test GET /api/conversations"""
        try:
            response = self.session.get(f"{self.base_url}/conversations")
            
            if response.status_code == 200:
                conversations = response.json()
                if isinstance(conversations, list):
                    self.log_result("GET /api/conversations", True, f"Retrieved {len(conversations)} conversations")
                    return True
                else:
                    self.log_result("GET /api/conversations", False, "Response is not a list", conversations)
                    return False
            else:
                self.log_result("GET /api/conversations", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("GET /api/conversations", False, f"Exception: {str(e)}")
            return False
    
    def test_create_conversation(self) -> bool:
        """Test POST /api/conversations"""
        try:
            payload = {"title": "Test Conversation"}
            response = self.session.post(
                f"{self.base_url}/conversations",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                conversation = response.json()
                required_fields = ["id", "title", "created_at", "updated_at"]
                
                if all(field in conversation for field in required_fields):
                    if conversation["title"] == "Test Conversation":
                        self.test_conversation_id = conversation["id"]
                        self.log_result("POST /api/conversations", True, f"Created conversation with ID: {self.test_conversation_id}")
                        return True
                    else:
                        self.log_result("POST /api/conversations", False, "Title mismatch", conversation)
                        return False
                else:
                    self.log_result("POST /api/conversations", False, "Missing required fields", conversation)
                    return False
            else:
                self.log_result("POST /api/conversations", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("POST /api/conversations", False, f"Exception: {str(e)}")
            return False
    
    def test_send_message(self) -> bool:
        """Test POST /api/conversations/{id}/messages"""
        if not self.test_conversation_id:
            self.log_result("POST /api/conversations/{id}/messages", False, "No test conversation ID available")
            return False
            
        try:
            payload = {"content": "Tell me a joke"}
            response = self.session.post(
                f"{self.base_url}/conversations/{self.test_conversation_id}/messages",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                
                # Check response structure
                if "user_message" in chat_response and "assistant_message" in chat_response:
                    user_msg = chat_response["user_message"]
                    assistant_msg = chat_response["assistant_message"]
                    
                    # Validate user message
                    if (user_msg["role"] == "user" and 
                        user_msg["content"] == "Tell me a joke" and
                        user_msg["conversation_id"] == self.test_conversation_id):
                        
                        # Validate assistant message
                        if (assistant_msg["role"] == "assistant" and 
                            len(assistant_msg["content"]) > 0 and
                            assistant_msg["conversation_id"] == self.test_conversation_id):
                            
                            self.test_message_id = assistant_msg["id"]
                            
                            # Check if response looks like a real AI response (not mocked)
                            ai_content = assistant_msg["content"].lower()
                            if any(keyword in ai_content for keyword in ["joke", "funny", "laugh", "humor", "why", "what"]):
                                self.log_result("POST /api/conversations/{id}/messages", True, 
                                              f"AI responded intelligently with: {assistant_msg['content'][:100]}...")
                                return True
                            else:
                                self.log_result("POST /api/conversations/{id}/messages", False, 
                                              f"AI response doesn't seem contextual: {assistant_msg['content']}")
                                return False
                        else:
                            self.log_result("POST /api/conversations/{id}/messages", False, "Invalid assistant message", assistant_msg)
                            return False
                    else:
                        self.log_result("POST /api/conversations/{id}/messages", False, "Invalid user message", user_msg)
                        return False
                else:
                    self.log_result("POST /api/conversations/{id}/messages", False, "Missing user_message or assistant_message", chat_response)
                    return False
            else:
                self.log_result("POST /api/conversations/{id}/messages", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("POST /api/conversations/{id}/messages", False, f"Exception: {str(e)}")
            return False
    
    def test_get_messages(self) -> bool:
        """Test GET /api/conversations/{id}/messages"""
        if not self.test_conversation_id:
            self.log_result("GET /api/conversations/{id}/messages", False, "No test conversation ID available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/conversations/{self.test_conversation_id}/messages")
            
            if response.status_code == 200:
                messages = response.json()
                
                if isinstance(messages, list) and len(messages) >= 2:
                    # Should have at least user message and assistant message
                    user_msg = messages[0]
                    assistant_msg = messages[1]
                    
                    if (user_msg["role"] == "user" and 
                        assistant_msg["role"] == "assistant" and
                        user_msg["content"] == "Tell me a joke"):
                        self.log_result("GET /api/conversations/{id}/messages", True, f"Retrieved {len(messages)} messages correctly")
                        return True
                    else:
                        self.log_result("GET /api/conversations/{id}/messages", False, "Message content/roles incorrect", messages)
                        return False
                else:
                    self.log_result("GET /api/conversations/{id}/messages", False, f"Expected at least 2 messages, got {len(messages) if isinstance(messages, list) else 'non-list'}", messages)
                    return False
            else:
                self.log_result("GET /api/conversations/{id}/messages", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("GET /api/conversations/{id}/messages", False, f"Exception: {str(e)}")
            return False
    
    def test_regenerate_response(self) -> bool:
        """Test POST /api/conversations/{id}/regenerate"""
        if not self.test_conversation_id or not self.test_message_id:
            self.log_result("POST /api/conversations/{id}/regenerate", False, "No test conversation ID or message ID available")
            return False
            
        try:
            payload = {"message_id": self.test_message_id}
            response = self.session.post(
                f"{self.base_url}/conversations/{self.test_conversation_id}/regenerate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                new_message = response.json()
                
                if (new_message["role"] == "assistant" and 
                    new_message["conversation_id"] == self.test_conversation_id and
                    len(new_message["content"]) > 0):
                    
                    # Check if it's a different response (regenerated)
                    self.log_result("POST /api/conversations/{id}/regenerate", True, 
                                  f"Successfully regenerated response: {new_message['content'][:100]}...")
                    return True
                else:
                    self.log_result("POST /api/conversations/{id}/regenerate", False, "Invalid regenerated message", new_message)
                    return False
            else:
                self.log_result("POST /api/conversations/{id}/regenerate", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("POST /api/conversations/{id}/regenerate", False, f"Exception: {str(e)}")
            return False
    
    def test_conversation_title_generation(self) -> bool:
        """Test that conversation title is auto-generated from first message"""
        try:
            # Create a new conversation
            payload = {"title": "New chat"}
            response = self.session.post(
                f"{self.base_url}/conversations",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result("Title Generation Test", False, "Failed to create conversation for title test")
                return False
                
            conv_id = response.json()["id"]
            
            # Send first message
            payload = {"content": "What is machine learning?"}
            response = self.session.post(
                f"{self.base_url}/conversations/{conv_id}/messages",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                self.log_result("Title Generation Test", False, "Failed to send message for title test")
                return False
            
            # Check if title was updated
            response = self.session.get(f"{self.base_url}/conversations")
            if response.status_code == 200:
                conversations = response.json()
                test_conv = next((c for c in conversations if c["id"] == conv_id), None)
                
                if test_conv and test_conv["title"] != "New chat":
                    self.log_result("Title Generation Test", True, f"Title auto-generated: '{test_conv['title']}'")
                    
                    # Clean up
                    self.session.delete(f"{self.base_url}/conversations/{conv_id}")
                    return True
                else:
                    self.log_result("Title Generation Test", False, "Title was not auto-generated", test_conv)
                    return False
            else:
                self.log_result("Title Generation Test", False, "Failed to fetch conversations for title verification")
                return False
                
        except Exception as e:
            self.log_result("Title Generation Test", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_conversation(self) -> bool:
        """Test DELETE /api/conversations/{id}"""
        if not self.test_conversation_id:
            self.log_result("DELETE /api/conversations/{id}", False, "No test conversation ID available")
            return False
            
        try:
            response = self.session.delete(f"{self.base_url}/conversations/{self.test_conversation_id}")
            
            if response.status_code == 200:
                # Verify conversation is deleted by checking if it's in the conversations list
                verify_response = self.session.get(f"{self.base_url}/conversations")
                
                if verify_response.status_code == 200:
                    conversations = verify_response.json()
                    deleted_conv = next((c for c in conversations if c["id"] == self.test_conversation_id), None)
                    
                    if deleted_conv is None:
                        # Also check that messages are empty
                        msg_response = self.session.get(f"{self.base_url}/conversations/{self.test_conversation_id}/messages")
                        if msg_response.status_code == 200 and msg_response.json() == []:
                            self.log_result("DELETE /api/conversations/{id}", True, "Conversation and messages deleted successfully (cascade delete working)")
                            return True
                        else:
                            self.log_result("DELETE /api/conversations/{id}", False, "Messages not properly deleted")
                            return False
                    else:
                        self.log_result("DELETE /api/conversations/{id}", False, "Conversation still exists in list")
                        return False
                else:
                    self.log_result("DELETE /api/conversations/{id}", False, "Failed to verify deletion")
                    return False
            else:
                self.log_result("DELETE /api/conversations/{id}", False, f"Status code: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("DELETE /api/conversations/{id}", False, f"Exception: {str(e)}")
            return False
    
    def test_database_persistence(self) -> bool:
        """Test that data persists in MySQL database"""
        try:
            # Create conversation
            payload = {"title": "Persistence Test"}
            response = self.session.post(f"{self.base_url}/conversations", json=payload)
            if response.status_code != 200:
                self.log_result("Database Persistence Test", False, "Failed to create test conversation")
                return False
                
            conv_id = response.json()["id"]
            
            # Send message
            payload = {"content": "Test persistence"}
            response = self.session.post(f"{self.base_url}/conversations/{conv_id}/messages", json=payload)
            if response.status_code != 200:
                self.log_result("Database Persistence Test", False, "Failed to send test message")
                return False
            
            # Wait a moment
            time.sleep(1)
            
            # Retrieve and verify data persists
            response = self.session.get(f"{self.base_url}/conversations/{conv_id}/messages")
            if response.status_code == 200:
                messages = response.json()
                if len(messages) >= 2 and messages[0]["content"] == "Test persistence":
                    self.log_result("Database Persistence Test", True, "Data persisted correctly in MySQL")
                    
                    # Clean up
                    self.session.delete(f"{self.base_url}/conversations/{conv_id}")
                    return True
                else:
                    self.log_result("Database Persistence Test", False, "Data not persisted correctly", messages)
                    return False
            else:
                self.log_result("Database Persistence Test", False, "Failed to retrieve persisted data")
                return False
                
        except Exception as e:
            self.log_result("Database Persistence Test", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting ChatGPT Clone Backend API Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Basic Connectivity", self.test_get_conversations),
            ("Create Conversation", self.test_create_conversation),
            ("Send Message & AI Response", self.test_send_message),
            ("Get Messages", self.test_get_messages),
            ("Regenerate Response", self.test_regenerate_response),
            ("Title Auto-Generation", self.test_conversation_title_generation),
            ("Database Persistence", self.test_database_persistence),
            ("Delete Conversation", self.test_delete_conversation),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"Running: {test_name}")
            if test_func():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        
        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
        return passed == total

def main():
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
