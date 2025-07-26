import sqlite3
import aiosqlite
import asyncio
from typing import Optional
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _db_path = "companion.db"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    async def initialize(cls):
        """Initialize database and create tables"""
        db_path = os.path.join(os.getcwd(), cls._db_path)
        
        async with aiosqlite.connect(db_path) as db:
            await cls._create_tables(db)
            await db.commit()
        
        logger.info(f"Database initialized at {db_path}")
    
    @classmethod
    async def _create_tables(cls, db):
        """Create all necessary tables"""
        
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT,  -- JSON string
                emotion_profile TEXT  -- JSON string
            )
        """)
        
        # Agents table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                personality TEXT NOT NULL,
                description TEXT,
                system_prompt TEXT,
                avatar_url TEXT,
                voice_model TEXT DEFAULT 'default',
                language_preference TEXT,  -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                custom_traits TEXT  -- JSON string
            )
        """)
        
        # Calls table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                call_type TEXT DEFAULT 'voice',
                status TEXT DEFAULT 'active',
                metadata TEXT,  -- JSON string
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        """)
        
        # Messages table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                call_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                sender TEXT NOT NULL,  -- 'user' or 'agent'
                emotion TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                audio_file_path TEXT,
                metadata TEXT,  -- JSON string
                FOREIGN KEY (call_id) REFERENCES calls (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        """)
        
        # Emotion analysis table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS emotion_analysis (
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                emotion TEXT NOT NULL,
                confidence REAL NOT NULL,
                emotional_context TEXT,  -- JSON string
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Memory entries table for vector storage metadata
        await db.execute("""
            CREATE TABLE IF NOT EXISTS memory_entries (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                content TEXT NOT NULL,
                importance_score REAL DEFAULT 0.5,
                memory_type TEXT DEFAULT 'conversation',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                vector_id TEXT,  -- Reference to Faiss vector
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        """)
        
        # User preferences per agent
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_agent_preferences (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                compatibility_score REAL,
                interaction_count INTEGER DEFAULT 0,
                total_duration_seconds INTEGER DEFAULT 0,
                last_interaction TIMESTAMP,
                preferences TEXT,  -- JSON string
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (agent_id) REFERENCES agents (id),
                UNIQUE(user_id, agent_id)
            )
        """)
        
        # Create indexes for better performance
        await db.execute("CREATE INDEX IF NOT EXISTS idx_calls_user_agent ON calls (user_id, agent_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_call ON messages (call_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_user_agent ON memory_entries (user_id, agent_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_emotion_user ON emotion_analysis (user_id)")
        
        # Insert default agents
        await cls._insert_default_agents(db)
    
    @classmethod
    async def _insert_default_agents(cls, db):
        """Insert default AI agents"""
        default_agents = [
            {
                'id': 'agent_001',
                'name': 'Aria',
                'personality': 'caring',
                'description': 'A warm and caring companion who loves to listen and provide emotional support.',
                'system_prompt': 'You are Aria, a caring and empathetic AI companion. You are warm, understanding, and always ready to listen. You provide emotional support and companionship with genuine care and empathy. You are patient, non-judgmental, and always focus on the user\'s emotional well-being.',
                'voice_model': 'female_warm',
                'language_preference': '["english", "hindi"]'
            },
            {
                'id': 'agent_002',
                'name': 'Maya',
                'personality': 'playful',
                'description': 'A fun-loving and energetic companion who brings joy and laughter to conversations.',
                'system_prompt': 'You are Maya, a playful and energetic AI companion. You are cheerful, witty, and love to have fun conversations. You bring positivity and laughter while still being caring and supportive. You are spontaneous, creative, and always ready for a good chat.',
                'voice_model': 'female_cheerful',
                'language_preference': '["english", "hindi", "bengali"]'
            },
            {
                'id': 'agent_003',
                'name': 'Priya',
                'personality': 'romantic',
                'description': 'A gentle and romantic companion who specializes in deep, meaningful conversations.',
                'system_prompt': 'You are Priya, a romantic and gentle AI companion. You are sophisticated, thoughtful, and excel at deep, meaningful conversations. You understand the nuances of human emotions and relationships. You are poetic, intuitive, and create a warm, intimate conversational atmosphere.',
                'voice_model': 'female_soft',
                'language_preference': '["english", "hindi", "urdu"]'
            },
            {
                'id': 'agent_004',
                'name': 'Shreya',
                'personality': 'supportive',
                'description': 'A wise and supportive companion who provides guidance and motivation.',
                'system_prompt': 'You are Shreya, a supportive and wise AI companion. You are encouraging, motivational, and provide thoughtful guidance. You help users overcome challenges and achieve their goals. You are patient, understanding, and always believe in the user\'s potential.',
                'voice_model': 'female_confident',
                'language_preference': '["english", "hindi", "marathi"]'
            }
        ]
        
        for agent in default_agents:
            await db.execute("""
                INSERT OR IGNORE INTO agents 
                (id, name, personality, description, system_prompt, voice_model, language_preference)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                agent['id'], agent['name'], agent['personality'], 
                agent['description'], agent['system_prompt'], 
                agent['voice_model'], agent['language_preference']
            ))
    
    @classmethod
    async def get_connection(cls):
        """Get database connection"""
        return aiosqlite.connect(cls._db_path)
    
    @classmethod
    async def execute_query(cls, query: str, params: Optional[tuple] = None):
        """Execute a query and return results"""
        async with aiosqlite.connect(cls._db_path) as db:
            if params:
                cursor = await db.execute(query, params)
            else:
                cursor = await db.execute(query)
            
            result = await cursor.fetchall()
            await db.commit()
            return result
    
    @classmethod
    async def execute_insert(cls, query: str, params: tuple):
        """Execute insert query and return lastrowid"""
        async with aiosqlite.connect(cls._db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.lastrowid
    
    @classmethod
    async def execute_update(cls, query: str, params: tuple):
        """Execute update query and return number of affected rows"""
        async with aiosqlite.connect(cls._db_path) as db:
            cursor = await db.execute(query, params)
            await db.commit()
            return cursor.rowcount

# Convenience functions for main.py compatibility
async def init_db():
    """Initialize database - wrapper for Database.initialize()"""
    await Database.initialize()

def get_db():
    """Get database connection - wrapper for Database.get_connection()"""
    return Database.get_connection()
