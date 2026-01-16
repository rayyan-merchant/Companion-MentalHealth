from typing import Dict, Any, Optional, List
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


CRISIS_KEYWORDS = [
    # Active
    "suicide", "kill myself", "want to die", "end my life", "better off dead",
    "hurt myself", "self-harm", "cutting myself", "overdose", "slit my wrists",
    "hang myself", "jump off", "shoot myself",
    # Passive / Edge Cases
    "sleep forever", "never wake up", "everyone would be happier",
    "burden to everyone", "no reason to live", "end it all", "wish i was dead"
]


def check_crisis(text: str, extraction_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check for crisis keywords and return immediate intervention if found."""
    text_lower = text.lower()
    negated_terms = extraction_result.get("negated_terms", [])
    
    # Check for keywords
    triggered_keyword = None
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            triggered_keyword = keyword
            break
            
    if triggered_keyword:
        # Check if the DETECTED keyword (or its key part) was negated
        # Simple check: if any word in the keyword phrases triggers negation
        # e.g. "kill" in "kill myself" might be negated
        
        # Robust check: if the keyword is literally in the negation list
        # or if the keyword contains a word that is in the negation list
        is_negated = False
        for term in negated_terms:
            if term in triggered_keyword:
                is_negated = True
                break
        
        if is_negated:
            return None  # False alarm (Negated)

        # Return Crisis Result
        return {
            "response_text": "I hear how much pain you're in right now. Please, you don't have to go through this alone. There are people who want to listen and help you stay safe.",
            "primary_state": "Crisis (Suicidal Ideation)",
            "confidence": "high",
            "action_taken": "crisis_intervention",
            "evidence_summary": {
                "symptoms": ["Suicidal Ideation"], 
                "emotions": ["Despair"], 
                "triggers": ["Crisis"],
                "keyword": triggered_keyword
            },
            "clarification_questions": [],
            "disclaimer": "URGENT: Immediate professional support is recommended."
        }
    return None


def run_hybrid_pipeline(
    session_id: str,
    user_input: str,
    previous_messages: Optional[List[Dict[str, Any]]] = None,
    openai_api_key: Optional[str] = None
) -> Dict[str, Any]:

    debug_info = {}
    
    # 0. Hydrate Session Memory if history is provided
    session = get_session(session_id)
    if previous_messages:
        session.hydrate(previous_messages)
        debug_info["hydrated"] = True
    
    # 1. Extraction first (to get negation context)
    extraction_result = extract_signals(user_input)
    debug_info["extraction"] = extraction_result

    # 2. Crisis Interceptor (now aware of negation)
    crisis_result = check_crisis(user_input, extraction_result)
    if crisis_result:
        result = PipelineResult(
            session_id=session_id,
            response_text=crisis_result["response_text"],
            primary_state=crisis_result["primary_state"],
            confidence=crisis_result["confidence"],
            action_taken=crisis_result["action_taken"],
            evidence_summary=crisis_result["evidence_summary"],
            clarification_questions=crisis_result["clarification_questions"],
            disclaimer=crisis_result["disclaimer"],
            debug={"crisis_detected": True, "keyword": crisis_result["evidence_summary"]["keyword"]}
        )
        return asdict(result)
    

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
    
    # 4. Context Fallback / Context Fusion
    # If the result is "NeedsMoreContext" or confidence is low, 
    # automatically try merging with session context to see if a pattern emerges.
    
    current_state = reasoning_result.get("primary_state")
    current_confidence = reasoning_result.get("confidence")
    
    if (not current_state or current_state == "NeedsMoreContext" or current_confidence == "low"):
        # Retrieve ACCUMULATED context from the entire session
        full_context = session.get_context()
        
        if full_context.turn_count > 0:
            accumulated_emotions = full_context.accumulated_emotions
            accumulated_symptoms = full_context.accumulated_symptoms
            accumulated_triggers = full_context.accumulated_triggers
            
            # Re-run reasoning with full historical context
            global_reasoning = reason_from_signals(
                emotions=accumulated_emotions,
                symptoms=accumulated_symptoms,
                triggers=accumulated_triggers,
                session_id=session_id,
                persistence=full_context.persistence_detected
            )
            
            new_state = global_reasoning.get("primary_state")
            
            # If fusion gave us a BETTER result (not NeedsMoreContext), upgrade to it.
            if new_state and new_state != "NeedsMoreContext":
                
                # We found a valid pattern from history!
                
                # Force action to explain if we found something useful
                fallback_decision = {"action": "explain", "clarification_questions": []}
                
                explanation_result = generate_explanation(
                    primary_state=new_state,
                    evidence=global_reasoning.get("evidence_used", {}),
                    confidence_decision=fallback_decision,
                    user_input=user_input,
                    api_key=openai_api_key
                )
                
                # Update debug info
                debug_info["context_fallback"] = f"Auto-fused session history -> {new_state}"
                
                # Update parameters for final result
                reasoning_result = global_reasoning 
                confidence_decision["action"] = "explain"
                emotions = accumulated_emotions
                symptoms = accumulated_symptoms
                triggers = accumulated_triggers

    # Help Request Logic (redundant now? No, explicitly handles 'suggest' intent overrides)
    help_keywords = ["suggest", "advice", "help", "what do i do", "recommend", "tips", "strategy"]
    is_help_request = any(k in user_input.lower() for k in help_keywords)
    
    if is_help_request and reasoning_result.get("primary_state") == "NeedsMoreContext":
         # Logic largely covered by above, but keeping specific 'Suggest' override intent check?
         # Actually the above covers it better. If fusion works, we already upgraded.
         pass

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


def process_message(
    session_id: str, 
    message: str, 
    previous_messages: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    
    result = run_hybrid_pipeline(
        session_id=session_id, 
        user_input=message, 
        previous_messages=previous_messages
    )
    
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
