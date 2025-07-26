#!/usr/bin/env python3
"""
Test script to validate WebSocket and API endpoints
"""

import asyncio
import websockets
import aiohttp
import json
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import config
    print("✅ Config module imported successfully")
except Exception as e:
    print(f"❌ Config import error: {e}")
    sys.exit(1)

class APITester:
    def __init__(self, host="localhost", port=None):
        self.host = host
        self.port = port or getattr(config, 'PORT', 8000)
        self.base_url = f"http://{self.host}:{self.port}"
        self.ws_url = f"ws://{self.host}:{self.port}/ws"
        self.results = []
        
    def log_result(self, test_name, success, message="", data=None):
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
    async def test_server_running(self):
        """Test if the server is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/") as response:
                    if response.status == 200:
                        text = await response.text()
                        self.log_result("server_health", True, f"Server is running (status: {response.status})", {"response": text[:100]})
                    else:
                        self.log_result("server_health", False, f"Server returned status: {response.status}")
        except aiohttp.ClientConnectorError:
            self.log_result("server_health", False, "Cannot connect to server - is it running?")
        except Exception as e:
            self.log_result("server_health", False, f"Server test error: {e}")
            
    async def test_api_endpoints(self):
        """Test various API endpoints"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                try:
                    async with session.get(f"{self.base_url}/health") as response:
                        if response.status == 200:
                            data = await response.json()
                            self.log_result("api_health", True, "Health endpoint working", data)
                        else:
                            self.log_result("api_health", False, f"Health endpoint status: {response.status}")
                except Exception as e:
                    self.log_result("api_health", False, f"Health endpoint error: {e}")
                
                # Test agents endpoint
                try:
                    async with session.get(f"{self.base_url}/agents") as response:
                        if response.status in [200, 404]:  # 404 is ok if no agents exist
                            data = await response.json() if response.content_type == 'application/json' else await response.text()
                            self.log_result("api_agents_get", True, f"Agents GET endpoint working (status: {response.status})", {"response": str(data)[:100]})
                        else:
                            self.log_result("api_agents_get", False, f"Agents GET status: {response.status}")
                except Exception as e:
                    self.log_result("api_agents_get", False, f"Agents GET error: {e}")
                
                # Test create agent endpoint
                test_agent = {
                    "name": "Test Agent",
                    "personality": "friendly and helpful",
                    "voice_settings": {
                        "speed": 1.0,
                        "pitch": 1.0
                    }
                }
                
                try:
                    async with session.post(f"{self.base_url}/agents", json=test_agent) as response:
                        if response.status in [200, 201, 400, 422]:  # Accept various response codes
                            data = await response.json() if response.content_type == 'application/json' else await response.text()
                            self.log_result("api_agents_post", True, f"Agents POST endpoint working (status: {response.status})", {"response": str(data)[:100]})
                        else:
                            self.log_result("api_agents_post", False, f"Agents POST status: {response.status}")
                except Exception as e:
                    self.log_result("api_agents_post", False, f"Agents POST error: {e}")
                
                # Test chat endpoint
                test_chat = {
                    "message": "Hello, this is a test message",
                    "user_id": "test_user_123",
                    "agent_id": "test_agent_456"
                }
                
                try:
                    async with session.post(f"{self.base_url}/chat", json=test_chat) as response:
                        if response.status in [200, 400, 422]:  # Accept various response codes
                            data = await response.json() if response.content_type == 'application/json' else await response.text()
                            self.log_result("api_chat_post", True, f"Chat POST endpoint working (status: {response.status})", {"response": str(data)[:100]})
                        else:
                            self.log_result("api_chat_post", False, f"Chat POST status: {response.status}")
                except Exception as e:
                    self.log_result("api_chat_post", False, f"Chat POST error: {e}")
                    
        except Exception as e:
            self.log_result("api_endpoints", False, f"API endpoints test error: {e}")
            
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        try:
            # Test basic WebSocket connection
            async with websockets.connect(self.ws_url, ping_timeout=10, close_timeout=10) as websocket:
                self.log_result("websocket_connection", True, "WebSocket connection established")
                
                # Test sending a message
                test_message = {
                    "type": "test",
                    "data": "Hello WebSocket!",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                self.log_result("websocket_send", True, "Message sent to WebSocket")
                
                # Try to receive a response (with timeout)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    self.log_result("websocket_receive", True, "Received WebSocket response", {"response": str(response_data)[:100]})
                except asyncio.TimeoutError:
                    self.log_result("websocket_receive", False, "WebSocket response timeout")
                except json.JSONDecodeError:
                    self.log_result("websocket_receive", False, "Invalid JSON response from WebSocket")
                    
        except websockets.exceptions.ConnectionRefused:
            self.log_result("websocket_connection", False, "WebSocket connection refused - is server running?")
        except Exception as e:
            self.log_result("websocket_connection", False, f"WebSocket error: {e}")
            
    async def test_websocket_chat(self):
        """Test WebSocket chat functionality"""
        try:
            async with websockets.connect(self.ws_url, ping_timeout=10, close_timeout=10) as websocket:
                # Test chat message
                chat_message = {
                    "type": "chat",
                    "message": "Hello, how are you?",
                    "user_id": "test_user_123",
                    "agent_id": "test_agent_456",
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(chat_message))
                self.log_result("websocket_chat_send", True, "Chat message sent via WebSocket")
                
                # Try to receive chat response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    response_data = json.loads(response)
                    self.log_result("websocket_chat_receive", True, "Received chat response", {"response": str(response_data)[:100]})
                except asyncio.TimeoutError:
                    self.log_result("websocket_chat_receive", False, "Chat response timeout")
                except json.JSONDecodeError:
                    self.log_result("websocket_chat_receive", False, "Invalid JSON in chat response")
                    
        except Exception as e:
            self.log_result("websocket_chat", False, f"WebSocket chat error: {e}")
            
    async def test_websocket_audio(self):
        """Test WebSocket audio functionality"""
        try:
            async with websockets.connect(self.ws_url, ping_timeout=10, close_timeout=10) as websocket:
                # Test audio message (with dummy audio data)
                import base64
                import numpy as np
                
                # Create dummy audio data
                dummy_audio = np.random.rand(16000).astype(np.float32)  # 1 second of random audio
                audio_bytes = dummy_audio.tobytes()
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                audio_message = {
                    "type": "audio",
                    "audio_data": audio_b64,
                    "user_id": "test_user_123",
                    "agent_id": "test_agent_456",
                    "format": "float32",
                    "sample_rate": 16000,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(audio_message))
                self.log_result("websocket_audio_send", True, "Audio message sent via WebSocket")
                
                # Try to receive audio response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                    response_data = json.loads(response)
                    self.log_result("websocket_audio_receive", True, "Received audio response", {"response": str(response_data)[:100]})
                except asyncio.TimeoutError:
                    self.log_result("websocket_audio_receive", False, "Audio response timeout")
                except json.JSONDecodeError:
                    self.log_result("websocket_audio_receive", False, "Invalid JSON in audio response")
                    
        except Exception as e:
            self.log_result("websocket_audio", False, f"WebSocket audio error: {e}")
            
    async def run_all_tests(self):
        """Run all API and WebSocket tests"""
        print("🚀 Starting API and WebSocket tests...\n")
        print(f"Testing server at: {self.base_url}")
        print(f"Testing WebSocket at: {self.ws_url}\n")
        
        # Test server health first
        await self.test_server_running()
        
        # Test API endpoints
        await self.test_api_endpoints()
        
        # Test WebSocket functionality
        await self.test_websocket_connection()
        await self.test_websocket_chat()
        await self.test_websocket_audio()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("API & WEBSOCKET TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*60)
        
        # Save detailed results
        with open("api_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("Detailed results saved to api_test_results.json")

async def main():
    """Main test function"""
    tester = APITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
