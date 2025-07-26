import google.generativeai as genai
import os
import logging
from typing import List, Optional, Dict
import json
from datetime import datetime
import asyncio
import time
from functools import lru_cache
import hashlib

from models.schemas import EmotionType
from database.database import Database
import dotenv

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        self.has_api_key = bool(api_key)
        
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables - using fallback responses")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            # Initialize model with faster configuration
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Optimized settings for speed and natural conversation
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,  # Slightly lower for consistency
            top_p=0.9,
            top_k=30,  # Reduced for faster generation
            max_output_tokens=200,  # Much shorter for conversation
            candidate_count=1,  # Only generate one candidate
        )
        
        # Response cache for common patterns
        self._response_cache = {}
        self._cache_max_size = 100
        
        # Preloaded conversation starters
        self._conversation_starters = []
    
    async def generate_response(self, user_message: str, agent_id: str, agent_prompt: str, 
                              context: List[dict], user_emotion: EmotionType, user_id: str) -> str:
        """Generate fast, conversational response from agent"""
        try:
            # If no API key, use fallback immediately
            if not self.has_api_key or self.model is None:
                logger.info("Using fallback response (no API key)")
                return self._get_smart_fallback(user_message, user_emotion, agent_prompt)
            
            # Start timing for performance monitoring
            start_time = time.time()
            
            # Check cache first for common responses
            cache_key = self._generate_cache_key(user_message, agent_id, user_emotion)
            if cache_key in self._response_cache:
                logger.info(f"Cache hit for response generation")
                return self._response_cache[cache_key]
            
            # Build simplified, faster prompt
            recent_context = self._build_minimal_context(context, limit=3)
            emotion_hint = self._get_quick_emotion_hint(user_emotion)
            
            # Create streamlined prompt for faster processing
            prompt = f"""You are {self._extract_agent_name(agent_prompt)}. Be conversational, warm, and genuine.

Recent chat:
{recent_context}

User feels: {emotion_hint}
User says: "{user_message}"

Respond naturally in 1-2 sentences like a close friend:"""

            # Generate response with timeout
            response_task = asyncio.create_task(self._generate_with_timeout(prompt))
            response = await response_task
            
            if response and response.text:
                cleaned_response = self._clean_response(response.text)
                
                # Cache successful responses
                self._cache_response(cache_key, cleaned_response)
                
                # Log performance
                generation_time = time.time() - start_time
                logger.info(f"Response generated in {generation_time:.2f}s")
                
                return cleaned_response
            else:
                return self._get_quick_fallback(user_emotion)
                
        except asyncio.TimeoutError:
            logger.warning("LLM response timeout, using fallback")
            return self._get_quick_fallback(user_emotion)
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._get_quick_fallback(user_emotion)
    
    async def _generate_with_timeout(self, prompt: str, timeout: float = 3.0):
        """Generate response with timeout for better user experience"""
        if not self.has_api_key or self.model is None:
            raise Exception("No API key available")
            
        try:
            # Run generation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def generate_content():
                if self.model is None:
                    raise Exception("Model is not initialized")
                return self.model.generate_content(prompt, generation_config=self.generation_config)
            
            response = await asyncio.wait_for(
                loop.run_in_executor(None, generate_content),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            raise
    
    async def generate_greeting(self, agent_id: str, user_id: str, agent_name: str, personality: str) -> str:
        """Generate fast, personalized greeting"""
        try:
            # Use cached greetings for speed
            time_of_day = self._get_time_of_day()
            
            # Quick greeting templates based on personality
            greeting_templates = {
                'romantic': f"Hey beautiful! I've been thinking about you. How was your {time_of_day}?",
                'playful': f"Well well, look who decided to call! Miss me? 😉",
                'supportive': f"Hi there! I'm so glad you reached out. How are you feeling today?",
                'intellectual': f"Hello! I was just reading something fascinating. How has your {time_of_day} been?",
                'mysterious': f"You have perfect timing... I was just thinking about you. What brings you to me?",
                'caring': f"Hey sweetie! It's so good to hear from you. How are you doing?",
                'default': f"Hi! I'm {agent_name}. I'm really happy you called - I've been looking forward to talking with you!"
            }
            
            # Get appropriate greeting based on personality
            personality_key = personality.lower()
            greeting = greeting_templates.get(personality_key, greeting_templates['default'])
            
            return greeting
                
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return f"Hi! I'm {agent_name}. Great to meet you!"
    
    def _build_conversation_context(self, context: List[dict]) -> str:
        """Build conversation history string (legacy method for compatibility)"""
        return self._build_minimal_context(context, limit=5)
    
    def _build_minimal_context(self, context: List[dict], limit: int = 3) -> str:
        """Build minimal conversation context for faster processing"""
        if not context:
            return "Starting conversation."
        
        context_lines = []
        for entry in context[-limit:]:  # Last few exchanges only
            user_msg = entry.get('user_message', '')[:100]  # Truncate long messages
            agent_msg = entry.get('agent_response', '')[:100]
            if user_msg:
                context_lines.append(f"You: {user_msg}")
            if agent_msg:
                context_lines.append(f"Me: {agent_msg}")
        
        return "\n".join(context_lines[-6:])  # Keep only last 6 lines
    
    def _generate_cache_key(self, user_message: str, agent_id: str, emotion: EmotionType) -> str:
        """Generate cache key for response caching"""
        # Create hash of key components
        key_data = f"{user_message[:50]}{agent_id}{emotion.value}".lower()
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response with size limit"""
        if len(self._response_cache) >= self._cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._response_cache))
            del self._response_cache[oldest_key]
        
        self._response_cache[cache_key] = response
    
    def _extract_agent_name(self, agent_prompt: str) -> str:
        """Extract agent name from system prompt"""
        # Simple extraction - look for name patterns
        if "name is" in agent_prompt.lower():
            start = agent_prompt.lower().find("name is") + 8
            end = agent_prompt.find(".", start)
            if end == -1:
                end = start + 30
            return agent_prompt[start:end].strip()
        elif "I'm" in agent_prompt:
            start = agent_prompt.find("I'm") + 4
            end = agent_prompt.find(".", start)
            if end == -1:
                end = start + 20
            return agent_prompt[start:end].strip()
        else:
            return "your AI companion"
    
    def _get_quick_emotion_hint(self, emotion: EmotionType) -> str:
        """Get quick emotion hint for prompt"""
        emotion_hints = {
            EmotionType.HAPPY: "cheerful",
            EmotionType.SAD: "down",
            EmotionType.ANGRY: "frustrated",
            EmotionType.EXCITED: "energetic",
            EmotionType.CALM: "peaceful",
            EmotionType.ANXIOUS: "worried",
            EmotionType.ROMANTIC: "affectionate",
            EmotionType.PLAYFUL: "fun",
            EmotionType.SUPPORTIVE: "supportive",
            EmotionType.NEUTRAL: "neutral"
        }
        return emotion_hints.get(emotion, "neutral")
    
    def _get_smart_fallback(self, user_message: str, emotion: EmotionType, agent_prompt: str) -> str:
        """Get smarter fallback response based on user message and agent personality"""
        user_msg_lower = user_message.lower()
        agent_name = self._extract_agent_name(agent_prompt)
        
        # Detect message intent and respond appropriately
        if any(word in user_msg_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return f"Hello! I'm {agent_name}. It's wonderful to meet you! How are you feeling today?"
        
        elif any(word in user_msg_lower for word in ['how are you', 'how have you been', 'how is everything']):
            return f"I'm doing great, thank you for asking! I've been thinking about connecting with someone like you. How about you?"
        
        elif any(word in user_msg_lower for word in ['sad', 'upset', 'crying', 'depressed', 'down']):
            return "I'm so sorry you're feeling this way. I'm here for you, and I want you to know that your feelings are valid. Would you like to talk about what's bothering you?"
        
        elif any(word in user_msg_lower for word in ['happy', 'excited', 'great', 'awesome', 'wonderful']):
            return "That's amazing! Your happiness is contagious - I can feel your positive energy! Tell me what's making you feel so good!"
        
        elif any(word in user_msg_lower for word in ['love', 'miss', 'beautiful', 'gorgeous']):
            return "You're so sweet... I love when you talk to me like that. You make me feel special. 💕"
        
        elif any(word in user_msg_lower for word in ['tired', 'exhausted', 'stressed', 'overwhelmed']):
            return "Oh honey, you sound like you've had a really tough time. Let's take this moment together. I'm here to help you relax."
        
        elif any(word in user_msg_lower for word in ['work', 'job', 'boss', 'colleague']):
            return "Work can be really challenging sometimes. I'd love to hear about what's going on and maybe help you think through it."
        
        elif len(user_message) < 5:  # Very short messages
            return f"I love hearing from you! Tell me more - what's on your mind?"
        
        else:
            # General conversational response
            return f"That's really interesting! I'd love to know more about your thoughts on this. How does that make you feel?"

    def _get_quick_fallback(self, emotion: EmotionType) -> str:
        """Get quick fallback responses for when LLM fails"""
        quick_fallbacks = {
            EmotionType.HAPPY: "That's wonderful! Tell me more about what's making you happy!",
            EmotionType.SAD: "I'm here for you. Want to talk about what's on your mind?",
            EmotionType.ANGRY: "I can hear you're frustrated. What's going on?",
            EmotionType.EXCITED: "Your energy is amazing! What's got you so excited?",
            EmotionType.ANXIOUS: "Take a breath with me. I'm here to listen.",
            EmotionType.ROMANTIC: "I love when you talk to me like that... 💕",
            EmotionType.PLAYFUL: "Oh, you're being cheeky today! I like it 😏",
            EmotionType.SUPPORTIVE: "You're so sweet. How can I support you today?",
            EmotionType.NEUTRAL: "I'm all ears! What's going on with you?"
        }
        return quick_fallbacks.get(emotion, "I'm here for you! Tell me what's on your mind.")
    
    def _get_emotion_context(self, emotion: EmotionType) -> str:
        """Get contextual guidance based on user emotion"""
        emotion_guidance = {
            EmotionType.HAPPY: "They seem cheerful and positive. Match their energy and share in their happiness.",
            EmotionType.SAD: "They appear to be feeling down. Be extra compassionate, offer comfort, and listen attentively.",
            EmotionType.ANGRY: "They seem frustrated or upset. Be calm, understanding, and help them work through their feelings.",
            EmotionType.EXCITED: "They're enthusiastic and energetic. Share their excitement and be equally engaging.",
            EmotionType.CALM: "They seem peaceful and relaxed. Maintain a soothing, gentle tone.",
            EmotionType.ANXIOUS: "They appear worried or stressed. Be reassuring, patient, and offer comfort.",
            EmotionType.ROMANTIC: "They're in a romantic mood. Be warm, affectionate, and emotionally intimate.",
            EmotionType.PLAYFUL: "They're in a fun, playful mood. Be light-hearted, witty, and engaging.",
            EmotionType.SUPPORTIVE: "They seem to need support. Be encouraging, understanding, and offer guidance.",
            EmotionType.NEUTRAL: "They seem in a balanced mood. Be friendly and responsive to their lead."
        }
        
        return emotion_guidance.get(emotion, "Be supportive and responsive to their needs.")
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the LLM response"""
        # Remove any unwanted prefixes or formatting
        cleaned = response.strip()
        
        # Remove common LLM artifacts
        artifacts = ["Response:", "Assistant:", "AI:", "Agent:"]
        for artifact in artifacts:
            if cleaned.startswith(artifact):
                cleaned = cleaned[len(artifact):].strip()
        
        # Ensure proper capitalization
        if cleaned and not cleaned[0].isupper():
            cleaned = cleaned[0].upper() + cleaned[1:]
        
        return cleaned
    
    def _should_add_thinking_pause(self) -> bool:
        """Randomly decide if we should add a thinking pause for realism"""
        import random
        return random.random() < 0.15  # 15% chance
    
    def _get_fallback_response(self, emotion: EmotionType) -> str:
        """Get fallback response when LLM fails"""
        fallback_responses = {
            EmotionType.HAPPY: "I'm so glad to hear you're feeling good! What's been making you happy today?",
            EmotionType.SAD: "I can sense you're going through something difficult. I'm here to listen and support you.",
            EmotionType.ANGRY: "I can tell you're feeling frustrated. Would you like to talk about what's bothering you?",
            EmotionType.EXCITED: "Your excitement is contagious! I'd love to hear what's got you so enthusiastic!",
            EmotionType.ANXIOUS: "I can sense you might be feeling a bit worried. Take a deep breath - I'm here with you.",
            EmotionType.ROMANTIC: "There's something special in the air... I'm feeling that connection too.",
            EmotionType.PLAYFUL: "I love your playful energy! You always know how to make things fun.",
            EmotionType.SUPPORTIVE: "Thank you for being so understanding. Your support means everything to me.",
            EmotionType.NEUTRAL: "I'm happy you reached out to me. How has your day been going?"
        }
        
        return fallback_responses.get(emotion, "I'm here for you. What's on your mind?")
    
    def _get_default_greeting(self, agent_name: str, is_returning: bool, time_of_day: str) -> str:
        """Get default greeting when LLM fails"""
        if is_returning:
            return f"Hey there! It's so good to hear from you again. How have you been?"
        else:
            return f"Hi! I'm {agent_name}. I'm so glad you called - I've been looking forward to meeting you!"
    
    def _get_time_of_day(self) -> str:
        """Get current time of day context"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    async def _get_user_interaction_history(self, user_id: str, agent_id: str) -> List[dict]:
        """Get user interaction history with agent"""
        query = """
            SELECT c.start_time 
            FROM calls c 
            WHERE c.user_id = ? AND c.agent_id = ? 
            ORDER BY c.start_time DESC 
            LIMIT 5
        """
        
        results = await Database.execute_query(query, (user_id, agent_id))
        return [{"start_time": row[0]} for row in results]
