import numpy as np
import onnxruntime as ort
from typing import List, Dict
import re
import config

class EmotionClassifier:
    def __init__(self, model_path: str = config.EMOTION_MODEL_PATH):
        self.model_path = model_path
        self.emotion_labels = config.EMOTION_LABELS
        self.session = None
        self._load_model()
    
    def _load_model(self):
        """Load ONNX emotion classification model"""
        try:
            if self.model_path and self.model_path.endswith('.onnx'):
                self.session = ort.InferenceSession(self.model_path)
                print(f"Loaded emotion model from {self.model_path}")
            else:
                print("No ONNX model found, using rule-based classification")
        except Exception as e:
            print(f"Failed to load emotion model: {e}")
            self.session = None
    
    def classify_text_emotion(self, text: str) -> Dict[str, float]:
        """Classify emotion from text using rules or model"""
        if self.session:
            return self._classify_with_model(text)
        else:
            return self._classify_with_rules(text)
    
    def _classify_with_model(self, text: str) -> Dict[str, float]:
        """Use ONNX model for emotion classification"""
        try:
            # This is a placeholder - actual implementation would depend on model format
            # For now, return neutral emotion
            emotions = {label: 0.0 for label in self.emotion_labels}
            emotions["neutral"] = 1.0
            return emotions
        except Exception as e:
            print(f"Model classification error: {e}")
            return self._classify_with_rules(text)
    
    def _classify_with_rules(self, text: str) -> Dict[str, float]:
        """Rule-based emotion classification"""
        text_lower = text.lower()
        emotions = {label: 0.0 for label in self.emotion_labels}
        
        # Happy keywords
        happy_words = ["happy", "joy", "excited", "great", "awesome", "wonderful", "amazing", "love", "smile", "laugh"]
        if any(word in text_lower for word in happy_words):
            emotions["happy"] = 0.8
            return emotions
        
        # Sad keywords
        sad_words = ["sad", "depressed", "down", "upset", "cry", "terrible", "awful", "bad", "sorry"]
        if any(word in text_lower for word in sad_words):
            emotions["sad"] = 0.7
            return emotions
        
        # Angry keywords
        angry_words = ["angry", "mad", "furious", "hate", "stupid", "annoying", "frustrated"]
        if any(word in text_lower for word in angry_words):
            emotions["angry"] = 0.7
            return emotions
        
        # Fear keywords
        fear_words = ["scared", "afraid", "fear", "worried", "anxious", "nervous"]
        if any(word in text_lower for word in fear_words):
            emotions["fear"] = 0.6
            return emotions
        
        # Surprise keywords
        surprise_words = ["wow", "amazing", "incredible", "unbelievable", "shocking"]
        if any(word in text_lower for word in surprise_words):
            emotions["surprise"] = 0.6
            return emotions
        
        # Default to neutral
        emotions["neutral"] = 1.0
        return emotions
    
    def classify_audio_emotion(self, audio_features: np.ndarray) -> Dict[str, float]:
        """Classify emotion from audio features"""
        # Placeholder for audio-based emotion classification
        # Would require audio feature extraction (MFCC, etc.)
        emotions = {label: 0.0 for label in self.emotion_labels}
        emotions["neutral"] = 1.0
        return emotions
    
    def get_dominant_emotion(self, emotions: Dict[str, float]) -> str:
        """Get the emotion with highest confidence"""
        return max(emotions.items(), key=lambda x: x[1])[0]

# Global instance
emotion_classifier = EmotionClassifier()
