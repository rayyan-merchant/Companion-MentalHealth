from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import uuid

from agents.ml_extractor import extract_signals
from agents.session_memory import get_session, SessionMemoryAgent
from agents.symbolic_reasoner import reason_from_signals
from agents.confidence_gate import evaluate_confidence
from agents.llm_explainer import generate_explanation


@dataclass
class PipelineResult:
    session_id: str
    response_text: str
    primary_state: Optional[str]
    confidence: str
    action_taken: str
    evidence_summary: Dict[str, Any]
    clarification_questions: list
    disclaimer: str
    debug: Dict[str, Any]


def run_hybrid_pipeline(
    session_id: str,
    user_input: str,
    openai_api_key: Optional[str] = None
) -> Dict[str, Any]:

    debug_info = {}
    

    extraction_result = extract_signals(user_input)
    debug_info["extraction"] = extraction_result
    

    session = get_session(session_id)
    
    session_context = session.get_context()
    persistence = session_context.persistence_detected
    
    similar_past = session.retrieve_similar(user_input, n_results=2)
    
    emotions = [e["label"] for e in extraction_result.get("emotions", [])]
    symptoms = [s["label"] for s in extraction_result.get("symptoms", [])]
    triggers = [t["label"] for t in extraction_result.get("triggers", [])]
    
    reasoning_result = reason_from_signals(
        emotions=emotions,
        symptoms=symptoms,
        triggers=triggers,
        session_id=session_id,
        persistence=persistence
    )
    debug_info["reasoning"] = reasoning_result
    
    confidence_decision = evaluate_confidence(
        reasoning_result=reasoning_result,
        extraction_result=extraction_result,
        session_context=session.get_memory_summary()
    )
    debug_info["confidence"] = confidence_decision
    
    explanation_result = generate_explanation(
        primary_state=reasoning_result.get("primary_state", "NeedsMoreContext"),
        evidence=reasoning_result.get("evidence_used", {}),
        confidence_decision=confidence_decision,
        user_input=user_input,
        api_key=openai_api_key
    )
    debug_info["explanation"] = explanation_result
    
    session.add_turn(
        raw_text=user_input,
        extraction_result=extraction_result,
        inferred_states=reasoning_result.get("inferred_states", []),
        confidence=reasoning_result.get("confidence", "low")
    )
    
    result = PipelineResult(
        session_id=session_id,
        response_text=explanation_result.get("response_text", ""),
        primary_state=reasoning_result.get("primary_state"),
        confidence=reasoning_result.get("confidence", "low"),
        action_taken=confidence_decision.get("action", "ask_clarification"),
        evidence_summary={
            "emotions": emotions,
            "symptoms": symptoms,
            "triggers": triggers,
            "intensity": extraction_result.get("intensity", "medium"),
            "temporal": extraction_result.get("temporal")
        },
        clarification_questions=confidence_decision.get("clarification_questions", []),
        disclaimer=explanation_result.get("disclaimer", ""),
        debug=debug_info
    )
    
    return asdict(result)


def process_message(session_id: str, message: str) -> Dict[str, Any]:
    result = run_hybrid_pipeline(session_id, message)
    
    # Format for frontend
    return {
        "session_id": result["session_id"],
        "response": result["response_text"],
        "state": result["primary_state"],
        "confidence": result["confidence"],
        "action": result["action_taken"],
        "evidence": result["evidence_summary"],
        "follow_up_questions": result["clarification_questions"],
        "disclaimer": result["disclaimer"]
    }


if __name__ == "__main__":
    print("Hybrid Pipeline Test")
    print("=" * 70)
    
    test_session = f"test_{uuid.uuid4().hex[:8]}"
    
    test_inputs = [
        "Anxious today",
        "Finals are killing me",
        "I can't sleep and feel restless",
        "I feel empty and avoid everyone",
        "Heart racing, can't breathe"
    ]
    
    expected = [
        "Ask clarification",
        "Academic Stress",
        "Anxiety Risk",
        "Depressive Spectrum",
        "Panic Risk"
    ]
    
    print(f"{'Input':<40} | {'Expected':<20} | {'Actual':<20} | {'Action':<20}")
    print("-" * 105)
    
    for text, exp in zip(test_inputs, expected):
        result = process_message(test_session, text)
        state = result.get("state", "None")
        action = result.get("action", "unknown")
        
        print(f"{text:<40} | {exp:<20} | {state:<20} | {action:<20}")
    
    print("\n" + "=" * 70)
    print("Pipeline test complete.")
