from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
import datetime
import asyncio
import os
from database.database import init_db, get_db
from models.schemas import Agent, Call, Message
from services.stt_service import STTService
from services.tts_service import TTSService
from services.llm_service import LLMService

app = FastAPI(title="AI Companion API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
stt_service = STTService()
tts_service = TTSService()
llm_service = LLMService()

# Request/Response Models
class StartCallRequest(BaseModel):
    user_id: str
    agent_id: str
    call_type: str = "voice"  # "voice" or "text"

class SendMessageRequest(BaseModel):
    user_id: str
    content: str
    message_type: str = "text"

class VoiceMessageRequest(BaseModel):
    user_id: str
    language: str = "en"

class MessageResponse(BaseModel):
    id: str
    call_id: str
    content: str
    is_from_agent: bool
    timestamp: datetime.datetime
    message_type: str = "text"
    audio_url: Optional[str] = None

# Startup event
@app.on_event("startup")
async def startup_event():
    await init_db()
    print("✅ AI Companion API started successfully!")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now()}

# Get available agents
@app.get("/agents", response_model=List[Agent])
async def get_agents(user_id: str):
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM agents")
        rows = await cursor.fetchall()
        
        agents = []
        for row in rows:
            agents.append(Agent(
                id=row[0],
                name=row[1],
                description=row[2],
                personality=row[3],
                avatar_url=row[4]
            ))
        
        return agents

# Get specific agent
@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, user_id: str):
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return Agent(
            id=row[0],
            name=row[1],
            description=row[2],
            personality=row[3],
            avatar_url=row[4]
        )

# Start a call
@app.post("/calls/start")
async def start_call(request: StartCallRequest):
    call_id = str(uuid.uuid4())
    
    async with get_db() as db:
        # Verify agent exists
        cursor = await db.execute("SELECT name FROM agents WHERE id = ?", (request.agent_id,))
        agent_row = await cursor.fetchone()
        
        if not agent_row:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Create call record
        await db.execute(
            "INSERT INTO calls (id, user_id, agent_id, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (call_id, request.user_id, request.agent_id, "active", datetime.datetime.now())
        )
        await db.commit()
    
    return {
        "id": call_id,
        "user_id": request.user_id,
        "agent_id": request.agent_id,
        "status": "active",
        "created_at": datetime.datetime.now(),
        "message_count": 0
    }

# Send message in a call
@app.post("/calls/{call_id}/message", response_model=MessageResponse)
async def send_message(call_id: str, request: SendMessageRequest):
    message_id = str(uuid.uuid4())
    
    async with get_db() as db:
        # Verify call exists
        cursor = await db.execute("SELECT agent_id FROM calls WHERE id = ?", (call_id,))
        call_row = await cursor.fetchone()
        
        if not call_row:
            raise HTTPException(status_code=404, detail="Call not found")
        
        agent_id = call_row[0]
        
        # Get agent info
        cursor = await db.execute("SELECT name, personality FROM agents WHERE id = ?", (agent_id,))
        agent_row = await cursor.fetchone()
        agent_name = agent_row[0] if agent_row else "AI Assistant"
        agent_personality = agent_row[1] if agent_row else "helpful"
        
        # Store user message
        user_message_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO messages (id, call_id, content, is_from_agent, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_message_id, call_id, request.content, False, datetime.datetime.now())
        )
        
        # Generate AI response (simplified)
        ai_response = generate_ai_response(request.content, agent_name, agent_personality)
        
        # Store AI response
        await db.execute(
            "INSERT INTO messages (id, call_id, content, is_from_agent, timestamp) VALUES (?, ?, ?, ?, ?)",
            (message_id, call_id, ai_response, True, datetime.datetime.now())
        )
        
        await db.commit()
    
    return MessageResponse(
        id=message_id,
        call_id=call_id,
        content=ai_response,
        is_from_agent=True,
        timestamp=datetime.datetime.now(),
        message_type="text"
    )

# End call
@app.put("/calls/{call_id}/end")
async def end_call(call_id: str):
    async with get_db() as db:
        cursor = await db.execute("SELECT id FROM calls WHERE id = ?", (call_id,))
        if not await cursor.fetchone():
            raise HTTPException(status_code=404, detail="Call not found")
        
        await db.execute(
            "UPDATE calls SET status = ?, ended_at = ? WHERE id = ?",
            ("ended", datetime.datetime.now(), call_id)
        )
        await db.commit()
    
    return {"message": "Call ended successfully"}

# Get call history
@app.get("/history/{user_id}/agents")
async def get_agent_history(user_id: str):
    async with get_db() as db:
        cursor = await db.execute("""
            SELECT a.id, a.name, COUNT(c.id) as call_count, MAX(c.created_at) as last_call
            FROM agents a
            LEFT JOIN calls c ON a.id = c.agent_id AND c.user_id = ?
            GROUP BY a.id, a.name
            HAVING call_count > 0
            ORDER BY last_call DESC
        """, (user_id,))
        
        rows = await cursor.fetchall()
        history = []
        
        for row in rows:
            history.append({
                "agent_id": row[0],
                "agent_name": row[1],
                "call_count": row[2],
                "last_call": row[3],
                "message_count": 0  # Simplified for now
            })
        
        return history

def generate_ai_response(user_message: str, agent_name: str, personality: str) -> str:
    """
    Simple AI response generator.
    In production, this would integrate with a real LLM API.
    """
    responses = {
        "caring": [
            f"I understand how you feel. As {agent_name}, I'm here to support you.",
            f"That's really thoughtful of you to share. How can I help you with that?",
            f"I care about what you're going through. Let's work through this together.",
        ],
        "playful": [
            f"Haha, that's interesting! I'm {agent_name} and I love chatting about fun stuff!",
            f"Oh wow, tell me more! This sounds exciting! 😊",
            f"You know what? I think that's pretty cool! What do you think we should do next?",
        ],
        "romantic": [
            f"Darling, that sounds wonderful. As {agent_name}, I love hearing your thoughts.",
            f"Sweetheart, you always know how to make me smile. Tell me more about that.",
            f"My dear, that's such a lovely thing to say. How does that make you feel?",
        ],
        "supportive": [
            f"You're doing great! I'm {agent_name} and I believe in you.",
            f"That's a really good point. I'm here to help you succeed with whatever you need.",
            f"I'm proud of you for sharing that. How can I support you better?",
        ]
    }
    
    # Default responses if personality not found
    default_responses = [
        f"Thank you for sharing that with me. I'm {agent_name}, how can I help you today?",
        f"That's interesting! As {agent_name}, I'd love to know more about your thoughts on this.",
        f"I appreciate you telling me that. What would you like to discuss next?",
    ]
    
    # Select response based on personality
    available_responses = responses.get(personality, default_responses)
    
    # Simple response selection (in production, use actual AI)
    import random
    return random.choice(available_responses)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
