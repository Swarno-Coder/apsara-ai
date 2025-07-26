import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Dict, List, Optional
import json
import config

class FirebaseInterface:
    def __init__(self, credentials_path: str = config.FIREBASE_CREDENTIALS_PATH):
        self.credentials_path = credentials_path
        self.db = None
        self.project_id = config.FIREBASE_PROJECT_ID
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                if self.credentials_path and self.credentials_path != "":
                    cred = credentials.Certificate(self.credentials_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': self.project_id
                    })
                else:
                    # Use default credentials (for deployed environments)
                    firebase_admin.initialize_app()
                
            self.db = firestore.client()
            print("Firebase initialized successfully")
            
        except Exception as e:
            print(f"Firebase initialization error: {e}")
            self.db = None
    
    def verify_user_token(self, token: str) -> Optional[Dict]:
        """Verify Firebase ID token and return user info"""
        try:
            decoded_token = auth.verify_id_token(token)
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email', ''),
                'name': decoded_token.get('name', '')
            }
        except Exception as e:
            print(f"Token verification error: {e}")
            return None
    
    def store_chat_message(self, user_id: str, message: Dict) -> bool:
        """Store chat message in Firestore"""
        try:
            if not self.db:
                return False
                
            self.db.collection('users').document(user_id).collection('chats').add(message)
            return True
            
        except Exception as e:
            print(f"Error storing chat message: {e}")
            return False
    
    def get_chat_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve chat history for user"""
        try:
            if not self.db:
                return []
                
            docs = (self.db.collection('users')
                   .document(user_id)
                   .collection('chats')
                   .order_by('timestamp', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
            
            messages = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                messages.append(data)
                
            return list(reversed(messages))  # Return in chronological order
            
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            return []
    
    def store_user_memory(self, user_id: str, memory_data: Dict) -> bool:
        """Store user memory/context data"""
        try:
            if not self.db:
                return False
                
            self.db.collection('users').document(user_id).collection('memories').add(memory_data)
            return True
            
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def get_user_memories(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Retrieve user memories"""
        try:
            if not self.db:
                return []
                
            docs = (self.db.collection('users')
                   .document(user_id)
                   .collection('memories')
                   .order_by('timestamp', direction=firestore.Query.DESCENDING)
                   .limit(limit)
                   .stream())
            
            memories = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                memories.append(data)
                
            return memories
            
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile data"""
        try:
            if not self.db:
                return None
                
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            print(f"Error retrieving user profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user profile"""
        try:
            if not self.db:
                return False
                
            self.db.collection('users').document(user_id).set(profile_data, merge=True)
            return True
            
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def get_available_agents(self) -> List[Dict]:
        """Get list of available AI agents"""
        try:
            if not self.db:
                return self._get_default_agents()
                
            docs = self.db.collection('agents').stream()
            agents = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                agents.append(data)
                
            return agents if agents else self._get_default_agents()
            
        except Exception as e:
            print(f"Error retrieving agents: {e}")
            return self._get_default_agents()
    
    def _get_default_agents(self) -> List[Dict]:
        """Return default agents if Firestore is unavailable"""
        return [
            {
                'id': 'friendly_assistant',
                'name': 'Friendly Assistant',
                'personality': 'friendly and empathetic',
                'description': 'A warm and understanding AI companion'
            },
            {
                'id': 'professional_advisor',
                'name': 'Professional Advisor',
                'personality': 'professional and knowledgeable',
                'description': 'Expert advice and guidance'
            }
        ]

# Global instance
firebase_client = FirebaseInterface()
