# Companion

**A non-clinical wellness reflection app for Pakistani university students** — built on an explicit ontology and symbolic reasoning pipeline instead of an opaque language model. Every response is traceable to specific extracted evidence and a specific fired rule.

**🔗 Live demo:** [companion-production.onrender.com](https://companion-production.onrender.com/)
*(Free-tier hosting — the app may take 30–50 seconds to wake up if it's been idle.)*

---

## Why Companion is different

Most AI wellness chatbots generate a reply and stop there, you never see *why* it said what it said. In a mental-health context, that's not just a UX gap; it's a trust problem.

Companion takes a different approach:

1. A free-text message is run through deterministic NLP extraction to identify emotions, symptoms, and triggers.
2. Extracted signals are mapped to concepts in a formal **OWL ontology** — not hardcoded if/else logic.
3. Evidence accumulates in a **session knowledge graph**, so the system reasons with context, not just one message at a time.
4. **Symbolic rules** fire over that evidence to infer a wellness pattern (e.g. `AnxietyRisk`, `PanicRisk`, `AcademicStress`).
5. A confidence gate decides whether to explain, explain cautiously, or ask a clarifying question.
6. A dedicated **safety layer** checks for crisis or medical red-flag language — and overrides *all* of the above the moment it detects one, no exceptions.
7. The response, the evidence, and the exact rule that fired are all shown back to the user and logged.

## Features

- 💬 **Conversational chat interface** with continuous session context
- 🔍 **Explainable analysis panel**: shows the inferred pattern, extracted signals, and the exact rule applied for every response
- 🛡️ **Crisis detection & safety interception**: suicidal ideation, self-harm, and medical emergencies bypass ordinary reasoning entirely, with false-positive filtering for idioms like "this assignment is killing me"
- 📊 **Rule-based reasoning engine** backed by a versioned, configurable rule catalog
- 🧠 **Optional LLM-assisted phrasing** for more natural responses, with deterministic template fallback when disabled
- 🗂️ **Session history & dashboard** with usage insights and safety-flag summaries

## How it's built

| Layer | Technologies |
|---|---|
| **Frontend** | React, TypeScript, TanStack Query, Tailwind CSS |
| **Backend** | Python, FastAPI, async SQLAlchemy, PostgreSQL, Redis |
| **Runtime reasoning** | Versioned YAML rule catalog + deterministic response templates |
| **Research / validation layer** | OWL ontology, RDFLib, SPARQL, Protégé — formal KRR artifacts kept outside the live request path |
| **Infrastructure** | Docker, deployed on Render (free tier), CI via GitHub Actions (lint, type-check, migrations, tests) |
| **Security** | Cookie-based auth, CSRF protection, rate limiting, hashed session tokens |

The repository contains two complementary layers: a **production path** (the deployed YAML rule engine — fast, deterministic, and safe to run under Render's memory limits) and a **research/validation path** (the full OWL/SWRL/SPARQL knowledge-representation stack, used to design and validate the same reasoning logic). The deployed app operationalizes the formal KRR design; it doesn't replace it.

## Project origin

Companion was built for the **Knowledge Representation & Reasoning** course at **FAST-NUCES**, under **Dr. Muhammad Rafi**, as a demonstration of a complete KRR pipeline: ontology design → knowledge graph representation → symbolic evidence extraction → rule-based inference → explanation generation → safety escalation → auditability.

## Team

| | |
|---|---|
| **Rayyan Merchant** | [GitHub](https://github.com/rayyan-merchant) · [LinkedIn](https://linkedin.com/in/rayyanmerchant2004) |
| **Syeda Rija Ali** | [GitHub](https://github.com/Srijaali/) · [LinkedIn](https://www.linkedin.com/in/syedarijaali/) |
| **Riya Bhart** | [GitHub](https://github.com/RiyaBhart) · [LinkedIn](https://www.linkedin.com/in/riya-bhart-339036287/) |

## ⚠️ Disclaimer

Companion is a **reflection tool**, not a diagnosis, therapy, or emergency service. It is a course project evaluated on transparency and reasoning quality, not clinical validation. It is not a substitute for professional mental health care.

**If you are experiencing a crisis, please contact local emergency services or a mental health professional immediately.**
