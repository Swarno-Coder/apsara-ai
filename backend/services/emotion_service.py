import logging
from typing import Optional
from models.schemas import EmotionType

logger = logging.getLogger(__name__)

class EmotionService:
    def __init__(self):
        """Initialize emotion analysis service"""
        # Simple keyword-based emotion detection
        self.emotion_keywords = {
            EmotionType.HAPPY: ["happy", "joy", "excited", "great", "wonderful", "amazing", "love", "awesome"],
            EmotionType.SAD: ["sad", "depressed", "down", "upset", "crying", "hurt", "disappointed"],
            EmotionType.ANGRY: ["angry", "mad", "furious", "annoyed", "frustrated", "irritated"],
            EmotionType.EXCITED: ["excited", "thrilled", "amazing", "wow", "fantastic", "incredible"],
            EmotionType.CALM: ["calm", "peaceful", "relaxed", "serene", "quiet", "still"],
            EmotionType.ANXIOUS: ["anxious", "worried", "nervous", "scared", "afraid", "stress"],
            EmotionType.ROMANTIC: ["love", "romantic", "kiss", "heart", "romance", "date"],
            EmotionType.PLAYFUL: ["fun", "play", "joke", "funny", "laugh", "silly"],
            EmotionType.SUPPORTIVE: ["help", "support", "care", "comfort", "understand"]
        }
    
    async def analyze_emotion(self, text: str) -> EmotionType:
        """Analyze emotion from text using keyword matching"""
        if not text:
            return EmotionType.NEUTRAL
        
        text_lower = text.lower()
        emotion_scores = {}
        
        # Score emotions based on keyword presence
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                emotion_scores[emotion] = score
        
        # Return emotion with highest score, or neutral if none found
        if emotion_scores:
            best_emotion = EmotionType.NEUTRAL
            best_score = 0
            for emotion, score in emotion_scores.items():
                if score > best_score:
                    best_score = score
                    best_emotion = emotion
            return best_emotion
        
        return EmotionType.NEUTRAL
