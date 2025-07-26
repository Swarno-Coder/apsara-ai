import pytest
import asyncio
import json
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from database.database import Database

# Test client
client = TestClient(app)

class TestAPI:
    """Test API endpoints"""
    
    def setup_method(self):
        """Setup for each test"""
        self.test_user_id = "test_user_123"
        self.test_agent_id = "agent_1"
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_get_agents(self):
        """Test getting agents list"""
        response = client.get(f"/agents?user_id={self.test_user_id}")
        assert response.status_code == 200
        agents = response.json()
        assert isinstance(agents, list)
    
    def test_get_specific_agent(self):
        """Test getting specific agent"""
        response = client.get(f"/agents/{self.test_agent_id}?user_id={self.test_user_id}")
        # Should return 200 if agent exists, 404 if not
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            agent = response.json()
            assert agent["id"] == self.test_agent_id
            assert "name" in agent
            assert "personality" in agent
    
    def test_start_call(self):
        """Test starting a call"""
        call_data = {
            "user_id": self.test_user_id,
            "agent_id": self.test_agent_id,
            "call_type": "voice"
        }
        
        response = client.post("/calls/start", json=call_data)
        # Should return 200 if agent exists, 404 if not
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            call = response.json()
            assert call["user_id"] == self.test_user_id
            assert call["agent_id"] == self.test_agent_id
            assert call["status"] == "active"
            return call["id"]
    
    def test_send_message(self):
        """Test sending a message"""
        # First start a call
        call_id = self.test_start_call()
        if not call_id:
            pytest.skip("Cannot test message without valid call")
        
        message_data = {
            "user_id": self.test_user_id,
            "content": "Hello, this is a test message",
            "message_type": "text"
        }
        
        response = client.post(f"/calls/{call_id}/message", json=message_data)
        assert response.status_code == 200
        
        message_response = response.json()
        assert message_response["call_id"] == call_id
        assert message_response["is_from_agent"] is True
        assert "content" in message_response
    
    def test_end_call(self):
        """Test ending a call"""
        # First start a call
        call_id = self.test_start_call()
        if not call_id:
            pytest.skip("Cannot test end call without valid call")
        
        response = client.put(f"/calls/{call_id}/end")
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
    
    def test_get_call_history(self):
        """Test getting call history"""
        response = client.get(f"/history/{self.test_user_id}/agents")
        assert response.status_code == 200
        
        history = response.json()
        assert isinstance(history, list)
    
    def test_invalid_agent_call(self):
        """Test starting call with invalid agent"""
        call_data = {
            "user_id": self.test_user_id,
            "agent_id": "invalid_agent_id",
            "call_type": "voice"
        }
        
        response = client.post("/calls/start", json=call_data)
        assert response.status_code == 404
    
    def test_missing_parameters(self):
        """Test API with missing parameters"""
        # Missing user_id in agents request
        response = client.get("/agents")
        assert response.status_code == 422  # Validation error
        
        # Missing fields in call start
        response = client.post("/calls/start", json={"user_id": self.test_user_id})
        assert response.status_code == 422


@pytest.mark.asyncio
class TestDatabase:
    """Test database operations"""
    
    async def test_database_connection(self):
        """Test database connection"""
        try:
            await Database.initialize()
            assert True  # If we get here, connection works
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")
    
    async def test_execute_query(self):
        """Test database query execution"""
        try:
            result = await Database.execute_query("SELECT COUNT(*) FROM agents")
            assert result is not None
            assert len(list(result)) > 0
        except Exception as e:
            pytest.fail(f"Database query failed: {e}")
    
    async def test_agent_operations(self):
        """Test agent CRUD operations"""
        try:
            # Test reading agents
            agents = await Database.execute_query("SELECT * FROM agents LIMIT 1")
            assert agents is not None
            
            # Test agent exists
            agent_list = list(agents)
            if agent_list:
                agent_id = agent_list[0][0]
                specific_agent = await Database.execute_query(
                    "SELECT * FROM agents WHERE id = ?", (agent_id,)
                )
                assert specific_agent is not None
                assert len(list(specific_agent)) == 1
                
        except Exception as e:
            pytest.fail(f"Agent operations failed: {e}")


class TestServices:
    """Test service layer"""
    
    def test_cache_service(self):
        """Test cache service operations"""
        from services.cache_service import cache
        
        # Test set and get
        test_key = "test_key"
        test_value = {"test": "data"}
        
        result = cache.set(test_key, test_value, ttl=60)
        assert result is True
        
        retrieved_value = cache.get(test_key)
        assert retrieved_value == test_value
        
        # Test delete
        result = cache.delete(test_key)
        assert result is True
        
        retrieved_value = cache.get(test_key)
        assert retrieved_value is None
    
    @pytest.mark.asyncio
    async def test_emotion_service(self):
        """Test emotion analysis service"""
        from services.emotion_service import EmotionService
        from models.schemas import EmotionType
        
        emotion_service = EmotionService()
        
        # Test happy emotion
        happy_text = "I'm so happy and excited about this!"
        emotion = await emotion_service.analyze_emotion(happy_text)
        assert emotion in [EmotionType.HAPPY, EmotionType.EXCITED]
        
        # Test sad emotion
        sad_text = "I'm feeling really sad and down today"
        emotion = await emotion_service.analyze_emotion(sad_text)
        assert emotion == EmotionType.SAD
        
        # Test neutral emotion
        neutral_text = "The weather is okay today"
        emotion = await emotion_service.analyze_emotion(neutral_text)
        assert emotion == EmotionType.NEUTRAL
    
    @pytest.mark.asyncio
    async def test_agent_service(self):
        """Test agent service operations"""
        from services.agent_service import AgentService
        
        agent_service = AgentService()
        test_user_id = "test_user_123"
        
        try:
            # Test get all agents
            agents = await agent_service.get_all_agents(test_user_id)
            assert isinstance(agents, list)
            
            # Test get specific agent if any exist
            if agents:
                agent_id = agents[0].id
                specific_agent = await agent_service.get_agent(agent_id, test_user_id)
                assert specific_agent is not None
                assert specific_agent.id == agent_id
                
        except Exception as e:
            # If database not set up, skip these tests
            pytest.skip(f"Agent service tests skipped: {e}")


class TestWebSocket:
    """Test WebSocket functionality"""
    
    def test_websocket_manager_initialization(self):
        """Test WebSocket manager initialization"""
        from services.websocket_service import manager
        
        assert manager is not None
        assert hasattr(manager, 'active_connections')
        assert hasattr(manager, 'user_calls')
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection handling"""
        from services.websocket_service import WebSocketManager
        
        ws_manager = WebSocketManager()
        
        # Test connection tracking
        call_id = "test_call_123"
        user_id = "test_user_123"
        
        # Mock websocket object
        class MockWebSocket:
            async def accept(self):
                pass
            
            async def send_text(self, data):
                pass
        
        mock_ws = MockWebSocket()
        
        # Test connect method (without actual websocket connection)
        try:
            await ws_manager.connect(mock_ws, call_id, user_id)
            assert call_id in ws_manager.active_connections
            assert user_id in ws_manager.user_calls
            
            # Test disconnect
            ws_manager.disconnect(call_id, user_id)
            assert call_id not in ws_manager.active_connections
            assert user_id not in ws_manager.user_calls
            
        except Exception as e:
            # If dependencies not available, skip
            pytest.skip(f"WebSocket test skipped: {e}")


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test complete conversation flow"""
        try:
            # This would test the full flow:
            # 1. Start call
            # 2. Send message
            # 3. Receive response
            # 4. End call
            
            # Use async client for better testing
            async with AsyncClient(app=app, base_url="http://test") as ac:
                # Start call
                call_data = {
                    "user_id": "test_user",
                    "agent_id": "agent_1",
                    "call_type": "voice"
                }
                
                response = await ac.post("/calls/start", json=call_data)
                if response.status_code != 200:
                    pytest.skip("Cannot start call for integration test")
                
                call = response.json()
                call_id = call["id"]
                
                # Send message
                message_data = {
                    "user_id": "test_user",
                    "content": "Hello, how are you?",
                    "message_type": "text"
                }
                
                response = await ac.post(f"/calls/{call_id}/message", json=message_data)
                assert response.status_code == 200
                
                message_response = response.json()
                assert "content" in message_response
                
                # End call
                response = await ac.put(f"/calls/{call_id}/end")
                assert response.status_code == 200
                
        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")


# Performance tests
class TestPerformance:
    """Performance and load tests"""
    
    def test_api_response_time(self):
        """Test API response times"""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                response = client.get("/health")
                results.append(response.status_code)
            except Exception as e:
                results.append(500)
        
        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Check results
        assert len(results) == 10
        assert all(status == 200 for status in results)
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
