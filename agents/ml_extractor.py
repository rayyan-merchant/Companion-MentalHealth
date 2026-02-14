from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import re
import json
import os
from pathlib import Path





@dataclass
class ExtractedSignal:
    label: str
    category: str  # emotion, symptom, trigger
    intensity: str = "medium"  # low, medium, high
    negated: bool = False
    temporal: Optional[str] = None  # acute, persistent, recent


@dataclass
class ExtractionResult:
    emotions: List[Dict[str, Any]] = field(default_factory=list)
    symptoms: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    intensity: str = "medium"
    negated_terms: List[str] = field(default_factory=list)
    temporal: Optional[str] = None
    raw_signals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



EMOTION_CONCEPTS = {
    "stress": ["stressed", "overwhelmed", "pressure", "tense", "burned out", "frazzled", "killing me", "stressing"],
    "anxiety": ["anxious", "nervous", "worried", "scared", "uneasy", "on edge", "dread", "restless", "racing thoughts"],
    "panic": ["panic", "panicking", "terrified", "freaking out", "terror", "heart racing", "can't breathe"],
    "sadness": ["sad", "unhappy", "down", "blue", "crying", "miserable", "empty", "hollow", "feel empty"],
    "depression": ["depressed", "hopeless", "despair", "no will to live", "pointless"],
    "irritability": ["irritated", "angry", "frustrated", "mad", "agitated"],
    "overwhelm": ["overwhelmed", "too much", "can't handle", "breaking point", "can't cope"]
}

SYMPTOM_CONCEPTS = {
    "insomnia": ["can't sleep", "sleepless", "trouble sleeping", "awake all night", "no sleep", "sleep"],
    "fatigue": ["tired", "exhausted", "no energy", "drained", "worn out", "lethargic"],
    "restlessness": ["restless", "can't sit still", "fidgeting", "pacing", "shaking", "feel restless"],
    "heart_symptoms": ["heart racing", "heart pounding", "palpitations", "chest pounding", "racing"],
    "breathing": ["can't breathe", "short of breath", "breathless", "hyperventilating"],
    "appetite": ["not eating", "no appetite", "lost appetite", "binge eating"],
    "withdrawal": ["avoiding", "isolating", "alone", "withdrawn", "hiding", "avoid everyone", "avoid"],
    "anhedonia": ["lost interest", "don't care", "nothing matters", "numb", "apathy"],
    "concentration": ["can't focus", "distracted", "brain fog", "can't concentrate"]
}

TRIGGER_CONCEPTS = {
    "academic": ["exam", "exams", "finals", "midterms", "grades", "homework", "thesis", "classes"],
    "financial": ["money", "debt", "broke", "rent", "bills", "loans", "tuition"],
    "family": ["family", "parents", "mom", "dad", "fight", "divorce", "expectations"],
    "social": ["friends", "lonely", "bullied", "relationship", "breakup", "judged"],
    "work": ["job", "boss", "deadline", "fired", "work stress", "overworked"]
}


INTENSITY_HIGH = ["extremely", "very", "so", "really", "incredibly", "severely", "killing me"]
INTENSITY_LOW = ["slightly", "a bit", "somewhat", "little", "mildly"]


NEGATION_PATTERNS = [
    r"not\s+(\w+)",
    r"don't\s+feel\s+(\w+)",
    r"don't\s+have\s+(\w+)",
    r"no\s+longer\s+(\w+)",
    r"never\s+(\w+)"
]


TEMPORAL_ACUTE = ["today", "right now", "suddenly", "just started"]
TEMPORAL_PERSISTENT = ["for weeks", "for months", "always", "constantly", "lately", "recently"]


class MLSignalExtractor:
    """
    Production-grade signal extractor with multi-provider embeddings and Qdrant caching.
    
    Architecture:
    1. Keyword matching (fast, always available)
    2. Semantic matching via embeddings (more accurate)
       - Uses multi-provider embedding service (HF -> Jina -> Gemini fallback)
       - Caches concept embeddings in Qdrant for instant startup
    """

    def __init__(self, use_embeddings: bool = True):
        self.use_embeddings = use_embeddings
        self.embedding_service = None
        self.vector_store = None
        
        if self.use_embeddings:
            self._initialize_embedding_infrastructure()
    
    def _initialize_embedding_infrastructure(self):
        """Initialize embedding providers and vector store."""
        try:
            from agents.embedding_providers import get_embedding_service, get_embedding
            from agents.vector_store import get_vector_store
            
            self.embedding_service = get_embedding_service()
            self.vector_store = get_vector_store()
            
            # Initialize concept embeddings in vector store (one-time)
            if self.vector_store and not self.vector_store.is_initialized():
                print("[MLExtractor] Initializing concept embeddings in vector store...")
                self.vector_store.initialize_concepts(get_embedding)
            
            print("[MLExtractor] Production embedding infrastructure ready.")
            
        except Exception as e:
            print(f"[MLExtractor] Failed to initialize embedding infrastructure: {e}")
            print("[MLExtractor] Falling back to keyword-only mode.")
            self.use_embeddings = False
    
    def extract(self, text: str) -> ExtractionResult:
        """Extract signals from text using keywords + semantic matching."""
        text_lower = text.lower()
        result = ExtractionResult()
        
        # Basic NLP features
        result.negated_terms = self._extract_negations(text_lower)
        result.intensity = self._detect_intensity(text_lower)
        result.temporal = self._detect_temporal(text_lower)
        
        # 1. Keyword matching (always runs)
        signals = self._extract_with_patterns(text_lower)
        
        # 2. Semantic matching (if embeddings available)
        if self.use_embeddings and self.embedding_service and self.vector_store:
            semantic_signals = self._extract_with_embeddings(text_lower)
            
            # Merge signals (avoid duplicates)
            seen_labels = {s.label for s in signals}
            for sig in semantic_signals:
                if sig.label not in seen_labels:
                    signals.append(sig)
                    seen_labels.add(sig.label)
        
        # Build result
        for signal in signals:
            signal_dict = {
                "label": signal.label,
                "intensity": result.intensity,
                "negated": signal.label in result.negated_terms,
                "temporal": result.temporal
            }
            result.raw_signals.append(signal.label)
            
            if signal.category == "emotion":
                result.emotions.append(signal_dict)
            elif signal.category == "symptom":
                result.symptoms.append(signal_dict)
            elif signal.category == "trigger":
                result.triggers.append(signal_dict)
        
        return result
    
    def _extract_with_embeddings(self, text: str) -> List[ExtractedSignal]:
        """Use embedding service + vector store for semantic matching."""
        from agents.embedding_providers import get_embedding
        
        # Get embedding for user text
        text_embedding = get_embedding(text)
        if not text_embedding:
            return []
        
        # Search vector store for similar concepts
        similar = self.vector_store.search_similar(text_embedding, top_k=5, threshold=0.5)
        
        signals = []
        seen_labels = set()
        
        for concept in similar:
            if concept.label not in seen_labels:
                signals.append(ExtractedSignal(
                    label=concept.label,
                    category=concept.category
                ))
                seen_labels.add(concept.label)
        
        return signals
    
    def _extract_negations(self, text: str) -> List[str]:
        negated = []
        for pattern in NEGATION_PATTERNS:
            matches = re.findall(pattern, text)
            negated.extend(matches)
        return negated
    
    def _detect_intensity(self, text: str) -> str:
        for marker in INTENSITY_HIGH:
            if marker in text:
                return "high"
        for marker in INTENSITY_LOW:
            if marker in text:
                return "low"
        return "medium"
    
    def _detect_temporal(self, text: str) -> Optional[str]:
        for marker in TEMPORAL_PERSISTENT:
            if marker in text:
                return "persistent"
        for marker in TEMPORAL_ACUTE:
            if marker in text:
                return "acute"
        return None
    
    def _extract_with_patterns(self, text: str) -> List[ExtractedSignal]:
        """Keyword-based extraction (fast fallback)."""
        signals = []
        seen_labels = set()
        
        all_concepts = [
            ("emotion", EMOTION_CONCEPTS),
            ("symptom", SYMPTOM_CONCEPTS),
            ("trigger", TRIGGER_CONCEPTS)
        ]
        
        for category, concepts in all_concepts:
            for label, phrases in concepts.items():
                for phrase in phrases:
                    pattern = r'(?<!\w)' + re.escape(phrase.lower()) + r'(?!\w)'
                    if re.search(pattern, text) and label not in seen_labels:
                        signals.append(ExtractedSignal(
                            label=label,
                            category=category
                        ))
                        seen_labels.add(label)
                        break
        
        return signals


_extractor_instance: Optional[MLSignalExtractor] = None


def get_extractor() -> MLSignalExtractor:
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = MLSignalExtractor()
    return _extractor_instance


def extract_signals(text: str) -> Dict[str, Any]:

    extractor = get_extractor()
    result = extractor.extract(text)
    return result.to_dict()



if __name__ == "__main__":
    test_inputs = [
        "I feel so anxious today",
        "Finals are killing me",
        "I can't sleep and feel restless",
        "I feel empty and avoid everyone",
        "Heart racing, can't breathe",
        "I'm not depressed, just tired",
        "I've been stressed for weeks"
    ]
    
    print("ML Signal Extraction Test")
    print("=" * 60)
    
    for text in test_inputs:
        result = extract_signals(text)
        print(f"\nInput: {text}")
        print(f"Emotions: {result['emotions']}")
        print(f"Symptoms: {result['symptoms']}")
        print(f"Triggers: {result['triggers']}")
        print(f"Intensity: {result['intensity']}, Temporal: {result['temporal']}")
