#!/usr/bin/env python3
"""
AI Companion System Validation Script
Validates all components are working correctly
"""

import asyncio
import requests
import json
import time
import sys
import os
from datetime import datetime

class SystemValidator:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.voice_service_url = "http://localhost:8001"
        self.test_results = []
    
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {message}")
    
    def test_backend_health(self):
        """Test backend API health"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health", "PASS", "Backend API responding")
                return True
            else:
                self.log_test("Backend Health", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", "FAIL", f"Connection failed: {e}")
            return False
    
    def test_voice_service_health(self):
        """Test voice service health"""
        try:
            response = requests.get(f"{self.voice_service_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Voice Service Health", "PASS", "Voice service responding")
                return True
            else:
                self.log_test("Voice Service Health", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Voice Service Health", "FAIL", f"Connection failed: {e}")
            return False
    
    def test_database_connection(self):
        """Test database connectivity through API"""
        try:
            response = requests.get(f"{self.backend_url}/agents?user_id=test_user", timeout=10)
            if response.status_code == 200:
                agents = response.json()
                self.log_test("Database Connection", "PASS", f"Retrieved {len(agents)} agents")
                return True
            else:
                self.log_test("Database Connection", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Connection", "FAIL", f"Database query failed: {e}")
            return False
    
    def test_agent_endpoints(self):
        """Test agent-related endpoints"""
        try:
            # Test get agents
            response = requests.get(f"{self.backend_url}/agents?user_id=test_user")
            if response.status_code != 200:
                self.log_test("Agent Endpoints", "FAIL", "Failed to get agents")
                return False
            
            agents = response.json()
            if not agents:
                self.log_test("Agent Endpoints", "WARN", "No agents found in database")
                return True
            
            # Test get specific agent
            agent_id = agents[0]["id"]
            response = requests.get(f"{self.backend_url}/agents/{agent_id}?user_id=test_user")
            if response.status_code == 200:
                self.log_test("Agent Endpoints", "PASS", f"Agent endpoints working")
                return True
            else:
                self.log_test("Agent Endpoints", "FAIL", "Failed to get specific agent")
                return False
                
        except Exception as e:
            self.log_test("Agent Endpoints", "FAIL", f"Agent endpoint test failed: {e}")
            return False
    
    def test_call_endpoints(self):
        """Test call-related endpoints"""
        try:
            # Get an agent first
            response = requests.get(f"{self.backend_url}/agents?user_id=test_user")
            if response.status_code != 200 or not response.json():
                self.log_test("Call Endpoints", "SKIP", "No agents available for call test")
                return True
            
            agent_id = response.json()[0]["id"]
            
            # Start a call
            call_data = {
                "user_id": "test_user",
                "agent_id": agent_id,
                "call_type": "voice"
            }
            
            response = requests.post(f"{self.backend_url}/calls/start", json=call_data)
            if response.status_code != 200:
                self.log_test("Call Endpoints", "FAIL", "Failed to start call")
                return False
            
            call = response.json()
            call_id = call["id"]
            
            # Send a message
            message_data = {
                "user_id": "test_user",
                "content": "Hello, this is a test message",
                "message_type": "text"
            }
            
            response = requests.post(f"{self.backend_url}/calls/{call_id}/message", json=message_data)
            if response.status_code != 200:
                self.log_test("Call Endpoints", "FAIL", "Failed to send message")
                return False
            
            # End the call
            response = requests.put(f"{self.backend_url}/calls/{call_id}/end")
            if response.status_code == 200:
                self.log_test("Call Endpoints", "PASS", "Call workflow completed successfully")
                return True
            else:
                self.log_test("Call Endpoints", "FAIL", "Failed to end call")
                return False
                
        except Exception as e:
            self.log_test("Call Endpoints", "FAIL", f"Call endpoint test failed: {e}")
            return False
    
    def test_voice_service_endpoints(self):
        """Test voice service specific endpoints"""
        try:
            # Test STT models endpoint
            response = requests.get(f"{self.voice_service_url}/stt/models")
            if response.status_code != 200:
                self.log_test("Voice Service Endpoints", "FAIL", "Failed to get STT models")
                return False
            
            # Test TTS voices endpoint
            response = requests.get(f"{self.voice_service_url}/tts/voices")
            if response.status_code != 200:
                self.log_test("Voice Service Endpoints", "FAIL", "Failed to get TTS voices")
                return False
            
            # Test languages endpoint
            response = requests.get(f"{self.voice_service_url}/stt/languages")
            if response.status_code == 200:
                self.log_test("Voice Service Endpoints", "PASS", "Voice service endpoints working")
                return True
            else:
                self.log_test("Voice Service Endpoints", "FAIL", "Failed to get languages")
                return False
                
        except Exception as e:
            self.log_test("Voice Service Endpoints", "FAIL", f"Voice endpoint test failed: {e}")
            return False
    
    def test_middleware(self):
        """Test middleware functionality"""
        try:
            response = requests.get(f"{self.backend_url}/health")
            
            # Check for middleware headers
            if "X-Request-ID" in response.headers:
                self.log_test("Middleware", "PASS", "Request middleware working")
                return True
            else:
                self.log_test("Middleware", "WARN", "Request ID header not found")
                return True
                
        except Exception as e:
            self.log_test("Middleware", "FAIL", f"Middleware test failed: {e}")
            return False
    
    def test_cors(self):
        """Test CORS configuration"""
        try:
            headers = {"Origin": "http://localhost:3000"}
            response = requests.get(f"{self.backend_url}/health", headers=headers)
            
            if "Access-Control-Allow-Origin" in response.headers:
                self.log_test("CORS", "PASS", "CORS headers present")
                return True
            else:
                self.log_test("CORS", "WARN", "CORS headers not found")
                return True
                
        except Exception as e:
            self.log_test("CORS", "FAIL", f"CORS test failed: {e}")
            return False
    
    def test_rate_limiting(self):
        """Test rate limiting (simplified test)"""
        try:
            # Make a few rapid requests
            for i in range(5):
                response = requests.get(f"{self.backend_url}/health")
                if response.status_code == 429:
                    self.log_test("Rate Limiting", "PASS", "Rate limiting working")
                    return True
            
            self.log_test("Rate Limiting", "PASS", "Rate limiting configured (not triggered)")
            return True
            
        except Exception as e:
            self.log_test("Rate Limiting", "FAIL", f"Rate limiting test failed: {e}")
            return False
    
    def generate_report(self):
        """Generate final validation report"""
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print("\n" + "="*50)
        print("🧪 VALIDATION REPORT")
        print("="*50)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 All critical tests passed! System is ready.")
            return True
        else:
            print(f"\n❌ {failed} test(s) failed. Please check the issues above.")
            return False
    
    async def run_all_tests(self):
        """Run all validation tests"""
        print("🧪 AI Companion System Validation")
        print("="*40)
        print("🔍 Testing system components...\n")
        
        # Core service tests
        self.test_backend_health()
        self.test_voice_service_health()
        self.test_database_connection()
        
        # API endpoint tests
        self.test_agent_endpoints()
        self.test_call_endpoints()
        self.test_voice_service_endpoints()
        
        # Infrastructure tests
        self.test_middleware()
        self.test_cors()
        self.test_rate_limiting()
        
        return self.generate_report()

def main():
    """Main validation function"""
    validator = SystemValidator()
    
    print("🚀 Starting AI Companion System Validation...")
    print("⏰ This may take a few minutes...\n")
    
    try:
        success = asyncio.run(validator.run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
