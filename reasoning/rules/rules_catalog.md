# 📘 `reasoning/rules/rule_catalog.md`

## Purpose

This document defines the **complete symbolic reasoning inventory** for the Mental Health KRR system.

Each rule specifies:

* which **ontology-aligned evidence patterns** trigger reasoning
* which **MentalState / RiskState** is inferred
* why the rule exists (causal intent)
* how it supports **explainability and safety**

This catalog is **authoritative** for SWRL implementation.

---

## 🔒 Global Rule Constraints

All rules:

* use **only ontology-defined classes & properties**
* infer **MentalState / Risk classes only**
* do **not** encode confidence, thresholds, or statistics
* do **not** perform escalation
* must be explainable via evidence provenance

---

## 🟦 Academic Stress & Anxiety Rules

---

### **Rule ID:** `R_ACS_01`

**If (Evidence):**

* `Stress` (Emotion)
* `ExamStressor` OR `WorkloadStressor` (Trigger)

**Ontology Preconditions:**

* `experiencesEmotion`
* `triggeredBy`

**Then (Infer):**

* `AcademicStress`

**Intent:**
Detect academic-context stress patterns.

**Explanation Goal:**
Explain stress as **situationally driven**, not pathological.

---

### **Rule ID:** `R_ANX_01`

**If:**

* `Stress`
* `Insomnia`
* `ExamStressor`

**Then:**

* `AnxietyRisk`

**Intent:**
Detect anxiety emerging from **sleep disruption + academic pressure**.

**Explanation Goal:**
Show how physiological symptoms + stressors combine causally.

---

### **Rule ID:** `R_ANX_02`

**If:**

* `Anxiety`
* `RepeatedStressExposure`

**Then:**

* `AnxietyRisk`

**Intent:**
Capture **persistence-driven anxiety**, not single events.

**Explanation Goal:**
Highlight accumulation over time.

---

## 🟦 Burnout & Chronic Stress Rules

---

### **Rule ID:** `R_BRN_01`

**If:**

* `Emotional_Overwhelm`
* `WorkloadStressor`
* `RepeatedStressExposure`

**Then:**

* `BurnoutRisk`

**Intent:**
Detect long-term overload patterns.

**Explanation Goal:**
Explain burnout as **chronic exposure**, not intensity.

---

### **Rule ID:** `R_BRN_02`

**If:**

* `Stress`
* `Fatigue`
* `RepeatedStressExposure`

**Then:**

* `BurnoutRisk`

**Intent:**
Capture physical + emotional depletion.

---

## 🟦 Panic & Acute Stress Rules

---

### **Rule ID:** `R_PAN_01`

**If:**

* `Anxiety`
* `RapidHeartRate`
* `BreathDifficulty`

**Then:**

* `PanicRisk`

**Intent:**
Detect panic-like physiological patterns.

**Explanation Goal:**
Explain panic as **acute physiological escalation**, not generalized anxiety.

---

## 🟦 Depressive Spectrum Rules (Soft Escalation Domain)

---

### **Rule ID:** `R_DEP_01`

**If:**

* `SocialISolationRisk`
* `Emotional_Overwhelm`
* `RepeatedStressExposure`

**Then:**

* `DepressiveSpectrum`

**Intent:**
Detect **withdrawal-based low mood patterns**.

**Safety Note:**
Does NOT imply diagnosis.
Triggers **soft escalation eligibility only**.

---

### **Rule ID:** `R_DEP_02`

**If:**

* `Fatigue`
* `Insomnia`
* `SocialISolationRisk`

**Then:**

* `DepressiveSpectrum`

**Intent:**
Identify behavioral + physiological convergence.

---

## 🟦 Risk-Level Attribution Rules (Non-Clinical)

---

### **Rule ID:** `R_RISK_01`

**If:**

* `AnxietyRisk` OR `BurnoutRisk`
* `RepeatedStressExposure`

**Then:**

* `ModerateRisk`

**Intent:**
Expose non-clinical risk stratification for explanations.

---

### **Rule ID:** `R_RISK_02`

**If:**

* `PanicRisk`
* `RepeatedStressExposure`

**Then:**

* `HighRisk`

**Intent:**
Flag acute patterns (still **non-diagnostic**).

