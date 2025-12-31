"""
Risk Ranking & Confidence Aggregation Layer
Phase 5 - Mental Health KRR System

This module ranks and prioritizes ALREADY-INFERRED mental risk states.
It does NOT perform inference, reasoning, or explanation.

RESPONSIBILITY SEPARATION:
- SWRL: Infers mental states (frozen)
- SPARQL: Materializes facts (frozen)
- Explainer (Phase-4): Explains why (complete)
- Ranker (Phase-5): Ranks & prioritizes (THIS MODULE)

CONSTRAINTS:
- No ontology modification
- No new SWRL rules
- No probabilistic inference
- No diagnosis or medical claims
- Deterministic, symbolic processing only
- Ranking ≠ reasoning ≠ explanation
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class ConfidenceLabel(Enum):
    """Symbolic confidence labels (non-probabilistic)."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SafetyFlag(Enum):
    """Safety flag levels for ranking override."""
    NONE = "NONE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


# Safety flag priority order (higher index = higher priority)
SAFETY_PRIORITY = {
    "NONE": 0,
    "MODERATE": 1,
    "HIGH": 2
}

# Evidence category weights for diversity scoring
# NOTE: These are NOT learned weights - they are fixed symbolic priorities
EVIDENCE_CATEGORIES = ["emotions", "symptoms", "triggers", "risk_factors"]


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class RankingSignals:
    """
    Symbolic signals used for ranking.
    All values are counts or boolean flags - NO probabilities.
    """
    rule_count: int = 0
    evidence_diversity: int = 0  # Number of distinct evidence categories
    total_evidence: int = 0
    has_persistence: bool = False
    safety_flag: str = "NONE"
    confidence_label: str = "LOW"


@dataclass
class RankedRiskState:
    """A ranked risk state with aggregation rationale."""
    risk_state: str
    rank: int
    confidence_label: str
    safety_flag: str
    signals: RankingSignals
    rationale: List[str]  # Internal explanation of ranking


@dataclass
class RankingResult:
    """Complete ranking output for an individual."""
    student_id: str
    ranked_states: List[RankedRiskState]
    primary_concern: Optional[str]  # Highest-ranked state
    aggregated_safety: str  # Overall safety level
    summary_rationale: str


# =============================================================================
# SIGNAL EXTRACTION
# =============================================================================

def _extract_signals(explanation: Dict[str, Any]) -> RankingSignals:
    """
    Extract ranking signals from an explanation output.
    
    Args:
        explanation: Output from explainer.py
        
    Returns:
        RankingSignals with symbolic values only
    """
    # Rule count
    rules_fired = explanation.get("rulesFired", [])
    rule_count = len(rules_fired)
    
    # Evidence diversity (count of non-empty categories)
    evidence = explanation.get("evidence", [])
    categories_present = set()
    for e in evidence:
        e_type = e.get("type", "").lower()
        if "emotion" in e_type:
            categories_present.add("emotions")
        elif "symptom" in e_type:
            categories_present.add("symptoms")
        elif "trigger" in e_type:
            categories_present.add("triggers")
        elif "risk" in e_type or "factor" in e_type:
            categories_present.add("risk_factors")
    
    evidence_diversity = len(categories_present)
    total_evidence = len(evidence)
    
    # Persistence check - use EXPLICIT boolean from explanation
    # DO NOT parse "repeated" from evidence text
    has_persistence = explanation.get("has_persistence", False)
    
    # Safety and confidence (direct from explanation)
    safety_flag = explanation.get("safety_flag", "NONE")
    confidence_label = explanation.get("confidence_label", "LOW")
    
    return RankingSignals(
        rule_count=rule_count,
        evidence_diversity=evidence_diversity,
        total_evidence=total_evidence,
        has_persistence=has_persistence,
        safety_flag=safety_flag,
        confidence_label=confidence_label
    )


# =============================================================================
# SYMBOLIC RANKING HEURISTICS
# =============================================================================

def _compute_rank_score(signals: RankingSignals) -> Tuple[int, int, int, int]:
    """
    Compute a symbolic ranking tuple for comparison.
    
    Returns a tuple for lexicographic comparison:
    (safety_priority, rule_score, diversity_score, persistence_score)
    
    Higher values = higher priority (will be ranked first).
    
    ⚠️ SAFETY OVERRIDE: HIGH safety flag automatically gets maximum priority.
    """
    # Component 1: Safety priority (HIGHEST WEIGHT)
    # HIGH safety flag ALWAYS ranks first regardless of other scores
    safety_priority = SAFETY_PRIORITY.get(signals.safety_flag, 0)
    
    # Component 2: Rule count score
    # More rules = more confidence in the inference
    if signals.rule_count >= 3:
        rule_score = 3
    elif signals.rule_count >= 2:
        rule_score = 2
    elif signals.rule_count >= 1:
        rule_score = 1
    else:
        rule_score = 0
    
    # Component 3: Evidence diversity score
    # Coverage across categories indicates stronger pattern
    if signals.evidence_diversity >= 4:
        diversity_score = 4
    elif signals.evidence_diversity >= 3:
        diversity_score = 3
    elif signals.evidence_diversity >= 2:
        diversity_score = 2
    else:
        diversity_score = 1
    
    # Component 4: Persistence score
    # Persistence indicates chronic rather than acute pattern
    persistence_score = 1 if signals.has_persistence else 0
    
    return (safety_priority, rule_score, diversity_score, persistence_score)


def _build_rationale(
    signals: RankingSignals,
    rank: int,
    total_states: int
) -> List[str]:
    """
    Build internal rationale explaining why this state received its rank.
    
    This is NOT user-facing but must be explainable for audit.
    """
    rationale = []
    
    # Safety escalation
    if signals.safety_flag == "HIGH":
        rationale.append("SAFETY OVERRIDE: HIGH safety flag places this at highest priority")
    elif signals.safety_flag == "MODERATE":
        rationale.append("Elevated priority due to MODERATE safety flag")
    
    # Rule firing
    if signals.rule_count >= 3:
        rationale.append(f"Strong rule support: {signals.rule_count} independent rules fired")
    elif signals.rule_count >= 2:
        rationale.append(f"Moderate rule support: {signals.rule_count} rules fired")
    elif signals.rule_count == 1:
        rationale.append("Limited rule support: single rule fired")
    else:
        rationale.append("No explicit rules tracked for this state")
    
    # Evidence diversity
    if signals.evidence_diversity >= 3:
        rationale.append(f"High evidence diversity: {signals.evidence_diversity} categories covered")
    elif signals.evidence_diversity >= 2:
        rationale.append(f"Moderate evidence diversity: {signals.evidence_diversity} categories")
    else:
        rationale.append("Low evidence diversity: limited category coverage")
    
    # Persistence
    if signals.has_persistence:
        rationale.append("Persistence detected: repeated stress exposure present")
    else:
        rationale.append("No persistence signal: may be acute/situational")
    
    # Relative position
    if rank == 1 and total_states > 1:
        rationale.append(f"Ranked highest of {total_states} states for this individual")
    elif rank == total_states and total_states > 1:
        rationale.append(f"Ranked lowest of {total_states} states")
    
    return rationale


# =============================================================================
# CONFIDENCE AGGREGATION
# =============================================================================

def _aggregate_confidence(signals: RankingSignals) -> str:
    """
    Produce a single aggregated confidence label.
    
    Based ONLY on:
    - Number of rules fired
    - Evidence diversity
    - Persistence flags
    
    ⚠️ IMPORTANT: Safety ≠ Confidence
    If safety_flag == HIGH AND rule_count == 1, confidence is capped at MEDIUM.
    Safety overrides RANKING only, never confidence.
    
    ❌ No probabilities
    ❌ No numeric scores exposed
    """
    score = 0
    
    # Rule contribution
    if signals.rule_count >= 3:
        score += 3
    elif signals.rule_count >= 2:
        score += 2
    elif signals.rule_count >= 1:
        score += 1
    
    # Diversity contribution
    if signals.evidence_diversity >= 4:
        score += 3
    elif signals.evidence_diversity >= 3:
        score += 2
    elif signals.evidence_diversity >= 2:
        score += 1
    
    # Persistence contribution
    if signals.has_persistence:
        score += 2
    
    # Evidence volume contribution
    if signals.total_evidence >= 5:
        score += 1
    
    # Map to label
    if score >= 7:
        confidence = ConfidenceLabel.HIGH.value
    elif score >= 4:
        confidence = ConfidenceLabel.MEDIUM.value
    else:
        confidence = ConfidenceLabel.LOW.value
    
    # ⚠️ SAFETY ≠ CONFIDENCE RULE:
    # If HIGH safety flag AND single rule fired, cap confidence at MEDIUM
    # Safety overrides RANKING only, never artificially inflates confidence
    if signals.safety_flag == "HIGH" and signals.rule_count == 1:
        if confidence == ConfidenceLabel.HIGH.value:
            confidence = ConfidenceLabel.MEDIUM.value
    
    return confidence


# =============================================================================
# MAIN RANKING FUNCTION
# =============================================================================

def rank_risk_states(
    student_id: str,
    explanations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Rank multiple risk states for a single individual.
    
    This function DOES NOT infer states - it only ranks already-inferred states.
    
    Args:
        student_id: Identifier for the student
        explanations: List of explanation outputs from explainer.py
                     Each should contain: riskState, rulesFired, evidence,
                     confidence_label, safety_flag
    
    Returns:
        Ranking result with:
        - ranked_states: List ordered by priority (index 0 = highest)
        - primary_concern: The highest-ranked risk state
        - aggregated_safety: Overall safety level for the individual
        - summary_rationale: Brief explanation of ranking
    
    ⚠️ SAFETY OVERRIDE: Any HIGH safety_flag automatically ranks highest.
    """
    if not explanations:
        return {
            "student_id": student_id,
            "ranked_states": [],
            "primary_concern": None,
            "aggregated_safety": "NONE",
            "summary_rationale": "No risk states to rank"
        }
    
    # Extract signals for each explanation
    states_with_signals = []
    for expl in explanations:
        risk_state = expl.get("riskState", expl.get("mental_state", "Unknown"))
        signals = _extract_signals(expl)
        rank_tuple = _compute_rank_score(signals)
        
        states_with_signals.append({
            "risk_state": risk_state,
            "signals": signals,
            "rank_tuple": rank_tuple,
            "original": expl
        })
    
    # Sort by rank tuple (descending - higher values first)
    states_with_signals.sort(key=lambda x: x["rank_tuple"], reverse=True)
    
    # Build ranked states
    ranked_states = []
    total_states = len(states_with_signals)
    
    for i, state_data in enumerate(states_with_signals):
        rank = i + 1  # 1-indexed rank
        signals = state_data["signals"]
        
        # Aggregate confidence
        aggregated_confidence = _aggregate_confidence(signals)
        
        # Build rationale
        rationale = _build_rationale(signals, rank, total_states)
        
        ranked_state = {
            "risk_state": state_data["risk_state"],
            "rank": rank,
            "confidence_label": aggregated_confidence,
            "safety_flag": signals.safety_flag,
            "signals": {
                "rule_count": signals.rule_count,
                "evidence_diversity": signals.evidence_diversity,
                "total_evidence": signals.total_evidence,
                "has_persistence": signals.has_persistence
            },
            "rationale": rationale
        }
        ranked_states.append(ranked_state)
    
    # Determine primary concern and aggregated safety
    primary_concern = ranked_states[0]["risk_state"] if ranked_states else None
    
    # ⚠️ EXPLICIT AGGREGATED SAFETY SHORT-CIRCUIT
    # If ANY state has HIGH safety flag, aggregated_safety is HIGH
    # This improves audit clarity
    if any(s["safety_flag"] == "HIGH" for s in ranked_states):
        aggregated_safety = "HIGH"
    elif any(s["safety_flag"] == "MODERATE" for s in ranked_states):
        aggregated_safety = "MODERATE"
    else:
        aggregated_safety = "NONE"
    
    # Summary rationale
    if len(ranked_states) == 1:
        summary_rationale = f"Single risk state identified: {primary_concern}"
    else:
        summary_rationale = (
            f"{primary_concern} ranked highest of {total_states} states. "
            f"Ranking based on safety priority, rule support, and evidence diversity."
        )
    
    if aggregated_safety == "HIGH":
        summary_rationale += " ⚠️ HIGH safety flag detected - prioritize support."
    
    return {
        "student_id": student_id,
        "ranked_states": ranked_states,
        "primary_concern": primary_concern,
        "aggregated_safety": aggregated_safety,
        "summary_rationale": summary_rationale
    }


def rank_batch(
    student_explanations: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Dict[str, Any]]:
    """
    Rank risk states for multiple students.
    
    Args:
        student_explanations: Dict mapping student_id to list of explanations
        
    Returns:
        Dict mapping student_id to ranking result
    """
    results = {}
    for student_id, explanations in student_explanations.items():
        results[student_id] = rank_risk_states(student_id, explanations)
    return results


# =============================================================================
# EXAMPLE OUTPUT (SYNTHETIC DEMONSTRATION)
# =============================================================================

def generate_example_output() -> Dict[str, Any]:
    """
    Generate synthetic example demonstrating ranking with:
    - Multiple mental states
    - Safety override case
    
    This is for documentation/testing purposes only.
    """
    
    # Synthetic explanations for demonstration
    example_explanations = [
        {
            "riskState": "AnxietyRisk",
            "rulesFired": ["R_ANX_01", "R_ANX_02"],
            "evidence": [
                {"type": "Emotion", "value": "Stress"},
                {"type": "Emotion", "value": "Anxiety"},
                {"type": "Symptom", "value": "Insomnia"},
                {"type": "Trigger", "value": "Exam Pressure"},
                {"type": "Risk Factor", "value": "Repeated Stress Exposure"}
            ],
            "confidence_label": "MEDIUM",
            "safety_flag": "MODERATE",
            "uncertaintyDrivers": []
        },
        {
            "riskState": "PanicRisk",
            "rulesFired": ["R_PAN_01"],
            "evidence": [
                {"type": "Emotion", "value": "Anxiety"},
                {"type": "Symptom", "value": "Rapid Heart Rate"},
                {"type": "Symptom", "value": "Breathing Difficulty"}
            ],
            "confidence_label": "MEDIUM",
            "safety_flag": "HIGH",  # ⚠️ This will trigger safety override
            "uncertaintyDrivers": ["Missing persistence"]
        },
        {
            "riskState": "AcademicStress",
            "rulesFired": ["R_ACS_01a"],
            "evidence": [
                {"type": "Emotion", "value": "Stress"},
                {"type": "Trigger", "value": "Exam Pressure"}
            ],
            "confidence_label": "LOW",
            "safety_flag": "NONE",
            "uncertaintyDrivers": ["Limited evidence", "Single rule fired"]
        }
    ]
    
    # Run ranking
    result = rank_risk_states("example_student_001", example_explanations)
    
    return {
        "description": "Example demonstrating safety override ranking",
        "input_states_count": len(example_explanations),
        "ranking_result": result,
        "notes": [
            "PanicRisk ranks #1 despite fewer rules due to HIGH safety flag",
            "AnxietyRisk ranks #2 with strong evidence diversity",
            "AcademicStress ranks #3 with limited signals"
        ]
    }
