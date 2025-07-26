import asyncio
import json
import uuid
import base64
from typing import Dict, Set, Optional
from datetime import datetime
import logging

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from services.stt_service import STTService
from services.tts_service import TTSService
from services.llm_service import LLMService
from services.emotion_service import EmotionService
from database.database import Database

logger = logging.getLogger(__name__)

class VoiceMessage(BaseModel):
    type: str  # "audio", "text", "control"
    content: str  # base64 encoded audio or text
    user_id: str
    agent_id: str
    call_id: str
    timestamp: datetime = datetime.now()

class WebSocketManager:
    def __init__(self):
        # Active connections by call_id
        self.active_connections: Dict[str, WebSocket] = {}
        # User to call mapping
        self.user_calls: Dict[str, str] = {}
        # Services
        self.stt_service = STTService()
        self.tts_service = TTSService()
        self.llm_service = LLMService()
        self.emotion_service = EmotionService()
    
    async def connect(self, websocket: WebSocket, call_id: str, user_id: str):
        """Accept WebSocket connection and register it"""
        await websocket.accept()
        self.active_connections[call_id] = websocket
        self.user_calls[user_id] = call_id
        
        logger.info(f"WebSocket connected for call_id: {call_id}, user_id: {user_id}")
        
        # Send connection confirmation
        await self.send_message(call_id, {
            "type": "connection",
            "status": "connected",
            "call_id": call_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, call_id: str, user_id: str):
        """Remove WebSocket connection"""
        if call_id in self.active_connections:
            del self.active_connections[call_id]
        if user_id in self.user_calls:
            del self.user_calls[user_id]
        
        logger.info(f"WebSocket disconnected for call_id: {call_id}")
    
    async def send_message(self, call_id: str, message: dict):
        """Send message to specific call WebSocket"""
        if call_id in self.active_connections:
            try:
                await self.active_connections[call_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {call_id}: {e}")
                # Remove dead connection
                if call_id in self.active_connections:
                    del self.active_connections[call_id]
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Send message to user's active call"""
        if user_id in self.user_calls:
            call_id = self.user_calls[user_id]
            await self.send_message(call_id, message)
    
    async def handle_voice_message(self, call_id: str, message: dict):
        """Process incoming voice/text message"""
        try:
            user_id = message.get("user_id")
            agent_id = message.get("agent_id")
            message_type = message.get("type")
            content = message.get("content")
            
            if not all([user_id, agent_id, call_id]):
                await self.send_error(call_id, "Missing required fields")
                return
            
            if not content:
                await self.send_error(call_id, "Missing message content")
                return
            
            # Send processing indicator
            await self.send_message(call_id, {
                "type": "processing",
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })
            
            if message_type == "audio":
                # Process voice input
                await self._process_voice_input(call_id, str(user_id), str(agent_id), str(content))
            elif message_type == "text":
                # Process text input
                await self._process_text_input(call_id, str(user_id), str(agent_id), str(content))
            elif message_type == "control":
                # Handle control messages (pause, resume, end)
                await self._handle_control_message(call_id, str(user_id), str(content))
            
        except Exception as e:
            logger.error(f"Error handling voice message: {e}")
            await self.send_error(call_id, "Internal server error")
    
    async def _process_voice_input(self, call_id: str, user_id: str, agent_id: str, audio_data: str):
        """Process voice input through STT -> LLM -> TTS pipeline"""
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Speech to Text
            await self.send_message(call_id, {
                "type": "processing",
                "stage": "speech_to_text",
                "timestamp": datetime.now().isoformat()
            })
            
            # Create a temporary file for STT service
            import tempfile
            import io
            from fastapi import UploadFile
            
            # Create a mock UploadFile object for the STT service
            audio_file = UploadFile(
                filename="audio.wav",
                file=io.BytesIO(audio_bytes)
            )
            
            transcribed_text = await self.stt_service.transcribe(audio_file)
            
            if not transcribed_text:
                await self.send_error(call_id, "Could not transcribe audio")
                return
            
            # Send transcription to user
            await self.send_message(call_id, {
                "type": "transcription",
                "content": transcribed_text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Store user message
            user_message_id = await self._store_message(
                call_id, user_id, agent_id, transcribed_text, "voice", "user"
            )
            
            # Process through LLM
            await self._generate_and_send_response(call_id, user_id, agent_id, transcribed_text)
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            await self.send_error(call_id, "Error processing voice input")
    
    async def _process_text_input(self, call_id: str, user_id: str, agent_id: str, text: str):
        """Process text input through LLM -> TTS pipeline"""
        try:
            # Store user message
            user_message_id = await self._store_message(
                call_id, user_id, agent_id, text, "text", "user"
            )
            
            # Generate and send response
            await self._generate_and_send_response(call_id, user_id, agent_id, text)
            
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
            await self.send_error(call_id, "Error processing text input")
    
    async def _generate_and_send_response(self, call_id: str, user_id: str, agent_id: str, user_message: str):
        """Generate AI response and convert to speech"""
        try:
            # Get agent info
            agent_query = "SELECT name, personality, system_prompt FROM agents WHERE id = ?"
            agent_result = await Database.execute_query(agent_query, (agent_id,))
            
            if not agent_result:
                await self.send_error(call_id, "Agent not found")
                return
            
            agent_name, personality, system_prompt = list(agent_result)[0]
            
            # Emotion analysis
            await self.send_message(call_id, {
                "type": "processing",
                "stage": "emotion_analysis",
                "timestamp": datetime.now().isoformat()
            })
            
            emotion = await self.emotion_service.analyze_emotion(user_message)
            
            # Generate LLM response
            await self.send_message(call_id, {
                "type": "processing",
                "stage": "generating_response",
                "timestamp": datetime.now().isoformat()
            })
            
            # Get conversation history for context
            history = await self._get_conversation_history(call_id)
            
            ai_response = await self.llm_service.generate_response(
                user_message=user_message,
                agent_id=agent_id,
                agent_prompt=system_prompt,
                context=history,
                user_emotion=emotion,
                user_id=user_id
            )
            
            # Store AI response
            ai_message_id = await self._store_message(
                call_id, user_id, agent_id, ai_response, "text", "agent"
            )
            
            # Send text response first
            await self.send_message(call_id, {
                "type": "response",
                "content": ai_response,
                "message_id": ai_message_id,
                "emotion": emotion,
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate speech
            await self.send_message(call_id, {
                "type": "processing",
                "stage": "text_to_speech",
                "timestamp": datetime.now().isoformat()
            })
            
            # Get agent voice model
            voice_model = await self._get_agent_voice_model(agent_id)
            
            audio_url = await self.tts_service.synthesize(
                text=ai_response,
                agent_id=agent_id,
                language="english",
                voice_style=voice_model
            )
            
            if audio_url:
                # Read the audio file and encode as base64
                try:
                    with open(audio_url, "rb") as f:
                        audio_data = f.read()
                    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    # Send audio response
                    await self.send_message(call_id, {
                        "type": "audio_response",
                        "content": audio_b64,
                        "message_id": ai_message_id,
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error reading audio file: {e}")
                    # Continue without audio if file reading fails
            
            # Send processing complete
            await self.send_message(call_id, {
                "type": "processing",
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            await self.send_error(call_id, "Error generating response")
    
    async def _handle_control_message(self, call_id: str, user_id: str, action: str):
        """Handle control messages like pause, resume, end"""
        try:
            if action == "end_call":
                # Update call status
                await Database.execute_query(
                    "UPDATE calls SET status = ?, end_time = ? WHERE id = ?",
                    ("ended", datetime.now(), call_id)
                )
                
                await self.send_message(call_id, {
                    "type": "call_ended",
                    "timestamp": datetime.now().isoformat()
                })
                
                # Disconnect WebSocket
                self.disconnect(call_id, user_id)
                
            elif action == "pause":
                await self.send_message(call_id, {
                    "type": "call_paused",
                    "timestamp": datetime.now().isoformat()
                })
                
            elif action == "resume":
                await self.send_message(call_id, {
                    "type": "call_resumed",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error handling control message: {e}")
            await self.send_error(call_id, "Error handling control message")
    
    async def _store_message(self, call_id: str, user_id: str, agent_id: str, 
                           content: str, message_type: str, sender: str) -> str:
        """Store message in database"""
        message_id = str(uuid.uuid4())
        
        await Database.execute_insert(
            """INSERT INTO messages 
               (id, call_id, user_id, agent_id, content, message_type, sender, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (message_id, call_id, user_id, agent_id, content, message_type, sender, datetime.now())
        )
        
        return message_id
    
    async def _get_conversation_history(self, call_id: str, limit: int = 10) -> list:
        """Get recent conversation history for context"""
        query = """
            SELECT content, sender, timestamp 
            FROM messages 
            WHERE call_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        
        results = await Database.execute_query(query, (call_id, limit))
        
        history = []
        for content, sender, timestamp in reversed(list(results)):
            history.append({
                "content": content,
                "sender": sender,
                "timestamp": timestamp
            })
        
        return history
    
    async def _get_agent_voice_model(self, agent_id: str) -> str:
        """Get agent's voice model preference"""
        query = "SELECT voice_model FROM agents WHERE id = ?"
        result = await Database.execute_query(query, (agent_id,))
        
        if result:
            return list(result)[0][0] or "default"
        return "default"
    
    async def send_error(self, call_id: str, error_message: str):
        """Send error message to client"""
        await self.send_message(call_id, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })

# Global WebSocket manager instance
manager = WebSocketManager()
