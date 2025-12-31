"""
Maps extracted labels to ontology URIs defined in krr.owl
"""

ONTOLOGY_MAP = {
    "Stress": ("mh:Stress", "Emotion"),
    "Anxiety": ("mh:Anxiety", "Emotion"),
    "Sadness": ("mh:Sadness", "Emotion"),
    "Insomnia": ("mh:Insomnia", "Symptom"),
    "Fatigue": ("mh:Fatigue", "Symptom"),
    "ExamPressure": ("mh:ExamPressure", "Trigger"),
    "AcademicWorkload": ("mh:AcademicWorkload", "Trigger")
}

def map_to_ontology(extracted_items):
    mapped = []

    for item in extracted_items:
        label = item["label"]
        if label in ONTOLOGY_MAP:
            uri, concept_type = ONTOLOGY_MAP[label]
            mapped.append({
                **item,
                "concept_uri": uri,
                "concept_type": concept_type
            })

    return mapped
