# Session Flow Strategy

## Goal
Ensure multi-turn context preservation and deterministic reasoning across a user session.

## Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend (React)
    participant Backend (FastAPI)
    participant GraphManager
    participant Reasoner (SPARQL)

    Note over Frontend: Session ID generated on mount (sess-123)

    User->>Frontend: "I have exams next week."
    Frontend->>Backend: POST /run {session_id: "sess-123", text: "..."}
    
    Backend->>GraphManager: load_existing_session("sess-123.ttl")
    alt Session Exists
        GraphManager->>GraphManager: Load Triples
    else New Session
        GraphManager->>GraphManager: Create New Graph
    end

    Backend->>GraphManager: Add Evidence (ExamPressure)
    
    Backend->>Reasoner: Execute SPARQL Rules
    Reasoner->>GraphManager: Insert Inferred Triples (AcademicStress)
    
    Backend->>GraphManager: Export Session ("sess-123.ttl")
    
    Backend-->>Frontend: Return Symbolic Result
    Frontend->>User: Display Explanations & Advice
```

## Persistence Logic

1.  **Local Storage (Server)**: 
    - Sessions are stored as `.ttl` (Turtle) files in `data/session_graphs/`.
    - Filename: `{session_id}.ttl`.
    - This ensures that if the server restarts, or if a user reconnects with the same ID, the graph state is recovered.

2.  **Client State**:
    - Frontend holds `session_id` in React state.
    - If page refresh occurs, session is currently reset (simplification for MVP). 
    - *Future Upgrades*: Store `session_id` in `localStorage` to resume exact conversations.

## Constraints Preserved
- **No Numeric State**: State is purely RDF triples.
- **Auditability**: Every turn saves the full graph state.
