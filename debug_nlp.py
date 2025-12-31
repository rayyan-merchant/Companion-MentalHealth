from nlp.extractor import extract_concepts
from nlp.concept_mapper import map_to_ontology

text = "I am so stressed about my exams next week. I haven't slept in days causing insomnia."
print("Input:", text)

extracted = extract_concepts(text)
print("\nExtracted:", extracted)

mapped = map_to_ontology(extracted)
print("\nMapped:", mapped)
