ONTOLOGY_MAP = {
    # Emotions
    "Stress": ("mh:Stress", "Emotion"),
    "Anxiety": ("mh:Anxiety", "Emotion"),
    "Sadness": ("mh:Sadness", "Emotion"),
    "Fear": ("mh:Fear", "Emotion"),
    "Panic": ("mh:Panic", "Emotion"),
    "Irritability": ("mh:Irritability", "Emotion"),
    "Emotional_Overwhelm": ("mh:EmotionalOverwhelm", "Emotion"), # Changed to CamelCase to match convention, need to check orchestrator

    # Symptoms
    "Insomnia": ("mh:Insomnia", "Symptom"),
    "Fatigue": ("mh:Fatigue", "Symptom"),
    "RapidHeartRate": ("mh:RapidHeartRate", "Symptom"), # Fixed
    "BreathingDifficulty": ("mh:BreathingDifficulty", "Symptom"), # Fixed
    "Headache": ("mh:Headache", "Symptom"),
    "DifficultyConcentrating": ("mh:DifficultyConcentrating", "Symptom"), # Fixed
    "SocialWithdrawal": ("mh:SocialWithdrawal", "Symptom"), # Fixed
    "AppetiteChange": ("mh:AppetiteChange", "Symptom"), # Fixed
    "Restlessness": ("mh:Restlessness", "Symptom"),
    "LossOfInterest": ("mh:LossOfInterest", "Symptom"), # Fixed

    # Triggers
    "ExamPressure": ("mh:ExamPressure", "Trigger"), # Fixed
    "AcademicWorkload": ("mh:AcademicWorkload", "Trigger"), # Fixed
    "AssignmentDeadline": ("mh:AssignmentDeadline", "Trigger"), # Fixed
    "PoorGrades": ("mh:PoorGrades", "Trigger"), # Fixed
    "FinancialConcern": ("mh:FinancialConcern", "Trigger"), # Fixed
    "FamilyPressure": ("mh:FamilyPressure", "Trigger"), # Fixed
    "SocialPressure": ("mh:SocialPressure", "Trigger"), # Added
    "Depression": ("mh:DepressiveSpectrum", "Mental_State") # Explicit Mapping
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
        else:
             pass

    return mapped
