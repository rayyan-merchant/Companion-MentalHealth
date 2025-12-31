"""
Safety, Escalation & Audit Layer
Phase 6 - Mental Health KRR System (Final Symbolic Layer)

This module produces escalation decisions, safety justifications, and audit trails.
It consumes outputs from Phase-5 (ranker.py) and SPARQL escalation checks.

RESPONSIBILITY:
- Does NOT infer mental states (SWRL does that)
- Does NOT materialize facts (SPARQL does that)
- Does NOT explain (explainer.py does that)
- Does NOT rank (ranker.py does that)
- ONLY produces escalation decisions with full audit trail

CONSTRAINTS:
- Symbolic logic only
- No ML/probabilistic models
- No diagnosis or treatment
- Advisory escalation only
- Always include disclaimer
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# CONSTANTS & ENUMS
# =============================================================================

class EscalationLevel(Enum):
    """Escalation levels - advisory only, not diagnostic."""
    NONE = "NONE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Mandatory disclaimer
DISCLAIMER = "This system does not provide medical diagnosis or treatment."

# Support recommendations by escalation level
SUPPORT_RECOMMENDATIONS = {
    EscalationLevel.CRITICAL: (
        "Immediate support may be beneficial. Please consider reaching out to a counselor, "
        "mental health professional, or trusted support person. Help is available."
    ),
    EscalationLevel.HIGH: (
        "Speaking with a counselor or mental health professional may be helpful. "
        "Support resources are available if you need them."
    ),
    EscalationLevel.MODERATE: (
        "Self-care and access to support resources may be beneficial. "
        "Consider speaking with someone you trust if concerns persist."
    ),
    EscalationLevel.NONE: (
        "No immediate escalation indicated. Continue healthy coping practices."
    )
}


# =============================================================================
# ESCALATION LOGIC (SYMBOLIC ONLY)
# =============================================================================

def _determine_escalation_level(
    escalation_findings: Dict[str, bool]
) -> EscalationLevel:
    """
    Determine escalation level based on symbolic conditions.
    
    Escalation Logic (from specification):
    | Condition                          | Escalation |
    | ---------------------------------- | ---------- |
    | HighRisk present                   | CRITICAL   |
    | PanicRisk + RepeatedStressExposure | HIGH       |
    | DepressiveSpectrum                 | HIGH       |
    | Multiple mental states             | MODERATE   |
    | ModerateRisk only                  | MODERATE   |
    | Else                               | NONE       |
    
    ⚠️ Escalation is advisory, not diagnostic.
    """
    # CRITICAL: HighRisk present
    if escalation_findings.get("high_risk", False):
        return EscalationLevel.CRITICAL
    
    # HIGH: PanicRisk + RepeatedStressExposure
    if escalation_findings.get("panic_with_persistence", False):
        return EscalationLevel.HIGH
    
    # HIGH: DepressiveSpectrum
    if escalation_findings.get("depressive_spectrum", False):
        return EscalationLevel.HIGH
    
    # MODERATE: Multiple mental states
    if escalation_findings.get("multiple_states", False):
        return EscalationLevel.MODERATE
    
    # MODERATE: ModerateRisk only
    if escalation_findings.get("moderate_risk", False):
        return EscalationLevel.MODERATE
    
    # NONE: Default
    return EscalationLevel.NONE


def _build_escalation_reasons(
    escalation_findings: Dict[str, bool],
    escalation_level: EscalationLevel
) -> List[str]:
    """
    Build list of reasons for the escalation decision.
    Each reason is traceable to a SPARQL query.
    """
    reasons = []
    
    if escalation_findings.get("high_risk", False):
        reasons.append("HighRisk classification detected (escalation_checks.sparql: HighRisk query)")
    
    if escalation_findings.get("panic_with_persistence", False):
        reasons.append("PanicRisk with RepeatedStressExposure (escalation_checks.sparql: panic_persistence query)")
    
    if escalation_findings.get("depressive_spectrum", False):
        reasons.append("DepressiveSpectrum indicators present (escalation_checks.sparql: depressive query)")
    
    if escalation_findings.get("multiple_states", False):
        reasons.append("Multiple risk states detected for same individual (escalation_checks.sparql: multiple_states query)")
    
    if escalation_findings.get("moderate_risk", False):
        reasons.append("ModerateRisk classification (escalation_checks.sparql: moderate_risk query)")
    
    if not reasons:
        reasons.append("No escalation triggers detected")
    
    return reasons


def _build_audit_trail(
    escalation_findings: Dict[str, bool],
    ranking_result: Dict[str, Any],
    escalation_level: EscalationLevel
) -> Dict[str, Any]:
    """
    Build complete audit trail for the escalation decision.
    This ensures the decision is fully traceable and auditable.
    """
    # Identify which SPARQL queries were triggered
    triggered_queries = []
    query_map = {
        "high_risk": "SELECT ?student WHERE { ?student rdf:type krr:HighRisk }",
        "panic_with_persistence": "SELECT ?student WHERE { ?student rdf:type krr:PanicRisk ; krr:hasRiskFactor [rdf:type krr:RepeatedStressExposure] }",
        "depressive_spectrum": "SELECT ?student WHERE { ?student rdf:type krr:DepressiveSpectrum }",
        "multiple_states": "SELECT ?student (COUNT(?state) AS ?count) WHERE { ... } HAVING (?count > 1)",
        "moderate_risk": "SELECT ?student WHERE { ?student rdf:type krr:ModerateRisk }"
    }
    
    for key, query in query_map.items():
        if escalation_findings.get(key, False):
            triggered_queries.append({
                "finding": key,
                "query_pattern": query,
                "result": True
            })
    
    # Check for safety override
    aggregated_safety = ranking_result.get("aggregated_safety", "NONE")
    safety_override = aggregated_safety == "HIGH"
    
    return {
        "triggered_queries": triggered_queries,
        "ranker_summary": ranking_result.get("summary_rationale", "No ranking summary available"),
        "safety_override": safety_override,
        "escalation_determination": {
            "level": escalation_level.value,
            "logic": "Symbolic condition matching from escalation_checks.sparql",
            "deterministic": True
        }
    }


# =============================================================================
# MAIN ESCALATION FUNCTION
# =============================================================================

def evaluate_escalation(
    student_id: str,
    ranking_result: Dict[str, Any],
    escalation_findings: Dict[str, bool]
) -> Dict[str, Any]:
    """
    Evaluate escalation for a student based on ranking and SPARQL findings.
    
    This function DOES NOT infer, rank, or explain.
    It ONLY produces escalation decisions with full audit trail.
    
    Args:
        student_id: Student identifier
        ranking_result: Output from ranker.py containing:
            - ranked_states
            - primary_concern
            - aggregated_safety
            - summary_rationale
        escalation_findings: Boolean flags from SPARQL escalation queries:
            - high_risk: bool
            - panic_with_persistence: bool
            - multiple_states: bool
            - depressive_spectrum: bool
            - moderate_risk: bool
    
    Returns:
        Escalation result with:
        - student_id
        - escalation_level: CRITICAL | HIGH | MODERATE | NONE
        - escalation_reasons: List of traceable reasons
        - support_recommendation: Support-oriented language
        - audit_trail: Full symbolic audit trail
        - disclaimer: Mandatory non-diagnostic disclaimer
    """
    # Determine escalation level
    escalation_level = _determine_escalation_level(escalation_findings)
    
    # Build escalation reasons
    escalation_reasons = _build_escalation_reasons(escalation_findings, escalation_level)
    
    # Build audit trail
    audit_trail = _build_audit_trail(escalation_findings, ranking_result, escalation_level)
    
    # Get support recommendation
    support_recommendation = SUPPORT_RECOMMENDATIONS.get(
        escalation_level,
        SUPPORT_RECOMMENDATIONS[EscalationLevel.NONE]
    )
    
    return {
        "student_id": student_id,
        "escalation_level": escalation_level.value,
        "escalation_reasons": escalation_reasons,
        "support_recommendation": support_recommendation,
        "audit_trail": audit_trail,
        "disclaimer": DISCLAIMER
    }


def evaluate_batch(
    student_data: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Evaluate escalation for multiple students.
    
    Args:
        student_data: Dict mapping student_id to:
            - ranking_result: Output from ranker.py
            - escalation_findings: SPARQL query results
    
    Returns:
        Dict mapping student_id to escalation result
    """
    results = {}
    for student_id, data in student_data.items():
        results[student_id] = evaluate_escalation(
            student_id=student_id,
            ranking_result=data.get("ranking_result", {}),
            escalation_findings=data.get("escalation_findings", {})
        )
    return results


# =============================================================================
# SPARQL RESULT PARSER
# =============================================================================

def parse_sparql_escalation_results(
    sparql_results: Dict[str, Any]
) -> Dict[str, bool]:
    """
    Parse raw SPARQL query results into escalation findings.
    
    This transforms SPARQL SELECT results into boolean flags
    that can be consumed by evaluate_escalation().
    
    Args:
        sparql_results: Dict containing results from escalation_checks.sparql
            Expected keys: high_risk_results, panic_persistence_results, etc.
    
    Returns:
        Dict with boolean flags for each escalation condition
    """
    def has_results(key: str) -> bool:
        results = sparql_results.get(key, [])
        if isinstance(results, list):
            return len(results) > 0
        if isinstance(results, dict):
            bindings = results.get("bindings", results.get("results", []))
            return len(bindings) > 0
        return bool(results)
    
    return {
        "high_risk": has_results("high_risk_results") or has_results("high_risk"),
        "panic_with_persistence": has_results("panic_persistence_results") or has_results("panic_with_persistence"),
        "depressive_spectrum": has_results("depressive_spectrum_results") or has_results("depressive_spectrum"),
        "multiple_states": has_results("multiple_states_results") or has_results("multiple_states"),
        "moderate_risk": has_results("moderate_risk_results") or has_results("moderate_risk")
    }


# =============================================================================
# EXAMPLE OUTPUT
# =============================================================================

def generate_example_output() -> Dict[str, Any]:
    """
    Generate example demonstrating escalation evaluation.
    """
    # Synthetic ranking result
    ranking_result = {
        "ranked_states": [
            {"risk_state": "PanicRisk", "rank": 1, "safety_flag": "HIGH"},
            {"risk_state": "AnxietyRisk", "rank": 2, "safety_flag": "MODERATE"}
        ],
        "primary_concern": "PanicRisk",
        "aggregated_safety": "HIGH",
        "summary_rationale": "PanicRisk ranked highest due to HIGH safety flag"
    }
    
    # Synthetic escalation findings (from SPARQL)
    escalation_findings = {
        "high_risk": True,
        "panic_with_persistence": True,
        "depressive_spectrum": False,
        "multiple_states": True,
        "moderate_risk": True
    }
    
    result = evaluate_escalation(
        student_id="example_student_001",
        ranking_result=ranking_result,
        escalation_findings=escalation_findings
    )
    
    return {
        "description": "Example CRITICAL escalation with full audit trail",
        "result": result
    }
