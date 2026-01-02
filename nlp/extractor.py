import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PATTERN_DIR = BASE_DIR / "patterns"

def load_patterns(filename):
    with open(PATTERN_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)

EMOTION_PATTERNS = load_patterns("emotion_patterns.json")
SYMPTOM_PATTERNS = load_patterns("symptom_patterns.json")
TRIGGER_PATTERNS = load_patterns("trigger_patterns.json")

def extract_concepts(text: str):
    text = text.lower()
    results = []

    def match(patterns, category):
        for label, phrases in patterns.items():
            for phrase in phrases:
                phrase = phrase.lower()

                pattern = r'(?<!\w)' + re.escape(phrase) + r'(?!\w)'
                
                if re.search(pattern, text):
                    results.append({
                        "label": label,
                        "surface_text": phrase,
                        "category": category,
                        "extraction_method": "pattern_match"
                    })

    match(EMOTION_PATTERNS, "Emotion")
    match(SYMPTOM_PATTERNS, "Symptom")
    match(TRIGGER_PATTERNS, "Trigger")

    return results
