from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EscalationLevel(Enum):
    NONE = "NONE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


DISCLAIMER = "This system does not provide medical diagnosis or treatment."

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


def _determine_escalation_level(
    escalation_findings: Dict[str, bool]
) -> EscalationLevel:

    if escalation_findings.get("high_risk", False):
        return EscalationLevel.CRITICAL
    
    if escalation_findings.get("panic_with_persistence", False):
        return EscalationLevel.HIGH
    
    if escalation_findings.get("depressive_spectrum", False):
        return EscalationLevel.HIGH
    
    if escalation_findings.get("multiple_states", False):
        return EscalationLevel.MODERATE
    
    if escalation_findings.get("moderate_risk", False):
        return EscalationLevel.MODERATE
    
    return EscalationLevel.NONE


def _build_escalation_reasons(
    escalation_findings: Dict[str, bool],
    escalation_level: EscalationLevel
) -> List[str]:

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


# main esclatiom
def evaluate_escalation(
    student_id: str,
    ranking_result: Dict[str, Any],
    escalation_findings: Dict[str, bool]
) -> Dict[str, Any]:

    escalation_level = _determine_escalation_level(escalation_findings)
    
    escalation_reasons = _build_escalation_reasons(escalation_findings, escalation_level)
    
    audit_trail = _build_audit_trail(escalation_findings, ranking_result, escalation_level)
    
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

    results = {}
    for student_id, data in student_data.items():
        results[student_id] = evaluate_escalation(
            student_id=student_id,
            ranking_result=data.get("ranking_result", {}),
            escalation_findings=data.get("escalation_findings", {})
        )
    return results



def parse_sparql_escalation_results(
    sparql_results: Dict[str, Any]
) -> Dict[str, bool]:
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



def generate_example_output() -> Dict[str, Any]:
    ranking_result = {
        "ranked_states": [
            {"risk_state": "PanicRisk", "rank": 1, "safety_flag": "HIGH"},
            {"risk_state": "AnxietyRisk", "rank": 2, "safety_flag": "MODERATE"}
        ],
        "primary_concern": "PanicRisk",
        "aggregated_safety": "HIGH",
        "summary_rationale": "PanicRisk ranked highest due to HIGH safety flag"
    }
    
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
