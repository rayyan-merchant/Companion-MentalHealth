from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import re
import json
from pathlib import Path


try:
    from sentence_transformers import SentenceTransformer, util
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not installed. Using pattern-based fallback.")


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

    def __init__(self, use_embeddings: bool = True):
        self.use_embeddings = use_embeddings and EMBEDDINGS_AVAILABLE
        self.model = None
        self.concept_embeddings = {}
        
        if self.use_embeddings:
            self._load_model()
            self._precompute_embeddings()
    
    def _load_model(self):
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Failed to load embedding model: {e}")
            self.use_embeddings = False
    
    def _precompute_embeddings(self):
        if not self.model:
            return
            
        all_concepts = {
            "emotion": EMOTION_CONCEPTS,
            "symptom": SYMPTOM_CONCEPTS,
            "trigger": TRIGGER_CONCEPTS
        }
        
        for category, concepts in all_concepts.items():
            for label, phrases in concepts.items():
                for phrase in phrases:
                    key = f"{category}:{label}:{phrase}"
                    self.concept_embeddings[key] = {
                        "embedding": self.model.encode(phrase, convert_to_tensor=True),
                        "category": category,
                        "label": label,
                        "phrase": phrase
                    }
    
    def extract(self, text: str) -> ExtractionResult:

        text_lower = text.lower()
        result = ExtractionResult()
        
        result.negated_terms = self._extract_negations(text_lower)
        
        result.intensity = self._detect_intensity(text_lower)
        
        result.temporal = self._detect_temporal(text_lower)
        
        signals = self._extract_with_patterns(text_lower)
        
        if self.use_embeddings and self.model:
            embedding_signals = self._extract_with_embeddings(text_lower)
            seen_labels = {s.label for s in signals}
            for sig in embedding_signals:
                if sig.label not in seen_labels:
                    signals.append(sig)
                    seen_labels.add(sig.label)
        
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
    
    def _extract_with_embeddings(self, text: str) -> List[ExtractedSignal]:
        signals = []
        text_embedding = self.model.encode(text, convert_to_tensor=True)
        
        seen_labels = set()
        
        for key, data in self.concept_embeddings.items():
            similarity = util.cos_sim(text_embedding, data["embedding"]).item()
            
            if similarity > 0.5 and data["label"] not in seen_labels:
                signals.append(ExtractedSignal(
                    label=data["label"],
                    category=data["category"]
                ))
                seen_labels.add(data["label"])
        
        return signals
    
    def _extract_with_patterns(self, text: str) -> List[ExtractedSignal]:
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
                    # Word boundary matching
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
