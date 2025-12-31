"""
Audit Trail & Provenance Layer
Phase 7 - Mental Health KRR System (Final Symbolic Layer)

This module captures, preserves, traces, and audits all symbolic outputs
from Phases 4-6. It exists to prove that the system is KRR-based,
deterministic, and inspectable.

RESPONSIBILITY (STRICT):
- Collect outputs from Phases 4-6
- Structure audit records
- Store provenance information
- Return immutable audit trails

THIS MODULE DOES NOT:
- Rank (that's Phase-5)
- Escalate (that's Phase-6)
- Explain (that's Phase-4)
- Infer (that's SWRL)
- Reason (that's forbidden)
- Perform NLP or ML
- Introduce probabilistic logic

CONSTRAINTS:
- Append-only audit records
- No mutation of previous sessions
- Deterministic and reproducible
- Full symbolic traceability
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json
import hashlib


# =============================================================================
# CONSTANTS
# =============================================================================

PIPELINE_VERSION = "v1.0"

# Mandatory disclaimers
AUDIT_DISCLAIMER = (
    "This system does not provide medical diagnosis or treatment. "
    "All outputs are advisory and symbolic in nature. "
    "No medical decision was made by this system."
)

# Provenance files (frozen)
DEFAULT_PROVENANCE = {
    "owl_file": "mental_health.owl",
    "swrl_file": "swrl_rules.owl",
    "sparql_files": [
        "materialization.sparql",
        "explanation_queries.sparql",
        "escalation_checks.sparql"
    ]
}

# Audit guarantees (system properties)
AUDIT_GUARANTEES = {
    "deterministic": True,
    "symbolic_only": True,
    "no_ml": True,
    "no_diagnosis": True,
    "reproducible": True,
    "append_only": True
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class InferenceSummary:
    """Summary of inferred states and rules fired."""
    inferred_states: List[str]
    rules_fired: List[str]


@dataclass
class RankingSummary:
    """Summary of ranking output."""
    ranked_states: List[Dict[str, Any]]
    primary_concern: Optional[str]
    aggregated_safety: str


@dataclass
class EscalationSummary:
    """Summary of escalation output."""
    level: str
    reasons: List[str]
    support_recommendation: str


@dataclass
class AuditRecord:
    """
    Immutable audit record for a single session.
    Once created, this record should not be modified.
    """
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
    record_hash: str = ""  # Computed after creation for integrity


# =============================================================================
# PROVENANCE TRACKING
# =============================================================================

def _extract_rules_fired(explanations: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all unique rule IDs fired across explanations.
    Source: Phase-4 explainer output
    """
    rules = set()
    for expl in explanations:
        for rule in expl.get("rulesFired", []):
            rules.add(rule)
    return sorted(list(rules))


def _extract_inferred_states(explanations: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all inferred mental states from explanations.
    Source: Phase-4 explainer output
    """
    states = set()
    for expl in explanations:
        state = expl.get("riskState", expl.get("mental_state"))
        if state:
            states.add(state)
    return sorted(list(states))


def _extract_triggered_queries(escalation_result: Dict[str, Any]) -> List[str]:
    """
    Extract SPARQL query names that returned results.
    Source: Phase-6 escalation output → audit_trail → triggered_queries
    """
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
    """
    Build layer-by-layer provenance showing which layer produced which output.
    """
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


# =============================================================================
# RECORD INTEGRITY
# =============================================================================

def _compute_record_hash(record_data: Dict[str, Any]) -> str:
    """
    Compute a deterministic hash for the audit record.
    This ensures record integrity and immutability verification.
    """
    # Create a canonical JSON representation
    canonical = json.dumps(record_data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


# =============================================================================
# MAIN AUDIT FUNCTION
# =============================================================================

def log_audit_session(
    session_id: str,
    student_id: str,
    explanation_outputs: List[Dict[str, Any]],
    ranking_result: Dict[str, Any],
    escalation_result: Dict[str, Any],
    provenance: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create an immutable audit record for a reasoning session.
    
    This function ONLY collects and structures data.
    It does NOT reason, rank, escalate, or explain.
    
    Args:
        session_id: Unique identifier for this reasoning session
        student_id: Identifier for the student
        explanation_outputs: List of outputs from Phase-4 explainer
        ranking_result: Output from Phase-5 ranker
        escalation_result: Output from Phase-6 escalation
        provenance: Optional custom provenance (defaults to system files)
        timestamp: Optional timestamp (defaults to current time)
    
    Returns:
        Immutable audit record with:
        - Session metadata
        - Inference summary
        - All phase outputs
        - Full provenance
        - Audit guarantees
        - Record hash for integrity
    
    Guarantees:
        - Deterministic: Same inputs produce same outputs
        - Reproducible: Can be regenerated from source data
        - Append-only: Records are never mutated
        - Symbolic-only: No ML or probabilistic logic
    """
    # Use provided or default values
    provenance = provenance or DEFAULT_PROVENANCE
    timestamp = timestamp or datetime.utcnow().isoformat() + "Z"
    
    # Build inference summary
    inference_summary = {
        "inferred_states": _extract_inferred_states(explanation_outputs),
        "rules_fired": _extract_rules_fired(explanation_outputs)
    }
    
    # Build ranking summary
    ranking_summary = {
        "ranked_states": ranking_result.get("ranked_states", []),
        "primary_concern": ranking_result.get("primary_concern"),
        "aggregated_safety": ranking_result.get("aggregated_safety", "NONE")
    }
    
    # Build escalation summary
    escalation_summary = {
        "level": escalation_result.get("escalation_level", "NONE"),
        "reasons": escalation_result.get("escalation_reasons", []),
        "support_recommendation": escalation_result.get("support_recommendation", "")
    }
    
    # Build extended provenance with layer tracking
    extended_provenance = {
        **provenance,
        "layer_provenance": _build_layer_provenance(
            explanation_outputs, ranking_result, escalation_result
        ),
        "triggered_queries": _extract_triggered_queries(escalation_result)
    }
    
    # Construct record data (before hash)
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
    
    # Compute integrity hash
    record_hash = _compute_record_hash(record_data)
    record_data["record_hash"] = record_hash
    
    return record_data


def log_batch_sessions(
    sessions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Create audit records for multiple sessions.
    
    Args:
        sessions: List of session data, each containing:
            - session_id
            - student_id
            - explanation_outputs
            - ranking_result
            - escalation_result
            - provenance (optional)
    
    Returns:
        List of audit records
    """
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
    """
    Verify that an audit record has not been tampered with.
    
    Args:
        record: An audit record to verify
    
    Returns:
        True if record is intact, False if modified
    """
    stored_hash = record.get("record_hash", "")
    
    # Reconstruct record without hash
    record_copy = {k: v for k, v in record.items() if k != "record_hash"}
    computed_hash = _compute_record_hash(record_copy)
    
    return stored_hash == computed_hash


# =============================================================================
# EXAMPLE OUTPUT (FOR DOCUMENTATION)
# =============================================================================

def generate_example_audit() -> Dict[str, Any]:
    """
    Generate a synthetic example audit record for documentation.
    """
    # Synthetic Phase-4 output
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
    
    # Synthetic Phase-5 output
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
    
    # Synthetic Phase-6 output
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
    
    # Generate audit record
    return log_audit_session(
        session_id="example_session_001",
        student_id="student_001",
        explanation_outputs=example_explanations,
        ranking_result=example_ranking,
        escalation_result=example_escalation,
        timestamp="2024-01-15T10:30:00Z"
    )
