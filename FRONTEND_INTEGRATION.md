# Frontend Integration: KRR System

## Overview
The frontend is a presentation layer for the Symbolic Knowledge Reasoning backend. It is responsible for:
1.  Capturing user input
2.  Maintaing session context (`session_id`)
3.  Displaying **immutable symbolic results** from the backend.

It explicitly **DOES NOT**:
- Perform client-side reasoning.
- Calculate scores.
- Store sensitive medical data locally (other than transient session state).

---

## Component Architecture

### `useSession` Hook (`hooks/useSession.ts`)
- **Role**: State container and API bridge.
- **Logic**: 
    - Generates/Persists `session_id`.
    - Calls `runKrrPipeline(text)`.
    - Updates local `krrResult` state.
    - Appends Bot messages derived from KRR Summary.

### `ExplanationPanel` (`components/explanation/ExplanationPanel.tsx`)
- **Role**: KRR Result Visualizer.
- **Data Source**: `krrResult` prop (Raw symbolic payload).
- **Sections**:
    - **Ranked Concerns**: Ordered list of inferred Ontology Classes (e.g. `AnxietyRisk`).
    - **Reasoning Trace**: Step-by-step logic returned by Explainer.
    - **Audit Ref**: Hash for verification.

### `Chat` Page (`pages/Chat.tsx`)
- **Role**: Layout Orchestrator.
- **Logic**: Connects `useSession` to `ChatShell` and `ExplanationPanel`.

---

## Integration Flow

1.  **User Input**: Typed in `Composer`.
2.  **API Call**: `POST /api/krr/run` triggered by `useSession`.
3.  **Processing**: UI shows loading state.
4.  **Update**: 
    - `krrResult` updated -> `ExplanationPanel` re-renders with new reasoning.
    - `messages` updated -> Chat history shows summary + guidance.
