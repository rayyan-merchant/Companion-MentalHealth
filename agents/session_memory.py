from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from pathlib import Path

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False
    print("Warning: qdrant-client not installed. Vector memory disabled.")


@dataclass
class MemoryEntry:
    turn_id: int
    timestamp: str
    raw_text: str
    emotions: List[str] = field(default_factory=list)
    symptoms: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    inferred_states: List[str] = field(default_factory=list)
    confidence: str = "low"


@dataclass
class SessionContext:
    session_id: str
    turn_count: int
    accumulated_emotions: List[str] = field(default_factory=list)
    accumulated_symptoms: List[str] = field(default_factory=list)
    accumulated_triggers: List[str] = field(default_factory=list)
    repeated_patterns: List[str] = field(default_factory=list)
    persistence_detected: bool = False
    similar_past_messages: List[str] = field(default_factory=list)


class SessionMemoryAgent:
    
    VECTOR_SIZE = 384  # Consistent with embedding model
    
    def __init__(self, session_id: str, persist_dir: Optional[str] = None):
        self.session_id = session_id
        self.turn_count = 0
        self.memory: List[MemoryEntry] = []
        
        self._accumulated = {
            "emotions": [],
            "symptoms": [],
            "triggers": []
        }
        
        self.client = None
        self.collection_name = f"session_{self.session_id}"
        
        if VECTOR_STORE_AVAILABLE:
            self._init_vector_store()
    
    def _init_vector_store(self):
        try:
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_key = os.getenv("QDRANT_API_KEY")
            
            if qdrant_url and qdrant_key:
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
                # Ensure session collection exists
                collections = self.client.get_collections().collections
                names = [c.name for c in collections]
                
                if self.collection_name not in names:
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=self.VECTOR_SIZE,
                            distance=Distance.COSINE
                        )
                    )
            else:
                self.client = None
                
        except Exception as e:
            print(f"Failed to initialize session vector store: {e}")
            self.client = None
    
    def add_turn(
        self,
        raw_text: str,
        extraction_result: Dict[str, Any],
        inferred_states: List[str] = None,
        confidence: str = "low"
    ) -> MemoryEntry:

        self.turn_count += 1
        
        # Extract labels from structured signals
        emotions = [e["label"] for e in extraction_result.get("emotions", [])]
        symptoms = [s["label"] for s in extraction_result.get("symptoms", [])]
        triggers = [t["label"] for t in extraction_result.get("triggers", [])]
        
        entry = MemoryEntry(
            turn_id=self.turn_count,
            timestamp=datetime.utcnow().isoformat() + "Z",
            raw_text=raw_text,
            emotions=emotions,
            symptoms=symptoms,
            triggers=triggers,
            inferred_states=inferred_states or [],
            confidence=confidence
        )
        
        self.memory.append(entry)
        
        # Accumulate signals
        self._accumulated["emotions"].extend(emotions)
        self._accumulated["symptoms"].extend(symptoms)
        self._accumulated["triggers"].extend(triggers)
        
        # Add to vector store if available
        if self.client:
            self._add_to_vector_store(entry)
        
        return entry

    def hydrate(self, messages: List[Dict[str, Any]]):
        """
        Re-populate memory from persistent message history.
        This handles server restarts/statelessness.
        """
        from agents.ml_extractor import extract_signals # Import here to avoid circular dependencies
        
        # Clear current volatile memory
        self.memory = []
        self.turn_count = 0
        self._accumulated = {"emotions": [], "symptoms": [], "triggers": []}
        
        # Process messages in order
        for i, msg in enumerate(messages):
            if msg.get("role") == "user":
                user_text = msg.get("content", "")
                
                # Check if there is a corresponding assistant response
                assistant_data = {}
                if i + 1 < len(messages) and messages[i+1].get("role") == "assistant":
                    meta = messages[i+1].get("metadata", {}) or {}
                    assistant_data = {
                        "state": meta.get("state"),
                        "confidence": meta.get("confidence", "low")
                    }
                
                # Re-extract
                extraction = extract_signals(user_text)
                
                # Add back to memory
                self.add_turn(
                    raw_text=user_text,
                    extraction_result=extraction,
                    inferred_states=[assistant_data.get("state")] if assistant_data.get("state") else [],
                    confidence=assistant_data.get("confidence", "low")
                )

    def get_formatted_history(self, limit: int = 5) -> str:
        """Get recent conversation history formatted for LLM context."""
        history_lines = []
        recent_turns = self.memory[-limit:]
        for turn in recent_turns:
            history_lines.append(f"User: {turn.raw_text}")
            
        return "\n".join(history_lines)

    
    def _add_to_vector_store(self, entry: MemoryEntry):
        try:
            # We need an embedding for the text
            from agents.embedding_providers import get_embedding
            
            embedding = get_embedding(entry.raw_text)
            if not embedding:
                return

            # Normalize dimensions if needed
            if len(embedding) != self.VECTOR_SIZE:
                 if len(embedding) > self.VECTOR_SIZE:
                     embedding = embedding[:self.VECTOR_SIZE]
                 else:
                     embedding = embedding + [0.0] * (self.VECTOR_SIZE - len(embedding))
            
            payload = {
                "turn_id": entry.turn_id,
                "raw_text": entry.raw_text,
                "emotions": ",".join(entry.emotions),
                "symptoms": ",".join(entry.symptoms),
                "triggers": ",".join(entry.triggers),
                "timestamp": entry.timestamp
            }
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[PointStruct(
                    id=entry.turn_id,
                    vector=embedding,
                    payload=payload
                )]
            )
        except Exception as e:
            print(f"Failed to add to session vector store: {e}")
    
    def get_context(self) -> SessionContext:

        unique_emotions = list(set(self._accumulated["emotions"]))
        unique_symptoms = list(set(self._accumulated["symptoms"]))
        unique_triggers = list(set(self._accumulated["triggers"]))
        
        repeated = self._detect_repeated_patterns()
        
        persistence = len(repeated) > 0
        
        return SessionContext(
            session_id=self.session_id,
            turn_count=self.turn_count,
            accumulated_emotions=unique_emotions,
            accumulated_symptoms=unique_symptoms,
            accumulated_triggers=unique_triggers,
            repeated_patterns=repeated,
            persistence_detected=persistence,
            similar_past_messages=[]  # Populated by retrieve_similar? Or handled by caller.
        )
    
    def _detect_repeated_patterns(self) -> List[str]:
        from collections import Counter
        
        all_signals = []
        for entry in self.memory:
            all_signals.extend(entry.emotions)
            all_signals.extend(entry.symptoms)
            all_signals.extend(entry.triggers)
        
        counts = Counter(all_signals)
        return [signal for signal, count in counts.items() if count >= 2]
    
    def retrieve_similar(self, query: str, n_results: int = 3) -> List[str]:

        if not self.client or self.turn_count == 0:
            return []
        
        try:
            # Generate query embedding
            from agents.embedding_providers import get_embedding
            query_embedding = get_embedding(query)
            if not query_embedding:
                return []
                
            # Normalize dimensions
            if len(query_embedding) != self.VECTOR_SIZE:
                 if len(query_embedding) > self.VECTOR_SIZE:
                     query_embedding = query_embedding[:self.VECTOR_SIZE]
                 else:
                     query_embedding = query_embedding + [0.0] * (self.VECTOR_SIZE - len(query_embedding))
            
            # Use query_points for search
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=n_results
            )
            
            # Extract text from payload
            return [point.payload.get("raw_text", "") for point in results.points]
            
        except Exception as e:
            print(f"Similarity retrieval failed: {e}")
            return []
    
    def get_memory_summary(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "total_emotions": len(self._accumulated["emotions"]),
            "total_symptoms": len(self._accumulated["symptoms"]),
            "total_triggers": len(self._accumulated["triggers"]),
            "unique_emotions": list(set(self._accumulated["emotions"])),
            "unique_symptoms": list(set(self._accumulated["symptoms"])),
            "unique_triggers": list(set(self._accumulated["triggers"])),
            "repeated_patterns": self._detect_repeated_patterns()
        }


_sessions: Dict[str, SessionMemoryAgent] = {}


def get_session(session_id: str, persist_dir: Optional[str] = None) -> SessionMemoryAgent:
    if session_id not in _sessions:
        _sessions[session_id] = SessionMemoryAgent(session_id, persist_dir)
    return _sessions[session_id]


def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]


if __name__ == "__main__":
    print("Session Memory Agent Test (Qdrant)")
    print("=" * 60)
    
    # Needs valid .env with QDRANT_API_KEY
    from dotenv import load_dotenv
    load_dotenv()
    
    session = get_session("test_session_001")
    
    turns = [
        ("I feel anxious today", {"emotions": [{"label": "anxiety"}], "symptoms": [], "triggers": []}),
        ("Finals are next week", {"emotions": [], "symptoms": [], "triggers": [{"label": "academic"}]}),
        ("I can't sleep because of the stress", {"emotions": [{"label": "stress"}], "symptoms": [{"label": "insomnia"}], "triggers": []})
    ]
    
    for text, extraction in turns:
        session.add_turn(text, extraction)
        print(f"\nAdded: {text}")
    
    context = session.get_context()
    print(f"\n--- Session Context ---")
    print(f"Turn count: {context.turn_count}")
    print(f"Accumulated emotions: {context.accumulated_emotions}")
    print(f"Repeated patterns: {context.repeated_patterns}")
    
    # Test retrieval
    print("\nSimilar to 'exam stress':")
    similar = session.retrieve_similar("exam stress")
    for s in similar:
        print(f"- {s}")
