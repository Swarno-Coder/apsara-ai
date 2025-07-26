import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple, Optional, Union
from sentence_transformers import SentenceTransformer
from datetime import datetime
import config

class FAISSMemoryManager:
    def __init__(self, index_path: str = config.FAISS_INDEX_PATH):
        self.index_path = index_path
        self.embedding_dimension = config.EMBEDDING_DIMENSION
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict] = []
        self.encoder: Optional[SentenceTransformer] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize FAISS index and sentence transformer"""
        try:
            # Initialize sentence transformer for embeddings
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dimension = self.encoder.get_sentence_embedding_dimension()
            
            # Create or load FAISS index
            if os.path.exists(f"{self.index_path}.index"):
                self._load_index()
            else:
                self._create_new_index()
                
            print(f"FAISS memory manager initialized with dimension {self.embedding_dimension}")
            
        except Exception as e:
            print(f"FAISS initialization error: {e}")
            self._create_fallback_index()
    
    def _create_new_index(self):
        """Create new FAISS index"""
        self.index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner product for similarity
        self.metadata = []
    
    def _create_fallback_index(self):
        """Create fallback index if imports fail"""
        self.index = None
        self.metadata = []
        self.encoder = None
        print("Using fallback mode - FAISS memory features disabled")
    
    def _load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            self.index = faiss.read_index(f"{self.index_path}.index")
            
            # Check if metadata file exists
            metadata_path = f"{self.index_path}.metadata"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                self.metadata = []
                
            if self.index is not None:
                print(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            self._create_new_index()
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            # Ensure directory exists
            index_dir = os.path.dirname(self.index_path)
            if index_dir:
                os.makedirs(index_dir, exist_ok=True)
            
            # Save FAISS index
            if self.index is not None:
                faiss.write_index(self.index, f"{self.index_path}.index")
            
            # Save metadata
            with open(f"{self.index_path}.metadata", 'wb') as f:
                pickle.dump(self.metadata, f)
                
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
    
    def add_memory(self, text: str, user_id: str, emotion: str = "neutral", 
                   additional_metadata: Optional[Dict] = None) -> bool:
        """Add memory to FAISS index"""
        try:
            if not self.encoder or not self.index:
                print("FAISS encoder or index not available")
                return False
            
            # Generate embedding
            embedding = self.encoder.encode([text])[0]
            embedding = embedding / np.linalg.norm(embedding)  # Normalize
            
            # Add to index
            if self.index is not None:
                vectors = np.array([embedding], dtype=np.float32)
                self.index.add(vectors)
            
            # Store metadata
            metadata = {
                'text': text,
                'user_id': user_id,
                'emotion': emotion,
                'timestamp': datetime.now().isoformat()  # Fixed: Use datetime.now().isoformat()
            }
            
            if additional_metadata:
                metadata.update(additional_metadata)
                
            self.metadata.append(metadata)
            
            # Save periodically
            if len(self.metadata) % 10 == 0:
                self._save_index()
            
            return True
            
        except Exception as e:
            print(f"Error adding memory: {e}")
            return False
    
    def search_memories(self, query: str, user_id: str, top_k: Optional[int] = None) -> List[Dict]:
        """Search for relevant memories"""
        try:
            # Use default from config if not provided
            effective_top_k: int = top_k if top_k is not None else getattr(config, 'TOP_K_MEMORIES', 5)
                
            if not self.encoder or not self.index or self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.encoder.encode([query])[0]
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search FAISS index
            search_k = min(effective_top_k * 2, self.index.ntotal)  # Get more results to filter by user
            scores, indices = self.index.search(
                np.array([query_embedding], dtype=np.float32), 
                search_k
            )
            
            # Filter by user and return results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                # Fixed: Check for valid index
                if idx >= 0 and idx < len(self.metadata):
                    metadata = self.metadata[idx].copy()  # Make a copy to avoid modifying original
                    if metadata['user_id'] == user_id:
                        metadata['similarity_score'] = float(score)
                        results.append(metadata)
                        
                        if len(results) >= effective_top_k:
                            break
            
            return results
            
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def get_user_memory_count(self, user_id: str) -> int:
        """Get number of memories for a user"""
        try:
            return sum(1 for meta in self.metadata if meta.get('user_id') == user_id)
        except Exception as e:
            print(f"Error getting user memory count: {e}")
            return 0
    
    def clear_user_memories(self, user_id: str) -> bool:
        """Clear all memories for a specific user"""
        try:
            if not self.encoder:
                print("FAISS encoder not available")
                return False
                
            # Find memories to keep
            new_metadata = []
            memories_removed = 0
            
            for meta in self.metadata:
                if meta.get('user_id') != user_id:
                    new_metadata.append(meta)
                else:
                    memories_removed += 1
            
            if memories_removed > 0:
                print(f"Removing {memories_removed} memories for user {user_id}")
                
                # Rebuild index with remaining memories
                self._create_new_index()
                
                if new_metadata:
                    embeddings = []
                    for meta in new_metadata:
                        try:
                            embedding = self.encoder.encode([meta['text']])[0]
                            embedding = embedding / np.linalg.norm(embedding)
                            embeddings.append(embedding)
                        except Exception as e:
                            print(f"Error re-encoding memory: {e}")
                            continue
                    
                    if embeddings and self.index is not None:
                        vectors = np.array(embeddings, dtype=np.float32)
                        self.index.add(vectors)
                
                self.metadata = new_metadata
                self._save_index()
                print(f"Successfully removed {memories_removed} memories")
            
            return True
            
        except Exception as e:
            print(f"Error clearing user memories: {e}")
            return False
    
    def get_all_user_memories(self, user_id: str) -> List[Dict]:
        """Get all memories for a specific user"""
        try:
            return [meta.copy() for meta in self.metadata if meta.get('user_id') == user_id]
        except Exception as e:
            print(f"Error getting all user memories: {e}")
            return []
    
    def cleanup_old_memories(self, days_old: int = 30) -> int:
        """Remove memories older than specified days"""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            new_metadata = []
            removed_count = 0
            
            for meta in self.metadata:
                try:
                    memory_date = datetime.fromisoformat(meta['timestamp'])
                    if memory_date > cutoff_date:
                        new_metadata.append(meta)
                    else:
                        removed_count += 1
                except Exception:
                    # Keep memories with invalid timestamps
                    new_metadata.append(meta)
            
            if removed_count > 0:
                # Rebuild index
                self._rebuild_index_from_metadata(new_metadata)
                print(f"Cleaned up {removed_count} old memories")
            
            return removed_count
            
        except Exception as e:
            print(f"Error cleaning up old memories: {e}")
            return 0
    
    def _rebuild_index_from_metadata(self, new_metadata: List[Dict]):
        """Helper method to rebuild index from metadata"""
        try:
            self._create_new_index()
            
            if new_metadata and self.encoder:
                embeddings = []
                valid_metadata = []
                
                for meta in new_metadata:
                    try:
                        embedding = self.encoder.encode([meta['text']])[0]
                        embedding = embedding / np.linalg.norm(embedding)
                        embeddings.append(embedding)
                        valid_metadata.append(meta)
                    except Exception as e:
                        print(f"Error re-encoding memory: {e}")
                        continue
                
                if embeddings and self.index is not None:
                    vectors = np.array(embeddings, dtype=np.float32)
                    self.index.add(vectors)
                
                self.metadata = valid_metadata
                self._save_index()
                
        except Exception as e:
            print(f"Error rebuilding index: {e}")
    
    def shutdown(self):
        """Save index before shutdown"""
        try:
            self._save_index()
            print("FAISS memory manager shutdown complete")
        except Exception as e:
            print(f"Error during shutdown: {e}")

# Global instance
memory_manager = FAISSMemoryManager()
