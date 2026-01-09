# Companion: Ontology-Driven Mental Health Chatbot

## Overview

**Companion** is an ontology-driven Knowledge Representation & Reasoning (KRR) chatbot designed to promote **explainable mental health risk awareness** for university students.
It analyzes user text to identify emotions, symptoms, and triggers, maps them onto a custom **mental health ontology (OWL)**, and applies **symbolic reasoning (SWRL + SPARQL)** to infer potential risk patterns.
The system provides **transparent, human-readable “why” explanations** for its inferences.

⚠️ *Companion is a non-clinical, educational support tool and does not provide medical diagnosis or therapy.*

---


## Key Features

* **Emotion & Symptom Extraction** from user text
* **Ontology-Based Mapping** using OWL and RDF
* **Symbolic Reasoning** via SWRL rules
* **SPARQL Querying** for inferred patterns
* **Explainable Outputs** with causal “why” explanations
* **Interactive Chat Interface** (React-based UI)
* **Ethical & Safety Alerts** (e.g crisis resources for high-risk indicators)

---

## Tech Stack

* **Backend:** Python, FastAPI
* **Frontend:** React, Vite
* **Semantic Web:** OWL, RDF, SWRL, SPARQL, RDFlib
* **NLP:** Keyword-based emotion & symptom extraction (spaCy and NLTK)

---

## Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/rayyan-merchant/Companion-MentalHealth.git
cd Companion-MentalHealth
```

### 2️⃣ Backend Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access the app at **[http://localhost:3000](http://localhost:3000)**.

---

## Usage

1. Start both backend and frontend servers
2. Open the chat UI in your browser
3. Enter a message describing your feelings or symptoms
4. View inferred mental health patterns, confidence levels, and clear explanations
5. Safety advisories appear automatically when high-risk indicators are detected

---

## Project Structure

```
agents/            Conversational logic modules
backend/           FastAPI backend & reasoning integration
frontend/          React chat UI
nlp/               Emotion & symptom extraction
ontology/          Mental health ontology (OWL and RDF)
reasoning/         SWRL rules & orchestrator
data/session_graphs/ Session-level knowledge graphs
```

---

## License

All rights are reserved by the project authors.
Permission is required for reuse, modification, or distribution.

---

## 👥 Project Contributors  

<div align="center">  <a href="https://www.linkedin.com/in/rayyanmerchant2004/" target="_blank">    <img src="https://img.shields.io/badge/Rayyan%20Merchant-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Rayyan Merchant"/>  </a>  <a href="https://www.linkedin.com/in/rija-ali-731095296" target="_blank">    <img src="https://img.shields.io/badge/Syeda%20Rija%20Ali-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Syeda Rija Ali"/>  </a>  <a href="https://www.linkedin.com/in/riya-bhart-339036287/" target="_blank">    <img src="https://img.shields.io/badge/Riya%20Bhart-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Riya Bhart"/>  </a></div>




