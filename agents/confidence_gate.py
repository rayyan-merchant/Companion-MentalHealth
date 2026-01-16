
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ConfidenceDecision:
    action: str  # "explain", "explain_cautious", "ask_clarification"
    confidence_level: str  # high, medium, low
    should_ask_clarification: bool
    clarification_questions: List[str]
    reasoning: str


CLARIFICATION_TEMPLATES = {
    "no_evidence": [
        "I'd like to understand what's on your mind. Could you share a bit more about how you're feeling?",
        "What's been going on lately that brought you here?"
    ],
    "insufficient_evidence": [
        "I noticed you mentioned something that sounds difficult. Can you tell me more about how this has been affecting you?",
        "Has this been a recent change, or something you've experienced for a while?"
    ],
    "single_emotion": [
        "I hear that you're feeling {emotion}. Can you tell me what might be contributing to this feeling?",
        "Is there anything else going on alongside feeling {emotion}?"
    ],
    "vague_trigger": [
        "It sounds like {trigger} might be involved. How has this been impacting your daily life?",
        "When you think about {trigger}, what feelings come up for you?"
    ],
    "need_symptom_context": [
        "You mentioned {symptom}. Has this been happening often, or just recently?",
        "Is there anything else you've noticed about how you've been feeling physically?"
    ]
}


class ConfidenceGateAgent:
    
    def evaluate(
        self,
        reasoning_result: Dict[str, Any],
        extraction_result: Dict[str, Any],
        session_context: Optional[Dict[str, Any]] = None
    ) -> ConfidenceDecision:

        confidence = reasoning_result.get("confidence", "low")
        needs_clarification = reasoning_result.get("needs_clarification", False)
        clarification_reason = reasoning_result.get("clarification_reason")
        
        emotions = extraction_result.get("emotions", [])
        symptoms = extraction_result.get("symptoms", [])
        triggers = extraction_result.get("triggers", [])
        
        evidence_categories = sum([
            1 if emotions else 0,
            1 if symptoms else 0,
            1 if triggers else 0
        ])
        
        # HIGH confidence: 2+ categories AND a state was inferred
        if confidence == "high" and not needs_clarification:
            return ConfidenceDecision(
                action="explain",
                confidence_level="high",
                should_ask_clarification=False,
                clarification_questions=[],
                reasoning="Strong evidence across multiple categories"
            )
        
        # MEDIUM confidence: Some evidence but weak
        if confidence == "medium" or (evidence_categories >= 1 and not needs_clarification):
            return ConfidenceDecision(
                action="explain_cautious",
                confidence_level="medium",
                should_ask_clarification=True,
                clarification_questions=self._generate_followup(emotions, symptoms, triggers),
                reasoning="Some evidence present but additional context would help"
            )
        
        # LOW confidence: Must ask clarification
        questions = self._generate_clarification(
            clarification_reason, emotions, symptoms, triggers
        )
        
        return ConfidenceDecision(
            action="ask_clarification",
            confidence_level="low",
            should_ask_clarification=True,
            clarification_questions=questions,
            reasoning=clarification_reason or "Insufficient evidence for assessment"
        )
    
    def _generate_clarification(
        self,
        reason: Optional[str],
        emotions: List[Dict],
        symptoms: List[Dict],
        triggers: List[Dict]
    ) -> List[str]:
        questions = []
        
        if reason == "no_evidence":
            questions = CLARIFICATION_TEMPLATES["no_evidence"][:2]
        
        elif reason == "insufficient_evidence":
            if emotions and not symptoms and not triggers:
                emotion_label = emotions[0].get("label", "that way")
                template = CLARIFICATION_TEMPLATES["single_emotion"][0]
                questions.append(template.format(emotion=emotion_label))
            
            elif triggers and not emotions:
                trigger_label = triggers[0].get("label", "that situation")
                template = CLARIFICATION_TEMPLATES["vague_trigger"][0]
                questions.append(template.format(trigger=trigger_label))
            
            else:
                questions = CLARIFICATION_TEMPLATES["insufficient_evidence"][:2]
        
        else:
            questions = CLARIFICATION_TEMPLATES["insufficient_evidence"][:1]
        
        return questions
    
    def _generate_followup(
        self,
        emotions: List[Dict],
        symptoms: List[Dict],
        triggers: List[Dict]
    ) -> List[str]:
        questions = []
        
        # If we have emotions but no symptoms
        if emotions and not symptoms:
            questions.append("Has this been affecting your sleep, appetite, or energy levels?")
        
        # If we have triggers but no emotions
        if triggers and not emotions:
            questions.append("How has this been making you feel emotionally?")
        
        # If we have symptoms but no context
        if symptoms and not triggers:
            symptom_label = symptoms[0].get("label", "this")
            questions.append(f"Do you have a sense of what might be contributing to {symptom_label}?")
        
        return questions[:2]  # Max 2 questions



_gate_instance: Optional[ConfidenceGateAgent] = None


def get_confidence_gate() -> ConfidenceGateAgent:
    global _gate_instance
    if _gate_instance is None:
        _gate_instance = ConfidenceGateAgent()
    return _gate_instance


def evaluate_confidence(
    reasoning_result: Dict[str, Any],
    extraction_result: Dict[str, Any],
    session_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    gate = get_confidence_gate()
    decision = gate.evaluate(reasoning_result, extraction_result, session_context)
    
    return {
        "action": decision.action,
        "confidence_level": decision.confidence_level,
        "should_ask_clarification": decision.should_ask_clarification,
        "clarification_questions": decision.clarification_questions,
        "reasoning": decision.reasoning
    }
    
    return {
        "action": decision.action,
        "confidence_level": decision.confidence_level,
        "should_ask_clarification": decision.should_ask_clarification,
        "clarification_questions": decision.clarification_questions,
        "reasoning": decision.reasoning
    }


if __name__ == "__main__":
    print("Confidence Gate Agent Test")
    print("=" * 60)
    
    test_cases = [
        # HIGH confidence
        (
            {"confidence": "high", "needs_clarification": False},
            {"emotions": [{"label": "anxiety"}], "symptoms": [{"label": "insomnia"}], "triggers": []},
            "High confidence case"
        ),
        # MEDIUM confidence
        (
            {"confidence": "medium", "needs_clarification": False},
            {"emotions": [{"label": "stress"}], "symptoms": [], "triggers": []},
            "Medium confidence case"
        ),
        # LOW confidence
        (
            {"confidence": "low", "needs_clarification": True, "clarification_reason": "insufficient_evidence"},
            {"emotions": [{"label": "anxiety"}], "symptoms": [], "triggers": []},
            "Low confidence case"
        ),
        # No evidence
        (
            {"confidence": "low", "needs_clarification": True, "clarification_reason": "no_evidence"},
            {"emotions": [], "symptoms": [], "triggers": []},
            "No evidence case"
        )
    ]
    
    for reasoning, extraction, description in test_cases:
        result = evaluate_confidence(reasoning, extraction)
        print(f"\n{description}")
        print(f"  Action: {result['action']}")
        print(f"  Confidence: {result['confidence_level']}")
        print(f"  Questions: {result['clarification_questions']}")
