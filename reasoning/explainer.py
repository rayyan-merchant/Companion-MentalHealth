"""
Explanation Engine for Mental Health KRR System
Phase 4 - Symbolic WHY-Engine for Post-Inference Explanation

Converts materialized graph facts into human-readable, auditable explanations.
Answers: "Why was this mental risk state inferred?"

CONSTRAINTS:
- No reasoning, rule firing, or SPARQL inference
- No NLP or ML
- No clinical claims or diagnosis
- All truth from materialized RDF triples only
- Safety-first language for high-risk states
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class SafetyFlag(Enum):
    """
    Risk level flags for safety-aware explanations.
    
    NOTE: Safety flag reflects escalation sensitivity, not certainty or severity.
    It determines language softening and support messaging, not clinical risk.
    """
    NONE = "NONE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class ConfidenceLabel(Enum):
    """Symbolic confidence labels (non-probabilistic)."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class ExplanationResult:
    """Structured explanation output - STRICT format."""
    student_id: str
    riskState: str
    confidence_label: str
    rulesFired: List[str]
    evidence: List[Dict[str, str]]
    causalChain: List[str]
    uncertaintyDrivers: List[str]
    explanation_text: str
    safety_flag: str


# =============================================================================
# RULE CATALOG (for rule ID to description mapping)
# =============================================================================

RULE_DESCRIPTIONS = {
    "R_ACS_01a": "Academic stress from exam pressure",
    "R_ACS_01b": "Academic stress from workload",
    "R_ANX_01": "Anxiety risk from stress, insomnia, and exam pressure",
    "R_ANX_02": "Anxiety risk from repeated stress exposure",
    "R_BRN_01": "Burnout risk from emotional overwhelm and workload",
    "R_BRN_02": "Burnout risk from stress, fatigue, and repeated exposure",
    "R_PAN_01": "Panic risk from anxiety with physiological symptoms",
    "R_DEP_01": "Depressive spectrum from isolation and emotional overwhelm",
    "R_DEP_02": "Depressive spectrum from fatigue, insomnia, and isolation",
    "R_RISK_01a": "Moderate risk from anxiety with repeated stress",
    "R_RISK_01b": "Moderate risk from burnout with repeated stress",
    "R_RISK_02": "High risk from panic with repeated stress"
}


# =============================================================================
# MENTAL STATE TEMPLATES
# =============================================================================

MENTAL_STATE_TEMPLATES = {
    "AcademicStress": {
        "description": "Academic Stress",
        "reasoning": (
            "This pattern reflects academic pressure combined with emotional strain, "
            "commonly associated with stress responses in educational settings."
        ),
        "notes": (
            "This observation reflects situational factors and does not constitute "
            "a clinical assessment."
        )
    },
    "AnxietyRisk": {
        "description": "Anxiety Risk Indicators",
        "reasoning": (
            "The observed combination of emotional distress, symptoms, and stressors "
            "aligns with patterns commonly associated with elevated anxiety responses."
        ),
        "notes": (
            "This is an observational pattern, not a diagnosis. Speaking with a "
            "counselor may be helpful if experiences persist."
        )
    },
    "BurnoutRisk": {
        "description": "Burnout Risk Indicators",
        "reasoning": (
            "The pattern of emotional overwhelm, fatigue, and sustained stressors "
            "is commonly associated with burnout from chronic strain."
        ),
        "notes": (
            "Burnout patterns are observational. Rest and workload management "
            "may support recovery."
        )
    },
    "PanicRisk": {
        "description": "Panic Risk Indicators",
        "reasoning": (
            "Anxiety with acute physiological symptoms suggests a heightened "
            "stress response beyond generalized anxiety."
        ),
        "notes": (
            "If physical symptoms are severe, seeking professional evaluation "
            "is recommended."
        )
    },
    "DepressiveSpectrum": {
        "description": "Depressive Spectrum Indicators",
        "reasoning": (
            "Social withdrawal, emotional overwhelm, and physiological symptoms "
            "align with withdrawal-based low mood patterns."
        ),
        "notes": (
            "This is non-diagnostic. Connecting with support services is encouraged "
            "if feelings persist."
        )
    },
    "ModerateRisk": {
        "description": "Moderate Risk Level",
        "reasoning": (
            "Mental state patterns combined with repeated stress exposure suggest "
            "a moderate level of concern worth monitoring."
        ),
        "notes": "Self-awareness and access to support resources may be beneficial."
    },
    "HighRisk": {
        "description": "Elevated Concern Level",
        "reasoning": "This pattern suggests elevated concern.",
        "notes": (
            "If distress is ongoing, seeking professional or institutional support "
            "may be beneficial. You are not alone."
        )
    }
}

HIGH_RISK_SUPPORT_NOTE = (
    "\n\n⚠️ Support Note: If you are experiencing ongoing distress, please consider "
    "reaching out to a counselor or trusted support person. Help is available."
)


# =============================================================================
# EVIDENCE PROCESSING
# =============================================================================

def _format_class_name(class_uri: str) -> str:
    """Convert ontology URI to human-readable label."""
    if '#' in class_uri:
        class_uri = class_uri.split('#')[-1]
    if '/' in class_uri:
        class_uri = class_uri.split('/')[-1]
    
    # Add spaces before capitals and replace underscores
    result = []
    for i, char in enumerate(class_uri.replace('_', ' ')):
        if char.isupper() and i > 0 and class_uri[i-1] not in (' ', '_'):
            result.append(' ')
        result.append(char)
    return ''.join(result).strip()


def _categorize_evidence(sparql_results: Dict[str, Any]) -> Dict[str, List[str]]:
    """Group evidence by category."""
    categories = {"emotions": [], "symptoms": [], "triggers": [], "risk_factors": []}
    
    type_map = {
        "emotions": ["emotionType", "emotion"],
        "symptoms": ["symptomType", "symptom"],
        "triggers": ["triggerType", "trigger"],
        "risk_factors": ["riskFactorType", "riskFactor"]
    }
    
    for category, keys in type_map.items():
        source_key = category if category in sparql_results else category.replace('_', '')
        if source_key in sparql_results:
            for item in sparql_results[source_key]:
                for key in keys:
                    if key in item and item[key]:
                        categories[category].append(_format_class_name(item[key]))
                        break
    
    # Handle bindings format
    if "bindings" in sparql_results:
        for binding in sparql_results["bindings"]:
            for category, keys in type_map.items():
                for key in keys:
                    if key in binding:
                        val = binding[key].get("value", "") if isinstance(binding[key], dict) else binding[key]
                        if val:
                            categories[category].append(_format_class_name(val))
    
    # Deduplicate
    for key in categories:
        categories[key] = list(dict.fromkeys(categories[key]))
    
    return categories


def _build_evidence_list(categories: Dict[str, List[str]]) -> List[Dict[str, str]]:
    """Build structured evidence list."""
    evidence = []
    labels = {"emotions": "Emotion", "symptoms": "Symptom", 
              "triggers": "Trigger", "risk_factors": "Risk Factor"}
    
    for cat, label in labels.items():
        for item in categories.get(cat, []):
            evidence.append({"type": label, "value": item})
    return evidence


# =============================================================================
# CAUSAL CHAIN CONSTRUCTION
# =============================================================================

def _build_causal_chain(
    categories: Dict[str, List[str]],
    rules_fired: List[str],
    risk_state: str
) -> List[str]:
    """
    Construct explicit causal chain: Emotion → Symptom → Trigger → Rule → Mental State
    
    Returns ordered list of human-readable steps.
    """
    chain = []
    
    # Step 1: Emotions detected
    if categories.get("emotions"):
        emotions_str = ", ".join(categories["emotions"][:3])  # Limit for readability
        chain.append(f"Emotional state observed: {emotions_str}")
    
    # Step 2: Symptoms manifested
    if categories.get("symptoms"):
        symptoms_str = ", ".join(categories["symptoms"][:3])
        chain.append(f"Symptoms manifested: {symptoms_str}")
    
    # Step 3: Triggers identified
    if categories.get("triggers"):
        triggers_str = ", ".join(categories["triggers"][:3])
        chain.append(f"Triggers identified: {triggers_str}")
    
    # Step 4: Risk factors present
    if categories.get("risk_factors"):
        rf_str = ", ".join(categories["risk_factors"][:3])
        chain.append(f"Risk factors present: {rf_str}")
    
    # Step 5: Rules fired
    if rules_fired:
        rule_desc = [RULE_DESCRIPTIONS.get(r, r) for r in rules_fired[:3]]
        chain.append(f"Reasoning patterns matched: {'; '.join(rule_desc)}")
    
    # Step 6: Mental state inferred
    state_desc = MENTAL_STATE_TEMPLATES.get(risk_state, {}).get("description", risk_state)
    chain.append(f"Mental state inferred: {state_desc}")
    
    return chain


# =============================================================================
# UNCERTAINTY DRIVERS (Non-Probabilistic)
# =============================================================================

def _identify_uncertainty_drivers(
    categories: Dict[str, List[str]],
    rules_fired: List[str],
    has_persistence: bool
) -> List[str]:
    """
    Identify symbolic uncertainty sources.
    
    Returns explanatory strings, NOT scores.
    These do NOT affect ranking directly - they are for explanation only.
    
    Uncertainty drivers are distinct from evidence absence:
    - Uncertainty = incomplete information that limits confidence
    - Absence = missing evidence (may be expected or unexpected)
    """
    drivers = []
    
    # Count total evidence
    total_evidence = sum(len(v) for v in categories.values())
    
    # Driver: Limited evidence (uncertainty)
    if total_evidence < 3:
        drivers.append("Limited evidence: fewer than 3 distinct factors identified")
    
    # Driver: Single rule fired (uncertainty)
    if len(rules_fired) == 1:
        drivers.append("Single reasoning pattern: only one rule matched the evidence")
    elif len(rules_fired) == 0:
        drivers.append("No explicit rules: inference based on class membership only")
    
    # Driver: Missing persistence (uncertainty) - from explicit flag, NOT string matching
    if not has_persistence and total_evidence > 0:
        drivers.append("Missing persistence: no repeated stress exposure detected")
    
    # Driver: Weak causal diversity (uncertainty)
    non_empty_categories = sum(1 for v in categories.values() if v)
    if non_empty_categories < 2:
        drivers.append("Weak causal diversity: evidence from only one category")
    
    # Driver: Missing symptoms (evidence absence)
    if not categories.get("symptoms") and categories.get("emotions"):
        drivers.append("No physiological symptoms: emotional evidence only")
    
    # Driver: Missing triggers (evidence absence)
    if not categories.get("triggers"):
        drivers.append("No situational triggers identified")
    
    return drivers


# =============================================================================
# SYMBOLIC CONFIDENCE (Non-Probabilistic)
# =============================================================================

def _compute_confidence_label(
    categories: Dict[str, List[str]],
    rules_fired: List[str],
    has_persistence: bool
) -> ConfidenceLabel:
    """
    Compute symbolic confidence based ONLY on:
    - Number of rules fired
    - Evidence diversity
    - Persistence flags (explicit boolean, NOT string matching)
    
    NO numeric probabilities.
    """
    score = 0
    
    # Rules factor
    if len(rules_fired) >= 3:
        score += 2
    elif len(rules_fired) >= 2:
        score += 1
    
    # Evidence diversity factor
    non_empty = sum(1 for v in categories.values() if v)
    if non_empty >= 3:
        score += 2
    elif non_empty >= 2:
        score += 1
    
    # Persistence factor (from explicit boolean flag)
    if has_persistence:
        score += 1
    
    # Total evidence volume
    total_evidence = sum(len(v) for v in categories.values())
    if total_evidence >= 5:
        score += 1
    
    # Map to label
    if score >= 5:
        return ConfidenceLabel.HIGH
    elif score >= 3:
        return ConfidenceLabel.MEDIUM
    else:
        return ConfidenceLabel.LOW


# =============================================================================
# SAFETY FLAG DETERMINATION
# =============================================================================

def _determine_safety_flag(escalation_flags: Dict[str, bool]) -> SafetyFlag:
    """Determine safety flag from escalation flags."""
    high_risk_keys = ["HighRisk", "high_risk", "PanicRisk", "panic_risk"]
    moderate_keys = ["ModerateRisk", "moderate_risk", "DepressiveSpectrum", 
                     "depressive_spectrum", "multiple_states"]
    
    if any(escalation_flags.get(k, False) for k in high_risk_keys):
        return SafetyFlag.HIGH
    if any(escalation_flags.get(k, False) for k in moderate_keys):
        return SafetyFlag.MODERATE
    return SafetyFlag.NONE


# =============================================================================
# EXPLANATION TEXT GENERATION
# =============================================================================

def _build_explanation_text(
    risk_state: str,
    categories: Dict[str, List[str]],
    causal_chain: List[str],
    safety_flag: SafetyFlag
) -> str:
    """Build human-readable explanation with safety awareness."""
    template = MENTAL_STATE_TEMPLATES.get(risk_state, {})
    
    # Detected Factors section
    text = "Detected Factors:\n"
    has_factors = False
    for cat, label in [("emotions", "Emotion"), ("symptoms", "Symptom"),
                       ("triggers", "Trigger"), ("risk_factors", "Risk Factor")]:
        for item in categories.get(cat, []):
            text += f"  • {label}: {item}\n"
            has_factors = True
    if not has_factors:
        text += "  • No specific factors identified\n"
    
    # Inferred State section
    text += f"\nInferred State:\n  • {template.get('description', risk_state)}\n"
    
    # Reasoning Basis section (minimal for HIGH risk)
    text += "\nReasoning Basis:\n"
    if safety_flag == SafetyFlag.HIGH:
        text += f"  {template.get('reasoning', 'Pattern observed.')[:100]}...\n"
    else:
        text += f"  {template.get('reasoning', 'Pattern observed based on identified factors.')}\n"
    
    # Notes section
    text += f"\nNotes:\n  {template.get('notes', 'This is an observational assessment.')}"
    
    # High-risk support note
    if safety_flag == SafetyFlag.HIGH:
        text += HIGH_RISK_SUPPORT_NOTE
    
    return text


# =============================================================================
# PUBLIC API
# =============================================================================

def generate_explanation(
    student_id: str,
    sparql_results: Dict[str, Any],
    escalation_flags: Dict[str, bool],
    rules_fired: Optional[List[str]] = None,
    has_persistence: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Generate a human-readable explanation for an inferred mental state.
    
    Args:
        student_id: URI or identifier for the student
        sparql_results: Evidence triples from SPARQL queries
        escalation_flags: Boolean flags for risk levels
        rules_fired: List of rule IDs that fired (e.g., ["R_ANX_01", "R_ANX_02"])
        has_persistence: Explicit boolean flag for RepeatedStressExposure
                        (from SPARQL materialization, NOT string matching)
    
    Returns:
        Structured explanation with format:
        {
            "student_id": "...",
            "riskState": "...",
            "has_persistence": true | false,
            "confidence_label": "LOW | MEDIUM | HIGH",
            "rulesFired": [...],
            "evidence": [...],
            "causalChain": [...],
            "uncertainty_drivers": [...],
            "explanation_text": "...",
            "safety_flag": "NONE | MODERATE | HIGH"
        }
        
        Note: safety_flag reflects escalation sensitivity, not certainty or severity.
    """
    rules_fired = rules_fired or []
    
    # Process evidence
    categories = _categorize_evidence(sparql_results)
    evidence = _build_evidence_list(categories)
    
    # Determine persistence from explicit input OR sparql_results
    # DO NOT use string matching on evidence text
    if has_persistence is None:
        has_persistence = sparql_results.get("has_persistence", False)
    
    # Determine risk state
    risk_state = sparql_results.get("mentalState") or sparql_results.get("riskState")
    if not risk_state:
        for state in ["AcademicStress", "AnxietyRisk", "BurnoutRisk", 
                      "PanicRisk", "DepressiveSpectrum", "ModerateRisk", "HighRisk"]:
            if escalation_flags.get(state, False):
                risk_state = state
                break
    risk_state = _format_class_name(risk_state) if risk_state else "Unknown"
    
    # Determine flags and confidence
    safety_flag = _determine_safety_flag(escalation_flags)
    confidence_label = _compute_confidence_label(categories, rules_fired, has_persistence)
    
    # Build causal chain
    causal_chain = _build_causal_chain(categories, rules_fired, risk_state)
    
    # Identify uncertainty drivers (separate from evidence absence)
    uncertainty_drivers = _identify_uncertainty_drivers(categories, rules_fired, has_persistence)
    
    # Generate explanation text
    explanation_text = _build_explanation_text(risk_state, categories, causal_chain, safety_flag)
    
    # Return format with explicit has_persistence
    return {
        "student_id": student_id,
        "riskState": risk_state,
        "has_persistence": has_persistence,
        "confidence_label": confidence_label.value,
        "rulesFired": rules_fired,
        "evidence": evidence,
        "causalChain": causal_chain,
        "uncertainty_drivers": uncertainty_drivers,
        "explanation_text": explanation_text,
        "safety_flag": safety_flag.value
    }


def generate_batch_explanations(
    student_results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate explanations for multiple students."""
    return [
        generate_explanation(
            student_id=s.get("student_id", "unknown"),
            sparql_results=s.get("sparql_results", {}),
            escalation_flags=s.get("escalation_flags", {}),
            rules_fired=s.get("rules_fired", [])
        )
        for s in student_results
    ]
