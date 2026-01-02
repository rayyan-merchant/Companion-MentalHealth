
# ❌ **WHAT NOT TO DO (For the AI Generating the Frontend + API Boilerplate)**

When generating the frontend and backend API scaffolding, you must strictly **avoid** doing any of the following:

---

## ❌ 1. **Do NOT build any ontology logic**

* Do **NOT** write OWL files
* Do **NOT** generate RDF triples
* Do **NOT** embed SPARQL queries
* Do **NOT** implement reasoning rules
* Do **NOT** load or parse ontologies

> These parts will be done **manually by our team**, not by the AI.

---

## ❌ 2. **Do NOT generate any NLP or ML logic**

* No symptom extraction
* No emotion detection
* No semantic similarity
* No transformers
* No classifiers
* No keyword matching pipeline

> The AI should only create the frontend UI and the backend endpoints, not the internal intelligence.

---

## ❌ 3. **Do NOT implement chatbot reasoning logic**

* Do not attempt to infer mental states
* Do not hardcode stress → anxiety rules
* Do not create heuristics or logic trees
* Do not write causal reasoners or explanations

> Only create placeholder handlers like:

```js
POST /api/message
→ receives { text: "...user message..." }
→ returns a dummy JSON response
```

We will replace dummy responses with real reasoning later.

---

## ❌ 4. Do NOT build database code

* No MongoDB
* No SQL
* No local storage logic
* No session persistence

> Use only **in-memory mocks** if needed.
> All actual logic will be added later by us.

---

## ❌ 5. Do NOT set up deployment, Docker, CI/CD, or authentication

We are **NOT** deploying the system, so:

* No Dockerfile
* No Kubernetes
* No Firebase/Auth0
* No JWT tokens

Keep the backend simple, local, and minimal.

---

## ❌ 6. Do NOT alter the UI theme or structure we provided

* Do not ignore our color palette
* Do not redesign screens
* Do not change the layout structure
* Do not add new pages

> Only build exactly what is listed in the frontend plan.

---

## ❌ 7. Do NOT create advanced UI functionality

Avoid:

* Recommender systems
* Graph visualizations of KG
* Ontology editors
* Admin dashboards
* Real-time analytics

> These features are out of scope for now.

---

## ❌ 8. Do NOT mix frontend and backend frameworks

The AI must follow:

### ✔ **Frontend:** React + TailwindCSS + Framer Motion

### ✔ **Backend:** FAST API

Anything else (Angular, Vue, Flask, Next.js, Django, etc.) is not allowed unless we explicitly ask.

---

## ❌ 9. Do NOT generate unnecessary comments, explanations, or tutorials

When generating actual code later:

* Keep code clean
* No long explanations
* No teaching
* No redundant documentation

We only want clean, production-quality code.

---

## ❌ 10. Do NOT assume or hallucinate system logic

If the backend response requires something like:

```
{
  "emotion": ...,
  "symptoms": ...,
  "inferred_state": ...,
  "explanation": ...
}
```

The AI must NOT automatically generate the logic behind it.

Just create placeholders like:

```
{
  "emotion": "placeholder_emotion",
  "symptoms": ["placeholder"],
  "inferred_state": "placeholder_state",
  "explanation": "placeholder_reason"
}
```

We will replace these placeholders with actual ontology/NLP logic later.

---

# ✔ What The AI **IS ALLOWED** To Do

For clarity, the AI **MAY** generate:

### ✔ Full frontend UI (React + Tailwind + Framer Motion)

### ✔ Components, layouts, themes, animations

### ✔ API call functions (fetch/axios)

### ✔ Backend boilerplate (Express.js)

### ✔ API endpoint structure

### ✔ Dummy placeholder responses

### ✔ Instructions for running the frontend/backend locally

Everything else is off-limits.

---

# ⭐ Final Summary 

**When generating code, focus ONLY on:**

* UI
* UX
* Layout
* Components
* Theming
* Animations
* Basic Express.js endpoints with mock JSON

**Do NOT build reasoning, NLP, ontology, ML, or backend logic.**

---


