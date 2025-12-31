# Person-2 NLP Module (Riya)

## Scope
This module is responsible ONLY for:
- Extracting ontology-aligned concepts from raw text
- Mapping them to krr.owl URIs
- Producing Evidence Objects

## Pipeline
text → extractor → concept_mapper → confidence_estimator → Evidence Objects

## Important Notes
- No machine learning
- No diagnosis or prediction
- No dataset parsing
- Ontology is the source of truth

## Output
Structured Evidence Objects compliant with evidence_schema.pdf
