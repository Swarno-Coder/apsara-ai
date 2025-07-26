import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_agents_endpoint():
    """Test the agents list endpoint"""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) > 0

def test_agent_detail_endpoint():
    """Test getting specific agent details"""
    response = client.get("/agents/friendly_assistant")
    assert response.status_code == 200
    data = response.json()
    assert "agent" in data
    
    # Test invalid agent
    response = client.get("/agents/invalid_agent")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection"""
    with client.websocket_connect("/ws") as websocket:
        # Connection should be established
        assert websocket is not None
        
        # Test sending a message
        test_message = {
            "type": "get_agents"
        }
        websocket.send_json(test_message)
        
        # Should receive agents list
        response = websocket.receive_json()
        assert response["type"] == "agents_list"
        assert "agents" in response
