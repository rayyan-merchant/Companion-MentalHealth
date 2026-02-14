from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class ConfidenceLabel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SafetyFlag(Enum):
    """Safety flag levels for ranking override."""
    NONE = "NONE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


SAFETY_PRIORITY = {
    "NONE": 0,
    "MODERATE": 1,
    "HIGH": 2
}


EVIDENCE_CATEGORIES = ["emotions", "symptoms", "triggers", "risk_factors"]



@dataclass
class RankingSignals:

    rule_count: int = 0
    evidence_diversity: int = 0  
    total_evidence: int = 0
    has_persistence: bool = False
    safety_flag: str = "NONE"
    confidence_label: str = "LOW"


@dataclass
class RankedRiskState:
    risk_state: str
    rank: int
    confidence_label: str
    safety_flag: str
    signals: RankingSignals
    rationale: List[str]  


@dataclass
class RankingResult:
    student_id: str
    ranked_states: List[RankedRiskState]
    primary_concern: Optional[str]  
    aggregated_safety: str  
    summary_rationale: str



def _extract_signals(explanation: Dict[str, Any]) -> RankingSignals:
    
    # Rule count
    rules_fired = explanation.get("rulesFired", [])
    rule_count = len(rules_fired)
    

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
    
    
    has_persistence = explanation.get("has_persistence", False)
    

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




STATE_PRIORITY = {
    "PanicRisk": 5,
    "DepressiveSpectrum": 4,
    "AnxietyRisk": 3,
    "AcademicStress": 2,
    "NeedsMoreContext": 0
}


def _compute_rank_score(signals: RankingSignals, risk_state: str) -> Tuple[int, int, int, int, int]:

    safety_priority = SAFETY_PRIORITY.get(signals.safety_flag, 0)
    
    state_priority = STATE_PRIORITY.get(risk_state, 1) # Default 1 for others
    
    if signals.rule_count >= 3:
        rule_score = 3
    elif signals.rule_count >= 2:
        rule_score = 2
    elif signals.rule_count >= 1:
        rule_score = 1
    else:
        rule_score = 0
    
    if signals.evidence_diversity >= 4:
        diversity_score = 4
    elif signals.evidence_diversity >= 3:
        diversity_score = 3
    elif signals.evidence_diversity >= 2:
        diversity_score = 2
    else:
        diversity_score = 1
    
    persistence_score = 1 if signals.has_persistence else 0
    
    return (safety_priority, state_priority, rule_score, diversity_score, persistence_score)


def _build_rationale(
    signals: RankingSignals,
    rank: int,
    total_states: int
) -> List[str]:

    rationale = []
    
    if signals.safety_flag == "HIGH":
        rationale.append("SAFETY OVERRIDE: HIGH safety flag places this at highest priority")
    elif signals.safety_flag == "MODERATE":
        rationale.append("Elevated priority due to MODERATE safety flag")
    
    if signals.rule_count >= 3:
        rationale.append(f"Strong rule support: {signals.rule_count} independent rules fired")
    elif signals.rule_count >= 2:
        rationale.append(f"Moderate rule support: {signals.rule_count} rules fired")
    elif signals.rule_count == 1:
        rationale.append("Limited rule support: single rule fired")
    else:
        rationale.append("No explicit rules tracked for this state")
    
    if signals.evidence_diversity >= 3:
        rationale.append(f"High evidence diversity: {signals.evidence_diversity} categories covered")
    elif signals.evidence_diversity >= 2:
        rationale.append(f"Moderate evidence diversity: {signals.evidence_diversity} categories")
    else:
        rationale.append("Low evidence diversity: limited category coverage")
    
    if signals.has_persistence:
        rationale.append("Persistence detected: repeated stress exposure present")
    else:
        rationale.append("No persistence signal: may be acute/situational")
    
    if rank == 1 and total_states > 1:
        rationale.append(f"Ranked highest of {total_states} states for this individual")
    elif rank == total_states and total_states > 1:
        rationale.append(f"Ranked lowest of {total_states} states")
    
    return rationale



def _aggregate_confidence(signals: RankingSignals) -> str:

    score = 0
    
    if signals.rule_count >= 3:
        score += 3
    elif signals.rule_count >= 2:
        score += 2
    elif signals.rule_count >= 1:
        score += 1
    
    if signals.evidence_diversity >= 4:
        score += 3
    elif signals.evidence_diversity >= 3:
        score += 2
    elif signals.evidence_diversity >= 2:
        score += 1
    
    if signals.has_persistence:
        score += 2
    
    if signals.total_evidence >= 5:
        score += 1
    
    if score >= 7:
        confidence = ConfidenceLabel.HIGH.value
    elif score >= 4:
        confidence = ConfidenceLabel.MEDIUM.value
    else:
        confidence = ConfidenceLabel.LOW.value
    
    
    if signals.safety_flag == "HIGH" and signals.rule_count == 1:
        if confidence == ConfidenceLabel.HIGH.value:
            confidence = ConfidenceLabel.MEDIUM.value
    
    return confidence


def rank_risk_states(
    student_id: str,
    explanations: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if not explanations:
        return {
            "student_id": student_id,
            "ranked_states": [],
            "primary_concern": None,
            "aggregated_safety": "NONE",
            "summary_rationale": "No risk states to rank"
        }
    
    states_with_signals = []
    for expl in explanations:
        risk_states_raw = expl.get("riskState", expl.get("mental_state", "Unknown"))
        if isinstance(risk_states_raw, str):
            risk_states = [risk_states_raw]
        else:
            risk_states = risk_states_raw

        signals = _extract_signals(expl)
        
        for r_state in risk_states:
            rank_tuple = _compute_rank_score(signals, r_state)
            states_with_signals.append({
                "risk_state": r_state,
                "signals": signals,
                "rank_tuple": rank_tuple,
                "original": expl
            })
    
    states_with_signals.sort(key=lambda x: x["rank_tuple"], reverse=True)
    
    ranked_states = []
    total_states = len(states_with_signals)
    
    for i, state_data in enumerate(states_with_signals):
        rank = i + 1 
        signals = state_data["signals"]
        
        aggregated_confidence = _aggregate_confidence(signals)
        
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
    
    primary_concern = ranked_states[0]["risk_state"] if ranked_states else None
    
    
    if any(s["safety_flag"] == "HIGH" for s in ranked_states):
        aggregated_safety = "HIGH"
    elif any(s["safety_flag"] == "MODERATE" for s in ranked_states):
        aggregated_safety = "MODERATE"
    else:
        aggregated_safety = "NONE"
    
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

    results = {}
    for student_id, explanations in student_explanations.items():
        results[student_id] = rank_risk_states(student_id, explanations)
    return results



def generate_example_output() -> Dict[str, Any]:

    
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
