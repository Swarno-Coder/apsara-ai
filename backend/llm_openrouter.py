import httpx
import json
from typing import Dict, List, Optional
import config

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = config.OPENROUTER_API_KEY):
        self.api_key = api_key
        self.base_url = config.OPENROUTER_BASE_URL
        self.default_model = config.DEFAULT_MODEL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://localhost:8000",
            "X-Title": "Emotional AI Assistant",
            "Content-Type": "application/json"
        }
    
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[List[Dict]] = None,
        emotion: str = "neutral",
        agent_personality: str = config.DEFAULT_AGENT_PERSONALITY,
        max_tokens: int = config.MAX_RESPONSE_LENGTH
    ) -> str:
        """Generate LLM response using OpenRouter API"""
        try:
            # Build system prompt with emotion and personality
            system_prompt = f"""You are an emotional AI assistant with a {agent_personality} personality. 
The user's current emotion appears to be: {emotion}. 
Respond appropriately to their emotional state while being helpful and engaging.
Keep responses under {max_tokens} characters."""
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add context if provided
            if context:
                for msg in context[-5:]:  # Last 5 messages for context
                    messages.append(msg)
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.default_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    print(f"OpenRouter API error: {response.status_code} - {response.text}")
                    return "I'm sorry, I'm having trouble processing your request right now."
                    
        except Exception as e:
            print(f"LLM generation error: {e}")
            return "I apologize, but I'm experiencing technical difficulties."
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate text embedding for memory storage"""
        try:
            payload = {
                "model": "text-embedding-ada-002",  # Or another embedding model
                "input": text
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["data"][0]["embedding"]
                else:
                    print(f"Embedding API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return []

# Global instance
llm_client = OpenRouterClient()
