# Companion: Technical Implementation Report

> Historical report: several architecture claims below describe the intended
> design rather than the current production path. See `README.md` for current
> behavior and `PROJECT_AUDIT.md` for the verified gap analysis.

## 1. Executive Summary

**Companion** is an ontology-driven **Knowledge Representation & Reasoning (KRR)** chatbot designed to promote explainable mental health risk awareness for university students. Unlike standard "black box" AI chatbots, Companion uses a hybrid neuro-symbolic approach: it combines **symbolic AI** (OWL Ontology, SWRL rules, SPARQL) for deterministic reasoning with **LLMs** (Large Language Models) for natural language generation and empathy.

**Purpose:** To provide students with a safe, transparent, and non-clinical space to express their feelings, returning not just support, but *explanations* of why certain risks (like Anxiety or Academic Stress) were identified, alongside actionable coping strategies.

---

## 2. System Architecture

The application follows a modern full-stack architecture with a specialized "AI Agents" layer.

### 2.1 High-Level Flow
1.  **User Input**: Student sends a message via the React Frontend.
2.  **API Layer**: FastAPI backend receives the request.
3.  **Hybrid Pipeline**:
    *   **Extraction**: NLP algorithms extract structured signals (Emotions, Symptoms, Triggers).
    *   **Crisis Interceptor**: Checks for immediate harm risks using regex loops (Tier 1 & 2 detection).
    *   **Symbolic Reasoning**: Maps signals to the **Mental Health Ontology**. Rules (SPARQL) fire to infer a "State" (e.g., `AnxietyRisk`).
    *   **Confidence Gating**: Evaluates if there is enough evidence to support the inference.
    *   **Explanation Engine**: An LLM (Groq/Gemini) generates a warm, empathetic response explaining the inference and suggesting coping strategies from a verified knowledge base (RAG).
4.  **Response**: The system returns the text response, the identified state, confidence level, and a "Reasoning Trace" to the user.

### 2.2 Tech Stack
*   **Frontend**: React (Vite), Tailwind CSS, Framer Motion (for animations).
*   **Backend**: Python FastAPI.
*   **AI/Logic**:
    *   **Symbolic**: `rdflib` (RDF/OWL/SPARQL).
    *   **NLP**: `spacy` / `nltk` (Keyword extraction).
    *   **LLM**: `groq`, `google-genai` (Response phrasing).
    *   **Reasoning**: Custom Rule Engine (Python + SPARQL).

---

## 3. Implementation Details

### 3.1 Backend & API (`backend/`)
*   **Entry Point** (`main.py`): Sets up the FastAPI app, CORS, and mounts the frontend static files.
*   **Session Management** (`session_routes.py`): Handles creating chat sessions, storing history, and invoking the AI pipeline.
*   **Store**: Manages session state and history (likely in-memory or file-based for this iteration).

### 3.2 The Hybrid AI Pipeline (`agents/`)
This is the core differentiator of the system.

#### A. NLP Extractor (`ml_extractor.py`)
*   Scans user text for specific keywords mapped to ontology concepts.
*   **Categorization**:
    *   **Emotions**: "anxious", "sad", "overwhelmed".
    *   **Symptoms**: "insomnia", "heart racing", "fatigue".
    *   **Triggers**: "exams", "money", "loneliness".

#### B. Crisis Detection (`pipeline.py`)
*   A **Three-Tier** safety system runs *before* any reasoning:
    1.  **Exact Phrase Match**: "I want to die" (High Severity).
    2.  **Contextual Regex**: "can't take this anymore".
    3.  **Idiom Filter**: Distinguishes "Exams are killing me" (Stress) from actual harm risks.
*   If a crisis is detected, the pipeline aborts normal logic and returns immediate resources/hotlines.

#### C. Symbolic Reasoner (`symbolic_reasoner.py`)
*   **Ontology**: Uses an OWL file (`mental_health.owl`) to define relationships between symptoms and conditions.
*   **Inference**:
    *   Constructs a temporary RDF graph for the session.
    *   Applies **SPARQL Rules** (e.g., `rule_R_ANX_physio.sparql`):
        > *IF hasEmotion(Anxiety) AND hasSymptom(Insomnia) -> Infer(AnxietyRisk)*
*   **Determinism**: This step is 100% predictable. If the rules match, the state is inferred. No hallucination is possible here.

#### D. Explainable AI Agent (`llm_explainer.py`)
*   Takes the **structured output** from the reasoner (State: AnxietyRisk, Evidence: Insomnia).
*   Retrieves "RAG Snippets" (strategies for Anxiety).
*   **LLM Role**: It acts as a "Translator". It does *not* diagnose; it only rephrases the deterministic logic into human-friendly language.
    *   *Input to LLM*: "State: Anxiety. Evidence: Insomnia. Strategy: 4-7-8 Breathing."
    *   *Output from LLM*: "I hear that you're having trouble sleeping. In our model, this often links to anxiety. Have you tried 4-7-8 breathing?"

### 3.3 Frontend (`frontend/`)
*   **Chat Interface**: Displays the conversation. Crucially, it shows the **metadata** returned by the backend (Risk Level, Inferred State) in a collapsible "Insight" panel, making the AI's "thought process" visible.
*   **Dashboard**: Offers a longitudinal view of the user's mental health journey, showing trends and AI-generated insights (`/api/sessions/insight`).
*   **Privacy**: Data is session-based.

---

## 4. Key Features & Innovations

1.  **"Glass Box" AI**: Users can see *exactly* why the AI suggested something. "I identified 'Stress' because you mentioned 'Exams' and 'Headaches'."
2.  **Safety First**: The multi-tier crisis detection system prioritizes user safety above all else.
3.  **Neuro-Symbolic**: Combines the reliability of code/rules with the fluency of modern LLMs.

### 4.1 Performance Optimizations
To ensure the application runs efficiently on limited resources (e.g., standard laptops or free-tier cloud instances), we implemented several key optimizations:

*   **Qdrant for Vector Storage**: We use **Qdrant** as our vector database. It is highly optimized for performance and allows us to store and retrieve embeddings efficiently, significantly reducing the memory footprint compared to loading all vectors into RAM.
*   **Embedding Caching**: To speed up response times and reduce API costs/latency, we implemented a **caching layer** for embeddings. If a user enters a similar message to one processed previously, the system retrieves the cached embedding instead of re-computing it or making a redundant API call.
*   **Lazy Loading**: Heavy ML models and libraries are loaded only when needed (or asynchronously) to keep the initial startup time fast and RAM usage low during idle periods.

### 4.2 Context Awareness & Long-Term Memory
Unlike simple chatbots that treat every message in isolation, Companion implements a **Session Memory** system:
*   **Conversational History**: The app retails the full context of the current session, allowing users to refer back to previous topics ("As I mentioned earlier...").
*   **Context Fusion**: When new logical inferences are weak (e.g., "NeedsMoreContext"), the system automatically retrieves and "fuses" accumulated signals from the entire session to find patterns that overlap over time (e.g., persistent sleep issues + new anxiety signals).
*   **Dashboard Insights**: The system analyzes long-term history to generate longitudinal insights on the dashboard, helping users track their mental health journey over days or weeks.

### 4.3 Safety & Ethical Guardrails
Safety is the foundational priority of Companion. We enforce strict guardrails to prevent harm:
*   **Non-Clinical Nature**: The system acts strictly as a peer support tool, not a doctor. It provides *educational* explanations of feelings, never medical diagnoses.
*   **Deterministic Crisis Intercept**: Before any AI processing, a **Rule-Based Crisis Interceptor** (Tier 1) scans for self-harm or violence patterns using regex. If detected, the AI is bypassed entirely, and immediate helpline resources are shown. This ensures that a "hallucinating" LLM can never downplay a crisis.
*   **Privacy by Design**: No personal identifiable information (PII) is required. Conversation data is session-scoped and not used to train global models.

## 5. Directory Structure Overview
```
/
├── agents/            # AI Logic (Pipeline, Reasoner, Explainer)
├── backend/           # FastAPI Server & Routes
├── frontend/          # React UI
├── ontology/          # .owl files and knowledge graph definitions
├── reasoning/         # SPARQL rules
└── data/              # Data storage
```

## 6. Deployment & DevOps

The application is containerized using **Docker** for consistent deployment across environments.

### 6.1 Docker Strategy
*   **Multi-Stage Build**: The `Dockerfile` uses a multi-stage approach to keep the final image size small.
    1.  **Build Stage**: Uses a Node.js image to compile the React frontend (`npm run build`).
    2.  **Runtime Stage**: Uses a lightweight Python Slim image. It installs Python dependencies, copies the built frontend assets from Stage 1, and serves the application.
*   **Unified Server**: The FastAPI backend serves both the API JSON responses *and* the static frontend files (SPA), simplifying deployment to a single container/service (e.g., Render, Railway, AWS App Runner).

### 6.2 CI/CD & Local Development
*   **Local**: Developers can run `docker-compose up` (if configured) or run backend/frontend servers independently for hot-reloading.
*   **Environment Variables**: Managed via `.env` files (e.g., `GROQ_API_KEY`, `JWT_SECRET`) to ensure security and flexibility.

## 7. Conclusion
Companion represents a safer, more transparent approach to mental health AI. By grounding its advice in strict logical rules and only using LLMs for phrasing, it avoids the common pitfalls of "hallucinated diagnoses" while maintaining a supportive, human-like interaction style.
