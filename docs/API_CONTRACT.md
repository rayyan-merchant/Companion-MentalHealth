# API Contract: Mental Health KRR System

## Overview
This document defines the strict interface between the Frontend UI and the Symbolic KRR Backend. 
The system operates on **symbolic-only** principles, rejecting numeric scores and heuristic inference.

---

## Endpoint: Execute Reasoning Pipeline

**URL**: `/api/krr/run`
**Method**: `POST`
**Content-Type**: `application/json`

### Request Body

```json
{
  "session_id": "string (UUID or deterministic ID)",
  "student_id": "string (URI or unique identifier)",
  "text": "string (User input text)"
}
```

- **session_id**: Required. Must persist across the user session to allow multi-turn reasoning.
- **text**: Raw input for NLP processing.

### Response Body (Success: 200 OK)

```json
{
  "session_id": "string",
  "summary": "string (High-level reasoning summary)",
  "explanations": [
    "string (Bullet 1 of reasoning trace)",
    "string (Bullet 2 ...)"
  ],
  "ranked_concerns": [
    "AcademicStress",
    "AnxietyRisk" 
  ],
  "escalation_guidance": "string (Advice on next steps)",
  "disclaimer": "This system does not provide medical diagnosis or treatment.",
  "audit_ref": "hash_string (Provenance reference)"
}
```

### Error Responses

**400 Bad Request**
```json
{
  "error": "Invalid input format"
}
```

**500 Internal Server Error**
```json
{
  "error": "Unable to process request at this time"
}
```

---

## Data Definitions

### Symbolic Constraints
1.  **NO Numeric Scores**: Confidence is implied by loop depth or explicit symbolic labels (HIGH/MEDIUM/LOW) attached to triples, but API returns only derived text/states.
2.  **Deterministic**: The same input sequence with the same `session_id` MUST produce the same `audit_ref`.
3.  **Safety**: "Unknown" or "Safe" states are valid outputs; the system never guesses.
