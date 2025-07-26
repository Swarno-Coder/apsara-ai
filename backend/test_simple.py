#!/usr/bin/env python3
"""
Simplified test script to validate backend modules one by one
"""

import sys
import os
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SimpleModuleTester:
    def __init__(self):
        self.results = []
        
    def log_result(self, module_name, test_name, success, message=""):
        result = {
            "module": module_name,
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {module_name}.{test_name}: {message}")
        
    def test_basic_imports(self):
        """Test basic module imports"""
        modules_to_test = [
            'config',
            'audio_utils',
            'emotion_classifier',
            'firebase_interface',
            'llm_openrouter',
            'stt_whispercpp',
            'tts_piper',
            'agent_manager',
            'websocket_handler'
        ]
        
        for module_name in modules_to_test:
            try:
                module = __import__(module_name)
                self.log_result(module_name, "import", True, "Module imported successfully")
            except Exception as e:
                self.log_result(module_name, "import", False, f"Import failed: {e}")
    
    def test_config_module(self):
        """Test config module specifically"""
        try:
            import config
            
            # Check required attributes
            required_attrs = [
                'HOST', 'PORT', 'OPENROUTER_API_KEY', 'FIREBASE_CONFIG_PATH',
                'SAMPLE_RATE', 'MODELS_DIR', 'FAISS_INDEX_PATH', 'EMBEDDING_DIMENSION'
            ]
            
            missing = []
            for attr in required_attrs:
                if not hasattr(config, attr):
                    missing.append(attr)
            
            if missing:
                self.log_result("config", "attributes", False, f"Missing: {missing}")
            else:
                self.log_result("config", "attributes", True, "All required attributes present")
                
            # Test some values
            self.log_result("config", "port", True, f"Port: {config.PORT}")
            self.log_result("config", "sample_rate", True, f"Sample rate: {config.SAMPLE_RATE}")
            
        except Exception as e:
            self.log_result("config", "general", False, str(e))
    
    def test_audio_utils_module(self):
        """Test audio utils module"""
        try:
            import audio_utils
            import numpy as np
            
            # Test normalize_audio function
            if hasattr(audio_utils, 'normalize_audio'):
                dummy_audio = np.random.rand(1000).astype(np.float32)
                normalized = audio_utils.normalize_audio(dummy_audio)
                self.log_result("audio_utils", "normalize_audio", True, 
                              f"Normalized audio shape: {normalized.shape}")
            else:
                self.log_result("audio_utils", "normalize_audio", False, "Function not found")
                
            # Test convert_to_wav function
            if hasattr(audio_utils, 'convert_to_wav'):
                dummy_audio = np.random.rand(1000).astype(np.float32)
                wav_bytes = audio_utils.convert_to_wav(dummy_audio)
                self.log_result("audio_utils", "convert_to_wav", True, 
                              f"WAV conversion: {len(wav_bytes)} bytes")
            else:
                self.log_result("audio_utils", "convert_to_wav", False, "Function not found")
                
        except Exception as e:
            self.log_result("audio_utils", "general", False, str(e))
    
    def test_emotion_classifier(self):
        """Test emotion classifier"""
        try:
            from emotion_classifier import EmotionClassifier
            
            classifier = EmotionClassifier()
            self.log_result("emotion_classifier", "init", True, "EmotionClassifier created")
            
            # Test text emotion classification
            if hasattr(classifier, 'classify_text_emotion'):
                emotion = classifier.classify_text_emotion("I am happy today!")
                self.log_result("emotion_classifier", "classify_text", True, 
                              f"Emotion result: {emotion}")
            else:
                self.log_result("emotion_classifier", "classify_text", False, "Method not found")
                
        except Exception as e:
            self.log_result("emotion_classifier", "general", False, str(e))
    
    def test_llm_openrouter(self):
        """Test OpenRouter LLM"""
        try:
            from llm_openrouter import OpenRouterClient
            
            llm = OpenRouterClient()
            self.log_result("llm_openrouter", "init", True, "OpenRouterClient created")
            
            # Check if API key is configured
            import config
            if hasattr(config, 'OPENROUTER_API_KEY') and config.OPENROUTER_API_KEY:
                self.log_result("llm_openrouter", "api_key", True, "API key configured")
            else:
                self.log_result("llm_openrouter", "api_key", False, "API key not configured")
                
        except Exception as e:
            self.log_result("llm_openrouter", "general", False, str(e))
    
    def test_firebase_interface(self):
        """Test Firebase interface"""
        try:
            from firebase_interface import FirebaseInterface
            
            firebase = FirebaseInterface()
            self.log_result("firebase_interface", "init", True, "FirebaseInterface created")
            
        except Exception as e:
            self.log_result("firebase_interface", "general", False, str(e))
    
    def test_agent_manager(self):
        """Test Agent Manager"""
        try:
            from agent_manager import AgentManager
            
            agent_manager = AgentManager()
            self.log_result("agent_manager", "init", True, "AgentManager created")
            
        except Exception as e:
            self.log_result("agent_manager", "general", False, str(e))
    
    def test_websocket_handler(self):
        """Test WebSocket handler"""
        try:
            from websocket_handler import WebSocketHandler
            
            handler = WebSocketHandler()
            self.log_result("websocket_handler", "init", True, "WebSocketHandler created")
            
        except Exception as e:
            self.log_result("websocket_handler", "general", False, str(e))
    
    def test_faiss_memory_simple(self):
        """Test FAISS memory with simple import"""
        try:
            print("Testing FAISS memory import...")
            from faiss_memory import FAISSMemoryManager
            
            self.log_result("faiss_memory", "import", True, "FAISSMemoryManager imported")
            
            # Try to create instance
            memory = FAISSMemoryManager()
            self.log_result("faiss_memory", "init", True, "FAISSMemoryManager created")
            
        except Exception as e:
            self.log_result("faiss_memory", "general", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting simplified backend tests...\n")
        
        # Test basic imports first
        self.test_basic_imports()
        print()
        
        # Test each module individually
        self.test_config_module()
        self.test_audio_utils_module()
        self.test_emotion_classifier()
        self.test_llm_openrouter()
        self.test_firebase_interface()
        self.test_agent_manager()
        self.test_websocket_handler()
        
        # Test FAISS last (most likely to have issues)
        print("\n--- Testing FAISS Memory (may take longer) ---")
        self.test_faiss_memory_simple()
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("SIMPLIFIED TEST SUMMARY")
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
                    print(f"  - {result['module']}.{result['test']}: {result['message']}")
        
        print("\n" + "="*60)
        
        # Save detailed results
        with open("simple_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("Detailed results saved to simple_test_results.json")

if __name__ == "__main__":
    tester = SimpleModuleTester()
    tester.run_all_tests()
