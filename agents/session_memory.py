from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False
    print("Warning: chromadb not installed. Vector memory disabled.")


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

    
    def __init__(self, session_id: str, persist_dir: Optional[str] = None):
        self.session_id = session_id
        self.turn_count = 0
        self.memory: List[MemoryEntry] = []
        
        self._accumulated = {
            "emotions": [],
            "symptoms": [],
            "triggers": []
        }
        
        self.vector_store = None
        self.collection = None
        if VECTOR_STORE_AVAILABLE and persist_dir:
            self._init_vector_store(persist_dir)
    
    def _init_vector_store(self, persist_dir: str):
        try:
            self.vector_store = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_dir,
                anonymized_telemetry=False
            ))
            self.collection = self.vector_store.get_or_create_collection(
                name=f"session_{self.session_id}",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Failed to initialize vector store: {e}")
            self.vector_store = None
    
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
        if self.collection:
            self._add_to_vector_store(entry)
        
        return entry

    def hydrate(self, messages: List[Dict[str, Any]]):
        """
        Re-populate memory from persistent message history.
        This handles server restarts/statelessness.
        """
        from agents.ml_extractor import extract_signals # Import here to avoid circular dependencies if any
        
        # Clear current volatile memory
        self.memory = []
        self.turn_count = 0
        self._accumulated = {"emotions": [], "symptoms": [], "triggers": []}
        
        # Process messages in order
        # We need to pair User input with Bot response (for metadata)
        
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
                
                # Re-extract (fast)
                extraction = extract_signals(user_text)
                
                # Add back to memory
                self.add_turn(
                    raw_text=user_text,
                    extraction_result=extraction,
                    inferred_states=[assistant_data.get("state")] if assistant_data.get("state") else [],
                    confidence=assistant_data.get("confidence", "low")
                )

    def hydrate(self, messages: List[Dict[str, Any]]):
        """
        Re-populate memory from persistent message history.
        This handles server restarts/statelessness.
        """
        from agents.ml_extractor import extract_signals # Import here to avoid circular dependencies if any
        
        # Clear current volatile memory
        self.memory = []
        self.turn_count = 0
        self._accumulated = {"emotions": [], "symptoms": [], "triggers": []}
        
        # Process messages in order
        # We need to pair User input with Bot response (for metadata)
        
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
                
                # Re-extract (fast)
                extraction = extract_signals(user_text)
                
                # Add back to memory
                self.add_turn(
                    raw_text=user_text,
                    extraction_result=extraction,
                    inferred_states=[assistant_data.get("state")] if assistant_data.get("state") else [],
                    confidence=assistant_data.get("confidence", "low")
                )
    
    def _add_to_vector_store(self, entry: MemoryEntry):
        try:
            self.collection.add(
                documents=[entry.raw_text],
                metadatas=[{
                    "turn_id": entry.turn_id,
                    "emotions": ",".join(entry.emotions),
                    "symptoms": ",".join(entry.symptoms),
                    "triggers": ",".join(entry.triggers)
                }],
                ids=[f"turn_{entry.turn_id}"]
            )
        except Exception as e:
            print(f"Failed to add to vector store: {e}")
    
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
            similar_past_messages=[]  # Populated by retrieve_similar
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

        if not self.collection or self.turn_count == 0:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.turn_count)
            )
            return results.get("documents", [[]])[0]
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
    print("Session Memory Agent Test")
    print("=" * 60)
    
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
    print(f"Accumulated symptoms: {context.accumulated_symptoms}")
    print(f"Accumulated triggers: {context.accumulated_triggers}")
    print(f"Repeated patterns: {context.repeated_patterns}")
    print(f"Persistence detected: {context.persistence_detected}")
