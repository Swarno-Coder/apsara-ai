import json
import asyncio
from typing import Dict, List, Optional
import websockets
from websockets.legacy.server import WebSocketServerProtocol
import base64
import time

# Import our modules
from stt_whispercpp import whisper_cpp
from emotion_classifier import emotion_classifier
from llm_openrouter import llm_client
from tts_piper import tts_engine
from firebase_interface import firebase_client
from faiss_memory import memory_manager
from agent_manager import agent_manager
from audio_utils import audio_from_bytes, convert_to_wav

class WebSocketHandler:
    def __init__(self):
        self.active_connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_sessions: Dict[str, Dict] = {}
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        connection_id = str(id(websocket))
        self.active_connections[connection_id] = websocket
        
        print(f"New WebSocket connection: {connection_id}")
        
        try:
            await self._handle_messages(websocket, connection_id)
        except websockets.exceptions.ConnectionClosed:
            print(f"WebSocket connection closed: {connection_id}")
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            self._cleanup_connection(connection_id)
    
    async def _handle_messages(self, websocket: WebSocketServerProtocol, connection_id: str):
        """Handle incoming WebSocket messages"""
        async for message in websocket:
            try:
                data = json.loads(message)
                await self._process_message(websocket, connection_id, data)
            except json.JSONDecodeError:
                await self._send_error(websocket, "Invalid JSON format")
            except Exception as e:
                await self._send_error(websocket, f"Message processing error: {str(e)}")
    
    async def _process_message(self, websocket: WebSocketServerProtocol, connection_id: str, data: Dict):
        """Process different types of messages"""
        message_type = data.get('type')
        
        if message_type == 'auth':
            await self._handle_auth(websocket, connection_id, data)
        elif message_type == 'audio_chunk':
            await self._handle_audio_chunk(websocket, connection_id, data)
        elif message_type == 'text_message':
            await self._handle_text_message(websocket, connection_id, data)
        elif message_type == 'set_agent':
            await self._handle_set_agent(websocket, connection_id, data)
        elif message_type == 'get_agents':
            await self._handle_get_agents(websocket)
        elif message_type == 'get_history':
            await self._handle_get_history(websocket, connection_id, data)
        else:
            await self._send_error(websocket, f"Unknown message type: {message_type}")
    
    async def _handle_auth(self, websocket: WebSocketServerProtocol, connection_id: str, data: Dict):
        """Handle user authentication"""
        token = data.get('token')
        if not token:
            await self._send_error(websocket, "No authentication token provided")
            return
        
        user_info = firebase_client.verify_user_token(token)
        if user_info:
            self.user_sessions[connection_id] = {
                'user_id': user_info['uid'],
                'user_info': user_info,
                'agent_id': 'friendly_assistant',
                'audio_buffer': b'',
                'conversation_context': []
            }
            
            await self._send_message(websocket, {
                'type': 'auth_success',
                'user': user_info
            })
        else:
            await self._send_error(websocket, "Authentication failed")
    
    async def _handle_audio_chunk(self, websocket: WebSocketServerProtocol, connection_id: str, data: Dict):
        """Handle incoming audio chunk"""
        session = self.user_sessions.get(connection_id)
        if not session:
            await self._send_error(websocket, "Not authenticated")
            return
        
        try:
            # Decode audio chunk
            audio_b64 = data.get('audio_data')
            if not audio_b64:
                return
            
            audio_bytes = base64.b64decode(audio_b64)
            
            # Check if this is the end of audio stream
            if data.get('is_final', False):
                # Add final chunk and process
                session['audio_buffer'] += audio_bytes
                await self._process_complete_audio(websocket, session)
                session['audio_buffer'] = b''  # Reset buffer
            else:
                # Accumulate audio chunks
                session['audio_buffer'] += audio_bytes
                
                # Send acknowledgment
                await self._send_message(websocket, {
                    'type': 'audio_received',
                    'chunk_size': len(audio_bytes)
                })
        
        except Exception as e:
            await self._send_error(websocket, f"Audio processing error: {str(e)}")
    
    async def _process_complete_audio(self, websocket: WebSocketServerProtocol, session: Dict):
        """Process complete audio input through the full pipeline"""
        try:
            audio_buffer = session['audio_buffer']
            user_id = session['user_id']
            agent_id = session['agent_id']
            
            # Step 1: Speech-to-Text
            await self._send_message(websocket, {'type': 'status', 'message': 'Transcribing audio...'})
            transcription = whisper_cpp.transcribe_from_bytes(audio_buffer)
            
            if not transcription.strip():
                await self._send_message(websocket, {'type': 'error', 'message': 'No speech detected'})
                return
            
            await self._send_message(websocket, {
                'type': 'transcription',
                'text': transcription
            })
            
            # Step 2: Emotion Detection
            await self._send_message(websocket, {'type': 'status', 'message': 'Analyzing emotion...'})
            emotions = emotion_classifier.classify_text_emotion(transcription)
            dominant_emotion = emotion_classifier.get_dominant_emotion(emotions)
            
            await self._send_message(websocket, {
                'type': 'emotion',
                'emotion': dominant_emotion,
                'confidence': emotions[dominant_emotion]
            })
            
            # Step 3: Memory Retrieval
            await self._send_message(websocket, {'type': 'status', 'message': 'Retrieving memories...'})
            relevant_memories = memory_manager.search_memories(transcription, user_id)
            
            # Step 4: LLM Response Generation
            await self._send_message(websocket, {'type': 'status', 'message': 'Generating response...'})
            
            # Build context from memories and conversation history
            context_messages = []
            
            # Add relevant memories as context
            if relevant_memories:
                memory_context = "Previous relevant context:\n"
                for memory in relevant_memories[:3]:  # Top 3 memories
                    memory_context += f"- {memory['text']}\n"
                context_messages.append({"role": "system", "content": memory_context})
            
            # Add recent conversation context
            context_messages.extend(session['conversation_context'][-5:])  # Last 5 messages
            
            # Get agent personality and generate response
            agent = agent_manager.get_agent(agent_id)
            system_prompt = agent_manager.get_system_prompt(agent_id, dominant_emotion)
            
            response = await llm_client.generate_response(
                prompt=transcription,
                context=context_messages,
                emotion=dominant_emotion,
                agent_personality=agent['personality']
            )
            
            await self._send_message(websocket, {
                'type': 'llm_response',
                'text': response
            })
            
            # Step 5: Text-to-Speech
            await self._send_message(websocket, {'type': 'status', 'message': 'Generating speech...'})
            tts_audio = tts_engine.synthesize_speech(response, dominant_emotion)
            
            if tts_audio:
                # Send audio in chunks
                tts_b64 = base64.b64encode(tts_audio).decode('utf-8')
                await self._send_message(websocket, {
                    'type': 'tts_audio',
                    'audio_data': tts_b64
                })
            
            # Step 6: Store in Memory and Firebase
            await self._store_interaction(session, transcription, response, dominant_emotion)
            
            await self._send_message(websocket, {'type': 'status', 'message': 'Complete!'})
            
        except Exception as e:
            await self._send_error(websocket, f"Processing error: {str(e)}")
    
    async def _handle_text_message(self, websocket: WebSocketServerProtocol, connection_id: str, data: Dict):
        """Handle text-only message (no audio)"""
        session = self.user_sessions.get(connection_id)
        if not session:
            await self._send_error(websocket, "Not authenticated")
            return
        
        text = data.get('text', '').strip()
        if not text:
            return
        
        try:
            user_id = session['user_id']
            agent_id = session['agent_id']
            
            # Process similar to audio, but skip STT
            emotions = emotion_classifier.classify_text_emotion(text)
            dominant_emotion = emotion_classifier.get_dominant_emotion(emotions)
            
            relevant_memories = memory_manager.search_memories(text, user_id)
            
            context_messages = []
            if relevant_memories:
                memory_context = "Previous relevant context:\n"
                for memory in relevant_memories[:3]:
                    memory_context += f"- {memory['text']}\n"
                context_messages.append({"role": "system", "content": memory_context})
            
            context_messages.extend(session['conversation_context'][-5:])
            
            agent = agent_manager.get_agent(agent_id)
            response = await llm_client.generate_response(
                prompt=text,
                context=context_messages,
                emotion=dominant_emotion,
                agent_personality=agent['personality']
            )
            
            await self._send_message(websocket, {
                'type': 'text_response',
                'user_message': text,
                'assistant_response': response,
                'emotion': dominant_emotion
            })
            
            await self._store_interaction(session, text, response, dominant_emotion)
            
        except Exception as e:
            await self._send_error(websocket, f"Text processing error: {str(e)}")
    
    async def _handle_set_agent(self, websocket: WebSocketServerProtocol, connection_id: str, data: Dict):
        """Handle agent selection"""
        session = self.user_sessions.get(connection_id)
        if not session:
            await self._send_error(websocket, "Not authenticated")
            return
        
        agent_id = data.get('agent_id')
        if agent_manager.set_current_agent(agent_id):
            session['agent_id'] = agent_id
            agent = agent_manager.get_agent(agent_id)
            
            await self._send_message(websocket, {
                'type': 'agent_set',
                'agent_id': agent_id,
                'agent_name': agent['name']
            })
        else:
            await self._send_error(websocket, f"Invalid agent ID: {agent_id}")
    
    async def _handle_get_agents(self, websocket: WebSocketServerProtocol):
        """Handle request for available agents"""
        agents = agent_manager.get_all_agents()
        await self._send_message(websocket, {
            'type': 'agents_list',
            'agents': agents
        })
    
    async def _handle_get_history(self, websocket: WebSocketServerProtocol, connection_id: str, data: Dict):
        """Handle request for chat history"""
        session = self.user_sessions.get(connection_id)
        if not session:
            await self._send_error(websocket, "Not authenticated")
            return
        
        limit = data.get('limit', 10)
        history = firebase_client.get_chat_history(session['user_id'], limit)
        
        await self._send_message(websocket, {
            'type': 'chat_history',
            'messages': history
        })
    
    async def _store_interaction(self, session: Dict, user_text: str, assistant_response: str, emotion: str):
        """Store interaction in memory and Firebase"""
        user_id = session['user_id']
        timestamp = time.time()
        
        # Store in FAISS memory
        memory_manager.add_memory(
            text=f"User: {user_text} | Assistant: {assistant_response}",
            user_id=user_id,
            emotion=emotion,
            additional_metadata={
                'user_message': user_text,
                'assistant_response': assistant_response,
                'timestamp': timestamp
            }
        )
        
        # Store in Firebase
        chat_message = {
            'user_message': user_text,
            'assistant_response': assistant_response,
            'emotion': emotion,
            'agent_id': session['agent_id'],
            'timestamp': timestamp
        }
        firebase_client.store_chat_message(user_id, chat_message)
        
        # Update conversation context
        session['conversation_context'].extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_response}
        ])
        
        # Keep only recent context
        if len(session['conversation_context']) > 10:
            session['conversation_context'] = session['conversation_context'][-10:]
    
    async def _send_message(self, websocket: WebSocketServerProtocol, message: Dict):
        """Send message to WebSocket client"""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def _send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send error message to WebSocket client"""
        await self._send_message(websocket, {
            'type': 'error',
            'message': error_message
        })
    
    def _cleanup_connection(self, connection_id: str):
        """Clean up connection data"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.user_sessions:
            del self.user_sessions[connection_id]

# Global instance
websocket_handler = WebSocketHandler()
