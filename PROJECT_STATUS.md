# Mental Health KG Chatbot - Project Status Report

**Project**: Mental Health Ontology & Knowledge Graph for Reasoning-Based Emotional Wellness Support  
**Last Updated**: December 6, 2025  
**Status**: Phase 1 Complete (UI/API Skeleton) → Ready for Phase 2 (Core Logic Implementation)

---

## 📊 Executive Summary

This project is building an explainable, reasoning-based mental health wellness assistant for university students. The system uses Knowledge Graphs (KG), OWL ontologies, SPARQL reasoning, and NLP to detect emotional patterns and provide transparent, causal explanations for inferred mental states.

**Current Progress**: ~30% Complete
- ✅ Frontend UI fully implemented
- ✅ Backend API skeleton ready
- ❌ Core reasoning & ontology logic not yet implemented
- ❌ NLP extraction pipeline not yet built
- ❌ SPARQL rules & knowledge graph pending

---

## ✅ What Has Been Completed

### 1. **Frontend Application (100% Complete)** 🎨

A complete React + TypeScript + TailwindCSS + Framer Motion UI has been built according to the specifications in `frontend.md`.

#### **Pages Implemented** (6 total)
- ✅ **Home** - Welcome/landing page
- ✅ **Chat** - Main conversational interface (continuous chat)
- ✅ **Session** - Session detail with explanation traces
- ✅ **Dashboard** - Analytics and trend visualizations
- ✅ **Settings** - User preferences and theme controls
- ✅ **About** - Project information and citations

#### **Components Implemented** (11 total)

**Chat Components:**
- ✅ `ChatShell.tsx` - Main conversation wrapper
- ✅ `MessageItem.tsx` - User/bot message bubbles
- ✅ `Composer.tsx` - Message input with multi-line support
- ✅ `QuickPrompts.tsx` - Pre-built message suggestions

**Explanation Components:**
- ✅ `ExplanationPanel.tsx` - Shows reasoning steps and inferred states
- ✅ `EvidenceList.tsx` - Displays clickable evidence linking to messages

**Intervention Components:**
- ✅ `InterventionCard.tsx` - Displays recommended wellness interventions
- ✅ `ExerciseModal.tsx` - Guided breathing/journaling exercises with timers

**Layout Components:**
- ✅ `TopNav.tsx` - Global navigation header
- ✅ `LeftNav.tsx` - Vertical menu sidebar
- ✅ `FooterBar.tsx` - Mobile quick actions

#### **Frontend Features**
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Calm, accessible UI design (soft colors, rounded shapes, high contrast)
- ✅ Framer Motion animations for smooth interactions
- ✅ React Router for multi-page navigation
- ✅ TypeScript type safety
- ✅ TailwindCSS styling with custom theme
- ✅ Lucide icons integration

#### **Frontend Tech Stack**
```json
{
  "framework": "React 18 + TypeScript",
  "styling": "TailwindCSS",
  "animations": "Framer Motion",
  "routing": "React Router",
  "icons": "Lucide React",
  "build": "Vite"
}
```

---

### 2. **Backend API Skeleton (100% Complete)** ⚙️

A minimal FastAPI backend has been implemented with **placeholder responses** only (no actual logic).

#### **API Endpoints Implemented**
- ✅ `POST /api/message` - Accepts user messages, returns dummy bot responses
- ✅ `GET /api/session/{id}` - Returns placeholder session data
- ✅ `POST /api/reset` - Resets session (dummy implementation)
- ✅ `GET /` - Health check endpoint

#### **Backend Features**
- ✅ CORS middleware configured for local development
- ✅ Pydantic models for request/response validation
- ✅ All endpoints return structured JSON matching frontend contracts
- ✅ TypeScript-compatible type definitions

#### **Backend Tech Stack**
```python
{
  "framework": "FastAPI",
  "validation": "Pydantic",
  "server": "Uvicorn",
  "cors": "CORS Middleware"
}
```

#### **What the Backend DOES NOT Do (By Design)**
- ❌ **No NLP extraction** (placeholders only)
- ❌ **No ontology mapping** (placeholders only)
- ❌ **No SPARQL reasoning** (rules not implemented)
- ❌ **No database** (all in-memory)
- ❌ **No actual mental state inference** (hardcoded dummy responses)

> **Note**: This was intentional per `rules.md` - the UI/API skeleton was built first, and the core logic will be implemented separately.

---

### 3. **Project Documentation (100% Complete)** 📄

- ✅ `context.md` - Complete project vision, goals, ontology design, and workflow
- ✅ `frontend.md` - Detailed UI/UX specifications (~680 lines)
- ✅ `rules.md` - "What NOT to do" guidelines for AI code generation
- ✅ `README.md` - Setup instructions, tech stack, and getting started guide

---

### 4. **Development Environment (100% Complete)** 🛠️

- ✅ Frontend scaffolded with Vite + React + TypeScript
- ✅ TailwindCSS configured with custom theme
- ✅ Backend dependencies defined (`requirements.txt`)
- ✅ Project runs locally (frontend on port 3000, backend on port 8000)
- ✅ CORS properly configured for local development

---

## ❌ What Remains To Be Done

### **Phase 2: Core Intelligence (0% Complete)** 🧠

This is the **main KRR (Knowledge Representation & Reasoning) work** and is entirely pending.

#### **1. Ontology Development**

**Status**: Not Started  
**Priority**: Critical  
**Estimated Effort**: 2-3 weeks

**Tasks:**
- [ ] Design and build `mental_health.owl` ontology using Protégé
- [ ] Define core classes:
  - `Emotion` (Stress, Anxiety, Sadness, Fear, Irritability, Hopelessness)
  - `Symptom` (Insomnia, Fatigue, SocialWithdrawal, RapidHeartRate, etc.)
  - `Trigger` (ExamPressure, AcademicWorkload, SocialExposure, etc.)
  - `MentalState` (AcademicStress, PanicRisk, EarlyDepression, Burnout, etc.)
  - `Intervention` (BreathingExercise, TimeManagement, Journaling, etc.)
  - `RiskLevel` (Low, Moderate, High, Escalation)
  - `BehaviorPattern` (EmotionalWithdrawal, PanicResponse, etc.)
- [ ] Define object properties:
  - `hasSymptom`, `experiencesEmotion`, `facingTrigger`
  - `associatedWith`, `canLeadTo`, `recommendedIntervention`
- [ ] Define data properties (confidence scores, severity, duration, etc.)
- [ ] Add subclass hierarchies and relationships
- [ ] Validate ontology consistency using Protégé reasoner
- [ ] Export to both OWL and Turtle (TTL) formats

**Deliverables:**
- `mental_health.owl` (OWL format)
- `mental_health.ttl` (Turtle/RDF format)

---

#### **2. Knowledge Graph Construction**

**Status**: Not Started  
**Priority**: Critical  
**Estimated Effort**: 1-2 weeks

**Tasks:**
- [ ] Create base knowledge graph with initial triples
- [ ] Define relationships between:
  - Emotions → Symptoms
  - Triggers → Emotions
  - Symptom patterns → Mental States
  - Mental States → Interventions
- [ ] Implement session-specific subgraphs (temporary KGs per user)
- [ ] Set up RDFLib in Python for triple manipulation
- [ ] Create utility functions for:
  - Adding new triples to session graph
  - Querying the graph
  - Exporting session graphs to TTL

**Example Triples to Implement:**
```turtle
:User :hasSymptom :Insomnia .
:User :experiencesEmotion :Stress .
:User :facingTrigger :ExamPressure .
:Insomnia :associatedWith :Anxiety .
:AcademicStress :canLeadTo :Anxiety .
:Anxiety :recommendedIntervention :BreathingExercise .
```

**Deliverables:**
- `base_graph.ttl` (core knowledge graph)
- `graph_manager.py` (Python module for KG operations)

---

#### **3. SPARQL Reasoning Rules**

**Status**: Not Started  
**Priority**: Critical  
**Estimated Effort**: 2 weeks

**Tasks:**
- [ ] Implement reasoning rules using SPARQL INSERT queries
- [ ] Core rules to implement:
  - **Rule R1**: `Stress + Insomnia + ExamPressure → AnxietyRisk`
  - **Rule R2**: `Fatigue + SocialWithdrawal → DepressivePattern`
  - **Rule R3**: `RapidHeartbeat + BreathDifficulty + Panic → PanicRisk`
  - **Rule R4**: `Overwork + Stress + Exhaustion → BurnoutRisk`
  - **Rule R5**: `SocialExposure + Fear + Avoidance → SocialAnxiety`
- [ ] Implement rule confidence scoring
- [ ] Create rule explanation generator (causal chains)
- [ ] Test rules on sample dialogues

**Deliverables:**
- `rules.sparql` (SPARQL rule definitions)
- `reasoner.py` (Python reasoning engine)

---

#### **4. NLP Extraction Pipeline**

**Status**: Not Started  
**Priority**: High  
**Estimated Effort**: 2-3 weeks

**Tasks:**
- [ ] Build emotion detection module
  - Use keyword dictionaries + semantic similarity
  - sentence-transformers for context-aware matching
- [ ] Build symptom extraction module
  - Pattern matching for physical symptoms (e.g., "can't sleep" → Insomnia)
- [ ] Build trigger detection module
  - Recognize academic, social, family, health-related triggers
- [ ] Implement semantic similarity matching to ontology concepts
  - Use pre-trained models (e.g., sentence-transformers)
- [ ] Create confidence scoring for extracted concepts
- [ ] Map extracted concepts to ontology URIs

**Technologies:**
- NLTK (tokenization, stopword removal)
- scikit-learn (TF-IDF, simple classifiers)
- sentence-transformers (semantic similarity)

**Deliverables:**
- `nlp_extractor.py` (NLP module)
- Keyword dictionaries for emotions, symptoms, triggers
- Pre-trained similarity model or embeddings

---

#### **5. Backend Integration**

**Status**: Not Started (Skeleton exists)  
**Priority**: High  
**Estimated Effort**: 1-2 weeks

**Tasks:**
- [ ] Replace placeholder `/api/message` logic with:
  - NLP extraction
  - Ontology mapping
  - Triple insertion into session graph
  - SPARQL reasoning
  - Explanation generation
  - Response synthesis
- [ ] Implement session state management
  - Store session graphs in memory (or lightweight DB)
  - Track conversation history
  - Accumulate evidence across messages
- [ ] Implement `/api/session` to return real session data
- [ ] Implement TTL export endpoint (`/api/session/:id/export.ttl`)
- [ ] Add error handling and validation

**Deliverables:**
- Updated `backend/main.py` with full reasoning pipeline
- Session manager module

---

#### **6. Causal Explanation Generator**

**Status**: Not Started  
**Priority**: High  
**Estimated Effort**: 1 week

**Tasks:**
- [ ] Build explanation step generator
  - "Detected [concept] in message [id]"
  - "Rule [R#] matched: [condition] → [inference]"
  - "Evidence: [list of supporting messages/triples]"
- [ ] Implement confidence aggregation
- [ ] Create human-readable explanation text
- [ ] Link explanations to specific triples in KG

**Deliverables:**
- `explainer.py` (explanation module)

---

### **Phase 3: Testing & Validation (0% Complete)** 🧪

**Status**: Not Started  
**Priority**: Medium  
**Estimated Effort**: 1 week

**Tasks:**
- [ ] Create 10 realistic test dialogues with expected inferences
- [ ] Test NLP extraction accuracy
- [ ] Validate reasoning rules produce correct inferences
- [ ] Test explanation quality (human-readable, causally accurate)
- [ ] Test intervention recommendations are relevant
- [ ] Verify TTL export works correctly
- [ ] Test edge cases (ambiguous input, contradictory symptoms, etc.)

**Deliverables:**
- Test suite with sample conversations
- Validation report

---

### **Phase 4: Final Documentation (0% Complete)** 📚

**Status**: Not Started  
**Priority**: Medium  
**Estimated Effort**: 3-4 days

**Tasks:**
- [ ] Write final project report with:
  - System architecture diagram
  - Ontology explanation (classes, properties, design rationale)
  - Reasoning demonstration (step-by-step example)
  - NLP pipeline explanation
  - Screenshots of UI flows
  - 10 case study dialogues with explanations
- [ ] Create presentation slides
- [ ] Record demo video (optional)
- [ ] Document limitations and future work

**Deliverables:**
- Final report (PDF)
- Presentation slides
- Demo video

---

## 🎯 Immediate Next Steps

### **Priority 1: Ontology Design** (Start Here)

1. Install Protégé (ontology editor)
2. Create `mental_health.owl` with core classes and properties
3. Validate using built-in reasoner
4. Export to TTL format

### **Priority 2: Build Initial Knowledge Graph**

1. Install RDFLib in Python (`pip install rdflib`)
2. Create base triples for common patterns
3. Test loading and querying the graph

### **Priority 3: Implement First Reasoning Rule**

1. Pick one simple rule (e.g., R1: Stress + Insomnia → AnxietyRisk)
2. Write SPARQL INSERT query
3. Test on a sample message
4. Verify inference is correct

### **Priority 4: Build Basic NLP Extractor**

1. Start with keyword-based emotion detection
2. Test on sample sentences
3. Integrate with backend `/api/message`
4. Verify extraction → ontology mapping works

---

## 📁 Project Deliverables Checklist

### **Completed** ✅
- [x] Frontend UI (all 6 pages, 11 components)
- [x] Backend API skeleton (3 endpoints)
- [x] Project documentation (`context.md`, `frontend.md`, `rules.md`, `README.md`)
- [x] Development environment setup

### **In Progress** 🔄
- [ ] None currently

### **Not Started** ❌
- [ ] Mental health ontology (`mental_health.owl`)
- [ ] Base knowledge graph (`base_graph.ttl`)
- [ ] Session knowledge graphs
- [ ] SPARQL reasoning rules (`rules.sparql`)
- [ ] NLP extraction pipeline (`nlp_extractor.py`)
- [ ] Reasoning engine (`reasoner.py`)
- [ ] Explanation generator (`explainer.py`)
- [ ] Backend integration (replace placeholders)
- [ ] Test case suite (10 dialogues)
- [ ] Final project report

---

## 🚧 Known Limitations

1. **No persistent storage** - All data is in-memory (as designed)
2. **Placeholder responses** - Backend returns dummy data (to be replaced)
3. **No authentication** - Not required for this project
4. **No deployment** - Runs locally only (as designed)
5. **No deep learning** - Uses rule-based reasoning + lightweight NLP (as designed)

---

## 🔄 Project Timeline Estimate

| Phase | Status | Estimated Time |
|-------|--------|---------------|
| Phase 1: UI/API Skeleton | ✅ **Complete** | 2 weeks (done) |
| Phase 2: Core Logic | ❌ Not Started | 6-8 weeks |
| Phase 3: Testing | ❌ Not Started | 1 week |
| Phase 4: Documentation | ❌ Not Started | 3-4 days |
| **Total Remaining** | | **~7-9 weeks** |

---

## 📚 Key References

- **Ontology Design**: See `context.md` Section 8
- **Knowledge Graph Triples**: See `context.md` Section 9
- **Reasoning Rules**: See `context.md` Section 10
- **UI Components**: See `frontend.md` Section 5
- **API Contracts**: See `frontend.md` Section 7
- **What NOT to Do**: See `rules.md` and `frontend.md` Section 17

---

## 🎓 Learning Outcomes (KRR Course Alignment)

This project directly demonstrates:

- ✅ **Ontology Design** (OWL, classes, properties, hierarchies)
- ✅ **Knowledge Representation** (RDF triples, graph structure)
- ✅ **Reasoning** (SPARQL rules, inference)
- ✅ **Explainable AI** (causal explanation generation)
- ✅ **Semantic NLP** (concept extraction, ontology mapping)
- ✅ **Practical Application** (mental health wellness support)

---

## 📞 Contact & Resources

- **Project Repository**: Local only (no deployment)
- **Ontology Tools**: Protégé (https://protege.stanford.edu/)
- **RDF Library**: RDFLib (https://rdflib.readthedocs.io/)
- **NLP Tools**: NLTK, sentence-transformers

---

**Last Updated**: December 6, 2025  
**Next Review Date**: After ontology completion

---
