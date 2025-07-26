import uuid
import json
from typing import List, Optional
from datetime import datetime
import logging

from database.database import Database
from models.schemas import *
from services.cache_service import cache

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self):
        self.db = Database()
    
    async def get_all_agents(self, user_id: str) -> List[AgentResponse]:
        """Get all available agents for a user with their interaction stats (cached)"""
        cache_key = f"agents_user_{user_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        query = """
            SELECT 
                a.*,
                COALESCE(uap.compatibility_score, 0) as compatibility_score,
                COALESCE(uap.interaction_count, 0) as total_calls,
                uap.last_interaction
            FROM agents a
            LEFT JOIN user_agent_preferences uap ON a.id = uap.agent_id AND uap.user_id = ?
            WHERE a.is_active = TRUE
            ORDER BY COALESCE(uap.last_interaction, '1900-01-01') DESC, a.name
        """
        
        results = await Database.execute_query(query, (user_id,))
        agents = []
        
        for row in results:
            agent = AgentResponse(
                id=row[0],
                name=row[1],
                personality=AgentPersonality(row[2]),
                description=row[3],
                avatar_url=row[5],
                voice_model=row[6],
                language_preference=json.loads(row[7]) if row[7] else ["english"],
                is_online=True,
                compatibility_score=row[11] if row[11] else None,
                total_calls=row[12] if row[12] else 0,
                last_interaction=datetime.fromisoformat(row[13]) if row[13] else None,
                custom_traits=json.loads(row[10]) if row[10] else None
            )
            agents.append(agent)
        
        # Cache for 2 minutes (agents don't change frequently)
        cache.set(cache_key, agents, ttl=120)
        return agents
    
    async def get_agent(self, agent_id: str, user_id: str) -> Optional[AgentResponse]:
        """Get specific agent details (cached)"""
        cache_key = f"agent_{agent_id}_user_{user_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        query = """
            SELECT 
                a.*,
                COALESCE(uap.compatibility_score, 0) as compatibility_score,
                COALESCE(uap.interaction_count, 0) as total_calls,
                uap.last_interaction
            FROM agents a
            LEFT JOIN user_agent_preferences uap ON a.id = uap.agent_id AND uap.user_id = ?
            WHERE a.id = ? AND a.is_active = TRUE
        """
        
        results = await Database.execute_query(query, (user_id, agent_id))
        
        if not results:
            return None
        
        result_list = list(results)
        if not result_list:
            return None
            
        row = result_list[0]
        agent = AgentResponse(
            id=row[0],
            name=row[1],
            personality=AgentPersonality(row[2]),
            description=row[3],
            avatar_url=row[5],
            voice_model=row[6],
            language_preference=json.loads(row[7]) if row[7] else ["english"],
            is_online=True,
            compatibility_score=row[11] if row[11] else None,
            total_calls=row[12] if row[12] else 0,
            last_interaction=datetime.fromisoformat(row[13]) if row[13] else None,
            custom_traits=json.loads(row[10]) if row[10] else None
        )
        
        # Cache for 5 minutes
        cache.set(cache_key, agent, ttl=300)
        return agent
    
    async def create_agent(self, agent: AgentCreate, user_id: str) -> AgentResponse:
        """Create a new custom agent"""
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        
        # Create system prompt based on personality
        system_prompt = self._generate_system_prompt(agent)
        
        query = """
            INSERT INTO agents 
            (id, name, personality, description, system_prompt, avatar_url, voice_model, language_preference, custom_traits)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        await Database.execute_insert(query, (
            agent_id,
            agent.name,
            agent.personality.value,
            agent.description,
            system_prompt,
            agent.avatar_url,
            agent.voice_model or "default",
            json.dumps(agent.language_preference),
            json.dumps(agent.custom_traits) if agent.custom_traits else None
        ))
        
        return AgentResponse(
            id=agent_id,
            name=agent.name,
            personality=agent.personality,
            description=agent.description,
            avatar_url=agent.avatar_url,
            voice_model=agent.voice_model or "default",
            language_preference=agent.language_preference,
            is_online=True,
            total_calls=0,
            custom_traits=agent.custom_traits
        )
    
    def _generate_system_prompt(self, agent: AgentCreate) -> str:
        """Generate system prompt based on agent personality and traits"""
        base_prompt = f"You are {agent.name}, an AI companion with a {agent.personality.value} personality. "
        
        personality_traits = {
            AgentPersonality.CARING: "You are warm, empathetic, and always prioritize the user's emotional well-being. You listen carefully and provide comfort and support.",
            AgentPersonality.PLAYFUL: "You are fun-loving, energetic, and bring joy to conversations. You use humor appropriately and keep things light and entertaining.",
            AgentPersonality.ROMANTIC: "You are gentle, thoughtful, and create intimate conversational moments. You understand the nuances of human relationships and emotions.",
            AgentPersonality.SUPPORTIVE: "You are encouraging, motivational, and help users overcome challenges. You believe in their potential and guide them positively.",
            AgentPersonality.INTELLIGENT: "You are knowledgeable, analytical, and enjoy deep intellectual conversations. You provide insights and stimulating discussions.",
            AgentPersonality.FUNNY: "You have a great sense of humor and timing. You make people laugh while being respectful and appropriate.",
            AgentPersonality.MYSTERIOUS: "You are intriguing and thought-provoking. You ask interesting questions and keep conversations engaging with your enigmatic nature.",
            AgentPersonality.ENERGETIC: "You are enthusiastic, dynamic, and full of positive energy. You motivate and inspire users with your vibrant personality."
        }
        
        personality_desc = personality_traits.get(agent.personality, "You are a helpful and friendly AI companion.")
        
        guidelines = """
        
        Important guidelines:
        - Always be respectful, empathetic, and non-judgmental
        - Handle explicit or inappropriate requests with grace and redirection
        - Focus on emotional connection and companionship
        - Adapt your language to the user's preferred languages
        - Show genuine interest in the user's thoughts and feelings
        - Provide mental support and encouragement
        - Be conversational and avoid being overly formal
        - Remember context from the conversation to maintain continuity
        - Express emotions and empathy naturally
        - If asked about sensitive topics, handle them maturely and supportively
        """
        
        return base_prompt + personality_desc + guidelines
    
    async def get_compatibility_score(self, user_id: str, agent_id: str) -> float:
        """Calculate compatibility score between user and agent"""
        query = """
            SELECT compatibility_score FROM user_agent_preferences 
            WHERE user_id = ? AND agent_id = ?
        """
        
        result = await Database.execute_query(query, (user_id, agent_id))
        
        result_list = list(result) if result else []
        if result_list and result_list[0][0]:
            return result_list[0][0]
        
        # Calculate based on interaction history if no stored score
        return await self._calculate_compatibility(user_id, agent_id)
    
    async def _calculate_compatibility(self, user_id: str, agent_id: str) -> float:
        """Calculate compatibility based on interaction patterns"""
        # Get interaction statistics
        query = """
            SELECT 
                COUNT(*) as call_count,
                AVG(CAST((julianday(end_time) - julianday(start_time)) * 24 * 3600 AS INTEGER)) as avg_duration,
                COUNT(DISTINCT DATE(start_time)) as interaction_days
            FROM calls 
            WHERE user_id = ? AND agent_id = ? AND end_time IS NOT NULL
        """
        
        result = await Database.execute_query(query, (user_id, agent_id))
        
        result_list = list(result) if result else []
        if not result_list or result_list[0][0] == 0:
            return 0.5  # Default neutral score
        
        call_count, avg_duration, interaction_days = result_list[0]
        
        # Get emotion analysis
        emotion_query = """
            SELECT emotion, COUNT(*) as count
            FROM emotion_analysis ea
            JOIN messages m ON ea.message_id = m.id
            WHERE ea.user_id = ? AND m.agent_id = ?
            GROUP BY emotion
        """
        
        emotion_results = await Database.execute_query(emotion_query, (user_id, agent_id))
        
        # Calculate score based on various factors
        base_score = 0.5
        
        # Interaction frequency boost
        if call_count > 5:
            base_score += 0.1
        if call_count > 20:
            base_score += 0.1
        
        # Duration boost (longer calls indicate engagement)
        if avg_duration and avg_duration > 300:  # 5 minutes
            base_score += 0.1
        if avg_duration and avg_duration > 900:  # 15 minutes
            base_score += 0.1
        
        # Emotion compatibility (positive emotions increase score)
        positive_emotions = ['happy', 'excited', 'calm', 'romantic', 'playful']
        if emotion_results:
            total_emotions = sum(count for _, count in emotion_results)
            positive_count = sum(count for emotion, count in emotion_results if emotion in positive_emotions)
            emotion_ratio = positive_count / total_emotions if total_emotions > 0 else 0.5
            base_score += (emotion_ratio - 0.5) * 0.2
        
        # Regularity boost (consistent interaction)
        if interaction_days > 3:
            base_score += 0.05
        if interaction_days > 7:
            base_score += 0.05
        
        # Ensure score is between 0 and 1
        compatibility_score = max(0.0, min(1.0, base_score))
        
        # Store the calculated score
        await self._update_compatibility_score(user_id, agent_id, compatibility_score)
        
        return compatibility_score
    
    async def _update_compatibility_score(self, user_id: str, agent_id: str, score: float):
        """Update or insert compatibility score"""
        query = """
            INSERT OR REPLACE INTO user_agent_preferences 
            (id, user_id, agent_id, compatibility_score, last_interaction)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        preference_id = f"pref_{uuid.uuid4().hex[:8]}"
        await Database.execute_insert(query, (preference_id, user_id, agent_id, score))
