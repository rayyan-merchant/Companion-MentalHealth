from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json
import hashlib


PIPELINE_VERSION = "v1.0"

AUDIT_DISCLAIMER = (
    "This system does not provide medical diagnosis or treatment. "
    "All outputs are advisory and symbolic in nature. "
    "No medical decision was made by this system."
)

DEFAULT_PROVENANCE = {
    "owl_file": "mental_health.owl",
    "swrl_file": "swrl_rules.owl",
    "sparql_files": [
        "materialization.sparql",
        "explanation_queries.sparql",
        "escalation_checks.sparql"
    ]
}

AUDIT_GUARANTEES = {
    "deterministic": True,
    "symbolic_only": True,
    "no_ml": True,
    "no_diagnosis": True,
    "reproducible": True,
    "append_only": True
}



# DATA STRUCTURES
@dataclass
class InferenceSummary:
    inferred_states: List[str]
    rules_fired: List[str]


@dataclass
class RankingSummary:
    ranked_states: List[Dict[str, Any]]
    primary_concern: Optional[str]
    aggregated_safety: str


@dataclass
class EscalationSummary:
    level: str
    reasons: List[str]
    support_recommendation: str


@dataclass
class AuditRecord:
    session_id: str
    student_id: str
    timestamp: str
    pipeline_version: str
    inference_summary: Dict[str, Any]
    explanations: List[Dict[str, Any]]
    ranking: Dict[str, Any]
    escalation: Dict[str, Any]
    provenance: Dict[str, Any]
    audit_guarantees: Dict[str, bool]
    disclaimer: str
    record_hash: str = ""  


def _extract_rules_fired(explanations: List[Dict[str, Any]]) -> List[str]:
    rules = set()
    for expl in explanations:
        for rule in expl.get("rulesFired", []):
            rules.add(rule)
    return sorted(list(rules))


def _extract_inferred_states(explanations: List[Dict[str, Any]]) -> List[str]:

    states = set()
    for expl in explanations:
        state = expl.get("riskState", expl.get("mental_state"))
        if state:
            if isinstance(state, list):
                states.update(state)
            else:
                states.add(state)
    return sorted(list(states))


def _extract_triggered_queries(escalation_result: Dict[str, Any]) -> List[str]:
    queries = []
    audit_trail = escalation_result.get("audit_trail", {})
    triggered = audit_trail.get("triggered_queries", [])
    
    for query_info in triggered:
        if isinstance(query_info, dict):
            finding = query_info.get("finding", "")
            if finding:
                queries.append(f"escalation_checks.sparql:{finding}")
        elif isinstance(query_info, str):
            queries.append(query_info)
    
    return queries


def _build_layer_provenance(
    explanations: List[Dict[str, Any]],
    ranking_result: Dict[str, Any],
    escalation_result: Dict[str, Any]
) -> Dict[str, Any]:

    return {
        "phase_4_explainer": {
            "output_count": len(explanations),
            "states_explained": _extract_inferred_states(explanations),
            "rules_referenced": _extract_rules_fired(explanations)
        },
        "phase_5_ranker": {
            "states_ranked": len(ranking_result.get("ranked_states", [])),
            "primary_concern": ranking_result.get("primary_concern"),
            "aggregated_safety": ranking_result.get("aggregated_safety", "NONE")
        },
        "phase_6_escalation": {
            "escalation_level": escalation_result.get("escalation_level", "NONE"),
            "triggered_queries": _extract_triggered_queries(escalation_result),
            "safety_override": escalation_result.get("audit_trail", {}).get("safety_override", False)
        }
    }



# RECORD INTEGRITY
def _compute_record_hash(record_data: Dict[str, Any]) -> str:
    canonical = json.dumps(record_data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]




def log_audit_session(
    session_id: str,
    student_id: str,
    explanation_outputs: List[Dict[str, Any]],
    ranking_result: Dict[str, Any],
    escalation_result: Dict[str, Any],
    provenance: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:

    provenance = provenance or DEFAULT_PROVENANCE
    timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
    
    inference_summary = {
        "inferred_states": _extract_inferred_states(explanation_outputs),
        "rules_fired": _extract_rules_fired(explanation_outputs)
    }
    
    ranking_summary = {
        "ranked_states": ranking_result.get("ranked_states", []),
        "primary_concern": ranking_result.get("primary_concern"),
        "aggregated_safety": ranking_result.get("aggregated_safety", "NONE")
    }
    
    escalation_summary = {
        "level": escalation_result.get("escalation_level", "NONE"),
        "reasons": escalation_result.get("escalation_reasons", []),
        "support_recommendation": escalation_result.get("support_recommendation", "")
    }
    
    extended_provenance = {
        **provenance,
        "layer_provenance": _build_layer_provenance(
            explanation_outputs, ranking_result, escalation_result
        ),
        "triggered_queries": _extract_triggered_queries(escalation_result)
    }
    
    record_data = {
        "session_id": session_id,
        "student_id": student_id,
        "timestamp": timestamp,
        "pipeline_version": PIPELINE_VERSION,
        "inference_summary": inference_summary,
        "explanations": explanation_outputs,
        "ranking": ranking_summary,
        "escalation": escalation_summary,
        "provenance": extended_provenance,
        "audit_guarantees": AUDIT_GUARANTEES,
        "disclaimer": AUDIT_DISCLAIMER
    }
    
    record_hash = _compute_record_hash(record_data)
    record_data["record_hash"] = record_hash
    
    return record_data


def log_batch_sessions(
    sessions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    records = []
    for session in sessions:
        record = log_audit_session(
            session_id=session.get("session_id", "unknown"),
            student_id=session.get("student_id", "unknown"),
            explanation_outputs=session.get("explanation_outputs", []),
            ranking_result=session.get("ranking_result", {}),
            escalation_result=session.get("escalation_result", {}),
            provenance=session.get("provenance")
        )
        records.append(record)
    return records


def verify_record_integrity(record: Dict[str, Any]) -> bool:
    stored_hash = record.get("record_hash", "")
    
    record_copy = {k: v for k, v in record.items() if k != "record_hash"}
    computed_hash = _compute_record_hash(record_copy)
    
    return stored_hash == computed_hash



def generate_example_audit() -> Dict[str, Any]:
    example_explanations = [
        {
            "student_id": "student_001",
            "riskState": "AnxietyRisk",
            "has_persistence": True,
            "confidence_label": "MEDIUM",
            "rulesFired": ["R_ANX_01", "R_ANX_02"],
            "evidence": [
                {"type": "Emotion", "value": "Stress"},
                {"type": "Symptom", "value": "Insomnia"}
            ],
            "causalChain": [
                "Emotional state observed: Stress",
                "Symptoms manifested: Insomnia",
                "Mental state inferred: Anxiety Risk"
            ],
            "uncertainty_drivers": [],
            "explanation_text": "...",
            "safety_flag": "MODERATE"
        }
    ]
    
    example_ranking = {
        "student_id": "student_001",
        "ranked_states": [
            {
                "risk_state": "AnxietyRisk",
                "rank": 1,
                "confidence_label": "MEDIUM",
                "safety_flag": "MODERATE"
            }
        ],
        "primary_concern": "AnxietyRisk",
        "aggregated_safety": "MODERATE",
        "summary_rationale": "Single risk state identified"
    }
    
    example_escalation = {
        "student_id": "student_001",
        "escalation_level": "MODERATE",
        "escalation_reasons": ["ModerateRisk classification"],
        "support_recommendation": "Self-care and support resources recommended.",
        "audit_trail": {
            "triggered_queries": [
                {"finding": "moderate_risk", "result": True}
            ],
            "safety_override": False
        },
        "disclaimer": AUDIT_DISCLAIMER
    }
    
    return log_audit_session(
        session_id="example_session_001",
        student_id="student_001",
        explanation_outputs=example_explanations,
        ranking_result=example_ranking,
        escalation_result=example_escalation,
        timestamp="2024-01-15T10:30:00Z"
    )
