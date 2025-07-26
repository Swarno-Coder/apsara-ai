#!/usr/bin/env python3
"""
Test script to validate all backend modules functionality
"""

import sys
import os
import asyncio
import json
import numpy as np
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all modules
try:
    import config
    import audio_utils  # Import the module directly, not a class
    from emotion_classifier import EmotionClassifier
    from faiss_memory import FAISSMemoryManager
    from firebase_interface import FirebaseInterface
    from llm_openrouter import OpenRouterClient as OpenRouterLLM
    from stt_whispercpp import WhisperCPPWrapper as WhisperSTT
    from tts_piper import PiperTTSWrapper as PiperTTS
    from agent_manager import AgentManager
    from websocket_handler import WebSocketHandler
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class ModuleTester:
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
        
    def test_config(self):
        """Test configuration module"""
        try:
            # Check required config attributes
            required_attrs = [
                'OPENROUTER_API_KEY', 'FIREBASE_CONFIG_PATH', 'WHISPER_MODEL_PATH',
                'PIPER_MODEL_PATH', 'FAISS_INDEX_PATH', 'EMBEDDING_DIMENSION'
            ]
            
            missing_attrs = []
            for attr in required_attrs:
                if not hasattr(config, attr):
                    missing_attrs.append(attr)
                    
            if missing_attrs:
                self.log_result("config", "required_attributes", False, 
                              f"Missing attributes: {missing_attrs}")
            else:
                self.log_result("config", "required_attributes", True, "All required attributes present")
                
            # Test config values
            if hasattr(config, 'PORT') and isinstance(config.PORT, int):
                self.log_result("config", "port_value", True, f"Port: {config.PORT}")
            else:
                self.log_result("config", "port_value", False, "Port not properly configured")
                
        except Exception as e:
            self.log_result("config", "general", False, str(e))
            
    def test_audio_utils(self):
        """Test audio utilities"""
        try:
            # Test audio utility functions
            self.log_result("audio_utils", "module_import", True, "Audio utils module imported")
            
            # Test with dummy audio data
            dummy_audio = np.random.rand(16000).astype(np.float32)  # 1 second of audio at 16kHz
            
            # Test audio processing functions
            if hasattr(audio_utils, 'normalize_audio'):
                result = audio_utils.normalize_audio(dummy_audio)
                self.log_result("audio_utils", "normalize_audio", True, f"Normalized audio shape: {result.shape}")
            else:
                self.log_result("audio_utils", "normalize_audio", False, "normalize_audio function not found")
                
            if hasattr(audio_utils, 'convert_to_wav'):
                wav_bytes = audio_utils.convert_to_wav(dummy_audio)
                self.log_result("audio_utils", "convert_to_wav", True, f"WAV conversion successful, {len(wav_bytes)} bytes")
            else:
                self.log_result("audio_utils", "convert_to_wav", False, "convert_to_wav function not found")
                
        except Exception as e:
            self.log_result("audio_utils", "general", False, str(e))
            
    def test_emotion_classifier(self):
        """Test emotion classification"""
        try:
            classifier = EmotionClassifier()
            self.log_result("emotion_classifier", "initialization", True, "EmotionClassifier created")
            
            # Test emotion classification
            test_text = "I am feeling happy today!"
            emotion = classifier.classify_text_emotion(test_text)
            self.log_result("emotion_classifier", "classify_text_emotion", True, 
                          f"Emotion for '{test_text}': {emotion}")
            
        except Exception as e:
            self.log_result("emotion_classifier", "general", False, str(e))
            
    def test_faiss_memory(self):
        """Test FAISS memory manager"""
        try:
            memory_manager = FAISSMemoryManager()
            self.log_result("faiss_memory", "initialization", True, "FAISSMemoryManager created")
            
            # Test adding memory
            test_user_id = "test_user_123"
            test_text = "This is a test memory for FAISS"
            test_emotion = "neutral"
            
            success = memory_manager.add_memory(test_text, test_user_id, test_emotion)
            self.log_result("faiss_memory", "add_memory", success, 
                          f"Added memory: {test_text[:30]}...")
            
            # Test searching memory
            if success:
                results = memory_manager.search_memories("test memory", test_user_id, top_k=5)
                self.log_result("faiss_memory", "search_memories", len(results) > 0, 
                              f"Found {len(results)} memories")
            
            # Test user memory count
            count = memory_manager.get_user_memory_count(test_user_id)
            self.log_result("faiss_memory", "get_user_memory_count", True, 
                          f"User has {count} memories")
            
        except Exception as e:
            self.log_result("faiss_memory", "general", False, str(e))
            
    def test_firebase_interface(self):
        """Test Firebase interface"""
        try:
            # Check if Firebase config file exists
            if hasattr(config, 'FIREBASE_CONFIG_PATH') and os.path.exists(config.FIREBASE_CONFIG_PATH):
                firebase = FirebaseInterface()
                self.log_result("firebase_interface", "initialization", True, "FirebaseInterface created")
                
                # Test basic Firebase operations (without actually writing to DB)
                test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
                # Note: We won't actually write to Firebase in tests
                self.log_result("firebase_interface", "config_loaded", True, "Firebase config accessible")
            else:
                self.log_result("firebase_interface", "config_file", False, "Firebase config file not found")
                
        except Exception as e:
            self.log_result("firebase_interface", "general", False, str(e))
            
    def test_llm_openrouter(self):
        """Test OpenRouter LLM"""
        try:
            # Check if API key is configured
            if hasattr(config, 'OPENROUTER_API_KEY') and config.OPENROUTER_API_KEY:
                llm = OpenRouterLLM()
                self.log_result("llm_openrouter", "initialization", True, "OpenRouterLLM created")
                
                # Note: We won't make actual API calls in tests to avoid costs
                self.log_result("llm_openrouter", "api_key_configured", True, "API key is configured")
            else:
                self.log_result("llm_openrouter", "api_key_configured", False, "API key not configured")
                
        except Exception as e:
            self.log_result("llm_openrouter", "general", False, str(e))
            
    def test_stt_whispercpp(self):
        """Test Speech-to-Text"""
        try:
            # Check if model path exists
            if hasattr(config, 'WHISPER_MODEL_PATH'):
                stt = WhisperSTT()
                self.log_result("stt_whispercpp", "initialization", True, "WhisperSTT created")
                
                # Test with dummy audio (if transcribe method exists)
                if hasattr(stt, 'transcribe'):
                    # Note: We won't test actual transcription without a real audio file
                    self.log_result("stt_whispercpp", "transcribe_method", True, "Transcribe method available")
                else:
                    self.log_result("stt_whispercpp", "transcribe_method", False, "Transcribe method not found")
            else:
                self.log_result("stt_whispercpp", "model_path", False, "Whisper model path not configured")
                
        except Exception as e:
            self.log_result("stt_whispercpp", "general", False, str(e))
            
    def test_tts_piper(self):
        """Test Text-to-Speech"""
        try:
            # Check if model path exists
            if hasattr(config, 'PIPER_MODEL_PATH'):
                tts = PiperTTS()
                self.log_result("tts_piper", "initialization", True, "PiperTTS created")
                
                # Test with dummy text (if synthesize method exists)
                if hasattr(tts, 'synthesize'):
                    # Note: We won't test actual synthesis without proper setup
                    self.log_result("tts_piper", "synthesize_method", True, "Synthesize method available")
                else:
                    self.log_result("tts_piper", "synthesize_method", False, "Synthesize method not found")
            else:
                self.log_result("tts_piper", "model_path", False, "Piper model path not configured")
                
        except Exception as e:
            self.log_result("tts_piper", "general", False, str(e))
            
    def test_agent_manager(self):
        """Test Agent Manager"""
        try:
            agent_manager = AgentManager()
            self.log_result("agent_manager", "initialization", True, "AgentManager created")
            
            # Test agent operations
            test_agent_data = {
                "name": "Test Agent",
                "personality": "friendly",
                "voice_settings": {"speed": 1.0}
            }
            
            if hasattr(agent_manager, 'create_agent'):
                # Note: We won't actually create agents in DB during tests
                self.log_result("agent_manager", "create_agent_method", True, "Create agent method available")
            else:
                self.log_result("agent_manager", "create_agent_method", False, "Create agent method not found")
                
        except Exception as e:
            self.log_result("agent_manager", "general", False, str(e))
            
    async def test_websocket_handler(self):
        """Test WebSocket handler"""
        try:
            # Check if WebSocketHandler can be instantiated
            handler = WebSocketHandler()
            self.log_result("websocket_handler", "initialization", True, "WebSocketHandler created")
            
            # Test handler methods
            if hasattr(handler, 'handle_connection'):
                self.log_result("websocket_handler", "handle_connection_method", True, "Handle connection method available")
            else:
                self.log_result("websocket_handler", "handle_connection_method", False, "Handle connection method not found")
                
        except Exception as e:
            self.log_result("websocket_handler", "general", False, str(e))
            
    def run_all_tests(self):
        """Run all module tests"""
        print("🚀 Starting backend module tests...\n")
        
        # Run sync tests
        self.test_config()
        self.test_audio_utils()
        self.test_emotion_classifier()
        self.test_faiss_memory()
        self.test_firebase_interface()
        self.test_llm_openrouter()
        self.test_stt_whispercpp()
        self.test_tts_piper()
        self.test_agent_manager()
        
        # Run async tests
        asyncio.run(self.test_websocket_handler())
        
        # Print summary
        self.print_summary()
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
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
        with open("test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("Detailed results saved to test_results.json")

if __name__ == "__main__":
    tester = ModuleTester()
    tester.run_all_tests()
