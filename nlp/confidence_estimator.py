from datetime import datetime

DEFAULT_CONFIDENCE = 0.75

def build_evidence(mapped_concepts, session_id="session_001", turn_index=0):
    evidence_objects = []

    for idx, concept in enumerate(mapped_concepts):
        evidence_objects.append({
            "evidence_id": f"ev_{turn_index}_{idx}",
            "concept_uri": concept["concept_uri"],
            "concept_type": concept["concept_type"],
            "confidence": DEFAULT_CONFIDENCE,
            "source_text": concept["surface_text"],   # ✅ ONLY ONCE
            "extraction_method": concept["extraction_method"],
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id
        })

    return evidence_objects
