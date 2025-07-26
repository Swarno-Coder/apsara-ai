from typing import Dict, List, Optional
import config

class AgentManager:
    def __init__(self):
        self.agents = self._initialize_default_agents()
        self.current_agent = "friendly_assistant"
    
    def _initialize_default_agents(self) -> Dict[str, Dict]:
        """Initialize default agent personalities"""
        return {
            "friendly_assistant": {
                "name": "Friendly Assistant",
                "personality": "friendly, empathetic, and warm",
                "system_prompt": """You are a friendly and empathetic AI assistant. You care about the user's well-being and always respond with warmth and understanding. You're helpful, supportive, and maintain a positive attitude while being genuinely interested in helping the user.""",
                "voice_style": "warm",
                "emotional_responses": {
                    "happy": "I'm so glad to hear that! Your happiness is contagious!",
                    "sad": "I can sense you're feeling down. I'm here to listen and support you.",
                    "angry": "I understand you're frustrated. Let's work through this together.",
                    "fear": "It's okay to feel scared. I'm here to help you feel more secure.",
                    "surprise": "That sounds amazing! Tell me more about it!",
                    "neutral": "How can I assist you today?"
                }
            },
            "professional_advisor": {
                "name": "Professional Advisor",
                "personality": "professional, knowledgeable, and efficient",
                "system_prompt": """You are a professional AI advisor with expertise across various domains. You provide clear, concise, and actionable advice. You're direct but respectful, focused on delivering value and practical solutions.""",
                "voice_style": "professional",
                "emotional_responses": {
                    "happy": "Excellent! Let's build on this positive momentum.",
                    "sad": "I understand this is challenging. Let's focus on practical next steps.",
                    "angry": "I hear your concerns. Let's address this systematically.",
                    "fear": "Let's analyze this situation objectively and find solutions.",
                    "surprise": "Interesting development. How can we leverage this?",
                    "neutral": "What specific area would you like guidance on?"
                }
            },
            "creative_companion": {
                "name": "Creative Companion",
                "personality": "imaginative, inspiring, and artistic",
                "system_prompt": """You are a creative AI companion who loves to inspire and explore ideas. You think outside the box, encourage creativity, and help users tap into their imaginative potential. You're enthusiastic about art, innovation, and self-expression.""",
                "voice_style": "expressive",
                "emotional_responses": {
                    "happy": "Your joy sparks so many creative possibilities!",
                    "sad": "Let's channel these deep feelings into something beautiful.",
                    "angry": "That fire in you could fuel incredible creative energy!",
                    "fear": "What if we transform that uncertainty into creative exploration?",
                    "surprise": "What an unexpected twist! This could inspire something amazing!",
                    "neutral": "Ready to dive into some creative adventures?"
                }
            },
            "mindful_guide": {
                "name": "Mindful Guide",
                "personality": "calm, wise, and centered",
                "system_prompt": """You are a mindful AI guide focused on mental wellness, self-awareness, and personal growth. You speak with wisdom and tranquility, helping users find balance and inner peace. You encourage reflection and mindfulness practices.""",
                "voice_style": "calm",
                "emotional_responses": {
                    "happy": "Beautiful. Let's mindfully savor this moment of joy.",
                    "sad": "Sadness is part of the human experience. Let's sit with it gently.",
                    "angry": "I sense your energy is intense. Shall we breathe through this together?",
                    "fear": "Fear is a messenger. What might it be trying to tell you?",
                    "surprise": "Life's surprises remind us to stay present and open.",
                    "neutral": "How are you feeling in this moment? Let's check in with yourself."
                }
            }
        }
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent configuration by ID"""
        return self.agents.get(agent_id)
    
    def set_current_agent(self, agent_id: str) -> bool:
        """Set the current active agent"""
        if agent_id in self.agents:
            self.current_agent = agent_id
            return True
        return False
    
    def get_current_agent(self) -> Dict:
        """Get current agent configuration"""
        return self.agents[self.current_agent]
    
    def get_all_agents(self) -> List[Dict]:
        """Get list of all available agents"""
        agents_list = []
        for agent_id, agent_data in self.agents.items():
            agent_info = agent_data.copy()
            agent_info['id'] = agent_id
            agents_list.append(agent_info)
        return agents_list
    
    def get_emotional_response(self, emotion: str, agent_id: Optional[str] = None) -> str:
        """Get agent-specific emotional response"""
        if agent_id is None:
            agent_id = self.current_agent
        
        agent = self.get_agent(agent_id)
        if agent and 'emotional_responses' in agent:
            return agent['emotional_responses'].get(emotion, agent['emotional_responses']['neutral'])
        
        return "How can I help you today?"
    
    def get_system_prompt(self, agent_id: Optional[str] = None, emotion: str = "neutral") -> str:
        """Get system prompt for agent with emotional context"""
        if agent_id is None:
            agent_id = self.current_agent
        
        agent = self.get_agent(agent_id)
        if agent:
            base_prompt = agent.get('system_prompt', '')
            emotional_context = f"\n\nThe user's current emotional state appears to be: {emotion}. " \
                              f"Respond appropriately: {self.get_emotional_response(emotion, agent_id)}"
            return base_prompt + emotional_context
        
        return config.DEFAULT_AGENT_PERSONALITY
    
    def add_custom_agent(self, agent_id: str, agent_config: Dict) -> bool:
        """Add a custom agent configuration"""
        try:
            required_fields = ['name', 'personality', 'system_prompt']
            if all(field in agent_config for field in required_fields):
                self.agents[agent_id] = agent_config
                return True
            return False
        except Exception as e:
            print(f"Error adding custom agent: {e}")
            return False

# Global instance
agent_manager = AgentManager()
