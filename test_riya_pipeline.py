from nlp.extractor import extract_concepts
from nlp.concept_mapper import map_to_ontology
from nlp.confidence_estimator import build_evidence

# Sample input (simulates upstream system)
text = "I feel very anxious and stressed because of academic pressure and exams."

# Step 1: Extract
extracted = extract_concepts(text)
print("\nEXTRACTED:")
for e in extracted:
    print(e)

# Step 2: Map to ontology
mapped = map_to_ontology(extracted)
print("\nMAPPED:")
for m in mapped:
    print(m)

# Step 3: Build evidence
evidence = build_evidence(mapped, session_id="test_session", turn_index=1)
print("\nEVIDENCE OBJECTS:")
for ev in evidence:
    print(ev)
