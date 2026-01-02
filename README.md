# Companion: Onotology Driven Mealth Health Chatbot


## Overview

This project is an **ontology-driven Knowledge Representation & Reasoning (KRR) system** that supports **explainable mental health risk inference** for university students.

The system:

* Extracts emotions, symptoms, and triggers from user text
* Maps them to a **Mental Health Ontology**
* Applies **SWRL-based symbolic reasoning**
* Materializes inferences via **SPARQL**
* Generates **human-readable causal explanations (“WHY” answers)**

⚠️ This system provides **non-clinical, educational support only** and does **not** perform diagnosis or therapy.


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/rayyan-merchant/Companion-MentalHealth
cd Companion-MentalHealth
```

---

### 1. Backend (FastAPI)
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*Logic orchestrated in `reasoning/orchestrator.py`.*

The API will be available at `http://localhost:8000

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`


---

## ▶️ Running the System

1. Start the **backend** first
2. Start the **frontend**
3. Open the frontend in your browser
4. Enter messages in the chat interface
5. View:

   * inferred mental health patterns
   * confidence levels
   * causal explanations
   * safety messages (if triggered)

---

## 🔐 Important Notes

* Ontology, SWRL rules, and reasoning logic **must not be modified** during integration.
* The system runs **locally only**.
* No user authentication or deployment is required.

---

## 🎓 Academic Focus

This project demonstrates:

* Explicit knowledge modeling
* Symbolic reasoning
* Explainable AI
* Ethical and safety-aware AI design

Designed for **Knowledge Representation & Reasoning coursework**.

