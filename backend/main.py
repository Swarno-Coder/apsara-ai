from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

import config
from websocket_handler import websocket_handler
from firebase_interface import firebase_client
from agent_manager import agent_manager
from faiss_memory import memory_manager

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Emotional AI Assistant Backend...")
    print(f"Server will run on {config.HOST}:{config.PORT}")
    
    # Initialize components
    try:
        # Verify Firebase connection
        if firebase_client.db:
            print("✓ Firebase initialized")
        else:
            print("⚠ Firebase not available - using fallback storage")
        
        # Check memory manager
        if memory_manager.encoder:
            print("✓ FAISS memory manager initialized")
        else:
            print("⚠ FAISS not available - using fallback memory")
        
        print("✓ Agent manager initialized with agents:", list(agent_manager.agents.keys()))
        
    except Exception as e:
        print(f"⚠ Startup warning: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    try:
        memory_manager.shutdown()
        print("✓ Memory saved")
    except Exception as e:
        print(f"Shutdown error: {e}")

# Create FastAPI app
app = FastAPI(
    title="Emotional AI Assistant",
    description="Voice assistant with emotional intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket_handler.handle_connection(websocket, "/ws")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "firebase": firebase_client.db is not None,
        "memory": memory_manager.encoder is not None,
        "agents": len(agent_manager.agents)
    }

# Get available agents
@app.get("/agents")
async def get_agents():
    try:
        agents = agent_manager.get_all_agents()
        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get agent details
@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    try:
        agent = agent_manager.get_agent(agent_id)
        if agent:
            return {"agent": agent}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User profile endpoints (requires authentication)
@app.get("/user/profile")
async def get_user_profile(user_id: str):
    try:
        profile = firebase_client.get_user_profile(user_id)
        if profile:
            return {"profile": profile}
        else:
            return {"profile": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/profile")
async def update_user_profile(user_id: str, profile_data: dict):
    try:
        success = firebase_client.update_user_profile(user_id, profile_data)
        if success:
            return {"status": "updated"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update profile")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat history endpoint
@app.get("/user/history")
async def get_chat_history(user_id: str, limit: int = 10):
    try:
        history = firebase_client.get_chat_history(user_id, limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Memory stats endpoint
@app.get("/user/memory-stats")
async def get_memory_stats(user_id: str):
    try:
        count = memory_manager.get_user_memory_count(user_id)
        return {"memory_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Clear user memories
@app.delete("/user/memories")
async def clear_user_memories(user_id: str):
    try:
        success = memory_manager.clear_user_memories(user_id)
        if success:
            return {"status": "cleared"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear memories")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Emotional AI Assistant Backend",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws",
            "health": "/health",
            "agents": "/agents",
            "documentation": "/docs"
        }
    }

# Error handlers
@app.exception_handler(WebSocketDisconnect)
async def websocket_disconnect_handler(request, exc):
    print("WebSocket disconnected")

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
