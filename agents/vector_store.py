"""
Qdrant Cloud Vector Store Integration

Features:
- Persistent storage of concept embeddings (no recompute on restart)
- Fast similarity search for user queries
- Automatic initialization with concept vocabulary
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        PointStruct,
        VectorParams,
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("[VectorStore] WARNING: qdrant-client not installed. Using in-memory fallback.")


# Import concept definitions
from agents.ml_extractor import EMOTION_CONCEPTS, SYMPTOM_CONCEPTS, TRIGGER_CONCEPTS


@dataclass
class SimilarConcept:
    """Result from similarity search."""
    label: str
    category: str  # emotion, symptom, trigger
    phrase: str
    score: float


class QdrantVectorStore:
    """
    Production vector store using Qdrant Cloud.
    
    Pre-caches all concept embeddings for instant similarity search.
    Falls back to in-memory store if Qdrant is unavailable.
    
    NEW: Also caches user text embeddings to avoid redundant API calls.
    """
    
    COLLECTION_NAME = "mental_health_concepts"
    CACHE_COLLECTION_NAME = "embedding_cache"
    VECTOR_SIZE = 384  # HuggingFace all-MiniLM-L6-v2 dimension
    
    def __init__(self):
        self.client = None
        self.in_memory_store: Dict[str, Dict[str, Any]] = {}
        self.in_memory_cache: Dict[str, List[float]] = {}  # text_hash -> embedding
        self.use_cloud = False
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Try to connect to Qdrant Cloud
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_key = os.getenv("QDRANT_API_KEY")
        
        if QDRANT_AVAILABLE and qdrant_url and qdrant_key:
            try:
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
                # Test connection
                self.client.get_collections()
                self.use_cloud = True
                print("[VectorStore] Connected to Qdrant Cloud")
                self._ensure_collections()
            except Exception as e:
                print(
                    "[VectorStore] Qdrant connection failed "
                    f"({type(e).__name__}). Using in-memory."
                )
        else:
            print("[VectorStore] No Qdrant credentials. Using in-memory store.")
    
    def _ensure_collections(self):
        """Create collections if they don't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        # Main concepts collection
        if self.COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            print(f"[VectorStore] Created collection: {self.COLLECTION_NAME}")
        
        # Embedding cache collection
        if self.CACHE_COLLECTION_NAME not in collection_names:
            self.client.create_collection(
                collection_name=self.CACHE_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            print(f"[VectorStore] Created cache collection: {self.CACHE_COLLECTION_NAME}")
    
    def _text_hash(self, text: str) -> int:
        """Generate a consistent hash for text (used as point ID)."""
        import hashlib
        # Use MD5 for speed, truncate to positive int for Qdrant ID
        h = hashlib.md5(text.lower().strip().encode()).hexdigest()
        return int(h[:15], 16)  # First 15 hex chars = 60 bits, fits in int64
    
    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Check if embedding exists in cache. Returns None if not found."""
        text_hash = self._text_hash(text)
        
        # Check in-memory cache first (fastest)
        if text_hash in self.in_memory_cache:
            self._cache_hits += 1
            return self.in_memory_cache[text_hash]
        
        if self.use_cloud:
            try:
                result = self.client.retrieve(
                    collection_name=self.CACHE_COLLECTION_NAME,
                    ids=[text_hash],
                    with_vectors=True
                )
                if result and len(result) > 0:
                    embedding = result[0].vector
                    # Store in in-memory cache for faster subsequent access
                    self.in_memory_cache[text_hash] = embedding
                    self._cache_hits += 1
                    return embedding
            except Exception:
                pass  # Not found or error
        
        self._cache_misses += 1
        return None
    
    def cache_embedding(self, text: str, embedding: List[float]):
        """Store embedding in cache for future reuse."""
        text_hash = self._text_hash(text)
        
        # Normalize embedding size
        if len(embedding) != self.VECTOR_SIZE:
            if len(embedding) > self.VECTOR_SIZE:
                embedding = embedding[:self.VECTOR_SIZE]
            else:
                embedding = embedding + [0.0] * (self.VECTOR_SIZE - len(embedding))
        
        # Always store in in-memory cache
        self.in_memory_cache[text_hash] = embedding
        
        if self.use_cloud:
            try:
                self.client.upsert(
                    collection_name=self.CACHE_COLLECTION_NAME,
                    points=[PointStruct(
                        id=text_hash,
                        vector=embedding,
                        payload={"text_preview": text[:100]}  # Store preview for debugging
                    )]
                )
            except Exception as e:
                print(f"[VectorStore] Cache write failed: {e}")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Return cache hit/miss statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate_percent": round(hit_rate, 1)
        }
    
    def is_initialized(self) -> bool:
        """Check if concept embeddings are already cached."""
        if self.use_cloud:
            info = self.client.get_collection(self.COLLECTION_NAME)
            return info.points_count > 0
        return len(self.in_memory_store) > 0
    
    def initialize_concepts(self, get_embedding_fn):
        """
        Pre-compute and store all concept embeddings.
        Only runs if the store is empty.
        """
        if self.is_initialized():
            count = self.client.get_collection(self.COLLECTION_NAME).points_count if self.use_cloud else len(self.in_memory_store)
            print(f"[VectorStore] Already initialized with {count} concepts.")
            return
        
        print("[VectorStore] Initializing concept embeddings...")
        
        all_concepts = {
            "emotion": EMOTION_CONCEPTS,
            "symptom": SYMPTOM_CONCEPTS,
            "trigger": TRIGGER_CONCEPTS
        }
        
        points = []
        point_id = 0
        
        for category, concepts in all_concepts.items():
            for label, phrases in concepts.items():
                for phrase in phrases:
                    embedding = get_embedding_fn(phrase)
                    if not embedding:
                        print(f"[VectorStore] Failed to get embedding for: {phrase}")
                        continue
                    
                    # Normalize embedding size if needed (Jina/Gemini have different dimensions)
                    if len(embedding) != self.VECTOR_SIZE:
                        # Simple truncation/padding for dimension mismatch
                        if len(embedding) > self.VECTOR_SIZE:
                            embedding = embedding[:self.VECTOR_SIZE]
                        else:
                            embedding = embedding + [0.0] * (self.VECTOR_SIZE - len(embedding))
                    
                    payload = {
                        "category": category,
                        "label": label,
                        "phrase": phrase
                    }
                    
                    if self.use_cloud:
                        points.append(PointStruct(
                            id=point_id,
                            vector=embedding,
                            payload=payload
                        ))
                    else:
                        self.in_memory_store[f"{category}:{label}:{phrase}"] = {
                            "embedding": embedding,
                            **payload
                        }
                    
                    point_id += 1
        
        if self.use_cloud and points:
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=points
            )
        
        print(f"[VectorStore] Initialized {point_id} concept embeddings.")
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.5) -> List[SimilarConcept]:
        """
        Find concepts most similar to the query embedding.
        """
        # Normalize embedding size
        if len(query_embedding) != self.VECTOR_SIZE:
            if len(query_embedding) > self.VECTOR_SIZE:
                query_embedding = query_embedding[:self.VECTOR_SIZE]
            else:
                query_embedding = query_embedding + [0.0] * (self.VECTOR_SIZE - len(query_embedding))
        
        if self.use_cloud:
            # Use query_points for newer qdrant-client versions
            results = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_embedding,
                limit=top_k,
                score_threshold=threshold
            )
            
            return [
                SimilarConcept(
                    label=r.payload["label"],
                    category=r.payload["category"],
                    phrase=r.payload["phrase"],
                    score=r.score
                )
                for r in results.points
            ]
        else:
            # In-memory cosine similarity
            import math
            
            def cosine_sim(v1, v2):
                dot = sum(a*b for a, b in zip(v1, v2, strict=False))
                mag1 = math.sqrt(sum(a*a for a in v1))
                mag2 = math.sqrt(sum(b*b for b in v2))
                return dot / (mag1 * mag2) if mag1 and mag2 else 0
            
            scored = []
            for _key, data in self.in_memory_store.items():
                score = cosine_sim(query_embedding, data["embedding"])
                if score >= threshold:
                    scored.append((score, data))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            
            return [
                SimilarConcept(
                    label=data["label"],
                    category=data["category"],
                    phrase=data["phrase"],
                    score=score
                )
                for score, data in scored[:top_k]
            ]


# Singleton
_vector_store: Optional[QdrantVectorStore] = None


def get_vector_store() -> QdrantVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = QdrantVectorStore()
    return _vector_store
