import requests
import sys
import json
from datetime import datetime
import tempfile
import os

class VoiceAssistantAPITester:
    def __init__(self, base_url="https://37d0552e-fc3b-4a7c-8adb-d3d1e3047cf3.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_email = f"test_user_{datetime.now().strftime('%H%M%S')}@test.com"
        self.user_password = "TestPass123!"
        self.username = f"testuser_{datetime.now().strftime('%H%M%S')}"

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    # Remove Content-Type for file uploads
                    headers.pop('Content-Type', None)
                    response = requests.post(url, files=files, headers=headers, params=params)
                else:
                    response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:300]}...")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_supported_languages(self):
        """Test supported languages endpoint"""
        return self.run_test("Supported Languages", "GET", "supported-languages", 200)

    def test_user_registration(self):
        """Test user registration"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "register",
            200,
            data={
                "username": self.username,
                "email": self.user_email,
                "password": self.user_password
            }
        )
        return success

    def test_user_login(self):
        """Test user login and get token"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "login",
            200,
            data={
                "email": self.user_email,
                "password": self.user_password
            }
        )
        if success and isinstance(response, dict) and 'access_token' in response:
            self.token = response['access_token']
            print(f"   Token obtained: {self.token[:20]}...")
            return True
        return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "login",
            401,
            data={
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
        )
        return success

    def test_protected_route(self):
        """Test protected route with valid token"""
        return self.run_test("Protected Route", "GET", "protected", 200)

    def test_protected_route_without_token(self):
        """Test protected route without token"""
        # Temporarily remove token
        temp_token = self.token
        self.token = None
        success, response = self.run_test("Protected Route (No Token)", "GET", "protected", 403)
        self.token = temp_token  # Restore token
        return success

    def test_process_voice_command(self):
        """Test voice command processing"""
        test_cases = [
            {
                "name": "Time Query",
                "text": "What time is it?",
                "detected_language": "en",
                "target_language": "en"
            },
            {
                "name": "Joke Request",
                "text": "Tell me a joke",
                "detected_language": "en",
                "target_language": "en"
            },
            {
                "name": "Greeting",
                "text": "Hello",
                "detected_language": "en",
                "target_language": "hi"
            },
            {
                "name": "Translation Request",
                "text": "translate this text",
                "detected_language": "en",
                "target_language": "te"
            }
        ]

        all_passed = True
        for case in test_cases:
            success, response = self.run_test(
                f"Process Voice - {case['name']}",
                "POST",
                "process-voice",
                200,
                params={
                    "transcribed_text": case["text"],
                    "detected_language": case["detected_language"],
                    "target_language": case["target_language"]
                }
            )
            if not success:
                all_passed = False
            
        return all_passed

    def test_translation(self):
        """Test text translation"""
        test_cases = [
            {"text": "Hello, how are you?", "target_language": "hi"},
            {"text": "Good morning", "target_language": "te"},
            {"text": "Thank you", "target_language": "ta"}
        ]

        all_passed = True
        for case in test_cases:
            success, response = self.run_test(
                f"Translation to {case['target_language']}",
                "POST",
                "translate",
                200,
                data=case
            )
            if not success:
                all_passed = False
                
        return all_passed

    def test_command_history(self):
        """Test command history retrieval"""
        return self.run_test("Command History", "GET", "command-history", 200)

    def test_text_to_speech(self):
        """Test text-to-speech conversion"""
        success, response = self.run_test(
            "Text-to-Speech",
            "POST",
            "text-to-speech",
            200,
            params={
                "text": "Hello, this is a test",
                "language": "en"
            }
        )
        return success

    def test_duplicate_registration(self):
        """Test duplicate user registration"""
        success, response = self.run_test(
            "Duplicate Registration",
            "POST",
            "register",
            400,
            data={
                "username": self.username,
                "email": self.user_email,
                "password": self.user_password
            }
        )
        return success

def main():
    print("🚀 Starting Multilingual Voice Assistant API Tests")
    print("=" * 60)
    
    tester = VoiceAssistantAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Supported Languages", tester.test_supported_languages),
        ("User Registration", tester.test_user_registration),
        ("Duplicate Registration", tester.test_duplicate_registration),
        ("User Login", tester.test_user_login),
        ("Invalid Login", tester.test_invalid_login),
        ("Protected Route", tester.test_protected_route),
        ("Protected Route (No Token)", tester.test_protected_route_without_token),
        ("Voice Command Processing", tester.test_process_voice_command),
        ("Translation", tester.test_translation),
        ("Text-to-Speech", tester.test_text_to_speech),
        ("Command History", tester.test_command_history),
    ]

    print(f"\n📋 Running {len(tests)} test categories...")
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test category '{test_name}' failed with error: {str(e)}")

    # Print final results
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())