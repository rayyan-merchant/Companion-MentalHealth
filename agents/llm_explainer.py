from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq not installed. LLM explanations disabled.")



RAG_SNIPPETS = {
    "AcademicStress": {
        "description": "Academic stress related to exams, coursework, or educational pressure.",
        "coping": [
            "Breaking tasks into smaller, manageable pieces can help reduce overwhelm.",
            "Taking short breaks during study sessions helps maintain focus.",
            "Reaching out to classmates or tutors for support is a sign of strength, not weakness."
        ],
        "empathy": "Academic pressure can feel relentless, especially during exam periods. What you're experiencing is valid."
    },
    "AnxietyRisk": {
        "description": "Signs of elevated anxiety including worry, restlessness, and sleep difficulties.",
        "coping": [
            "Grounding exercises like deep breathing or the 5-4-3-2-1 technique can help in the moment.",
            "Regular physical activity, even short walks, can help reduce anxiety over time.",
            "Limiting caffeine and ensuring consistent sleep patterns may help."
        ],
        "empathy": "Anxiety can make everything feel harder than it should. You're not alone in this."
    },
    "DepressiveSpectrum": {
        "description": "Patterns associated with low mood, withdrawal, and loss of interest.",
        "coping": [
            "Even small activities like a short walk or talking to someone can make a difference.",
            "Setting tiny, achievable goals for each day can help build momentum.",
            "Connecting with a counselor or support person is encouraged if feelings persist."
        ],
        "empathy": "Feeling empty or disconnected is hard to put into words. Your feelings are valid, and support is available."
    },
    "PanicRisk": {
        "description": "Signs of acute panic or high anxiety with physical symptoms.",
        "coping": [
            "Focus on your breathing: breathe in for 4 counts, hold for 4, breathe out for 6.",
            "Grounding yourself by naming 5 things you can see can help bring you back to the present.",
            "If symptoms are severe or persist, speaking with a healthcare provider is recommended."
        ],
        "empathy": "Panic symptoms can be frightening, but they do pass. You're going to be okay."
    },
    "NeedsMoreContext": {
        "description": "More information is needed to provide helpful guidance.",
        "coping": [],
        "empathy": "I want to make sure I understand what you're going through so I can be as helpful as possible."
    }
}


SYSTEM_PROMPT = """You are a supportive mental health assistant. Your role is ONLY to:
1. Rephrase the provided explanation in a warm, human tone
2. Offer the provided coping suggestions naturally
3. Ask clarifying questions when provided

You MUST NOT:
- Diagnose any mental health condition
- Infer new symptoms or states beyond what's provided
- Override or contradict the provided assessment
- Make medical recommendations
- Escalate risk levels

Always maintain a calm, supportive, non-judgmental tone.
Keep responses concise (under 100 words).
End responses with an open, supportive question when appropriate."""

REPHRASE_PROMPT = """Given the following assessment and evidence, create a warm, supportive response:

State Identified: {state}
Evidence Used: {evidence}
Coping Suggestions: {coping}
Empathy Note: {empathy}

Generate a response that:
1. Acknowledges what the person shared (1-2 sentences)
2. Gently reflects the identified pattern (1 sentence)
3. Offers 1-2 coping suggestions naturally
4. Ends with an open, supportive question

Keep the response under 100 words. Do NOT use clinical language."""

CLARIFICATION_PROMPT = """The user said: "{user_input}"

We need more information. Generate a warm, supportive response that:
1. Acknowledges what they shared
2. Asks ONE of these clarifying questions naturally: {questions}

Keep it under 50 words. Be gentle and non-invasive."""


@dataclass
class ExplanationResult:
    """Output from the LLM explainer."""
    response_text: str
    coping_suggestions: List[str]
    disclaimer: str
    used_llm: bool
    raw_state: Optional[str] = None


class LLMExplanationAgent:

    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        self.use_llm = False
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
        api_key = api_key or os.getenv("GROQ_API_KEY")
        
        if GROQ_AVAILABLE and api_key:
            try:
                self.client = Groq(api_key=api_key)
                self.use_llm = True
                print(f"LLM enabled with model: {self.model}")
            except Exception as e:
                print(f"Failed to initialize Groq client: {e}")
        
        self.rag_db = RAG_SNIPPETS
        self.disclaimer = (
            "This is an observational assessment, not a diagnosis. "
            "If you're experiencing ongoing distress, please consider speaking with "
            "a counselor or mental health professional."
        )
    
    def explain(
        self,
        primary_state: str,
        evidence: Dict[str, List[str]],
        confidence_decision: Dict[str, Any],
        user_input: str = ""
    ) -> ExplanationResult:

        action = confidence_decision.get("action", "explain")
        questions = confidence_decision.get("clarification_questions", [])
        
        # Get RAG snippet for the state
        rag_data = self.rag_db.get(primary_state, self.rag_db["NeedsMoreContext"])
        
        # Handle clarification case
        if action == "ask_clarification":
            response = self._generate_clarification(user_input, questions, rag_data)
            return ExplanationResult(
                response_text=response,
                coping_suggestions=[],
                disclaimer="",
                used_llm=self.use_llm,
                raw_state=primary_state
            )
        
        # Generate explanation
        if self.use_llm:
            response = self._generate_with_llm(primary_state, evidence, rag_data, action)
        else:
            response = self._generate_template(primary_state, evidence, rag_data, action)
        
        # Add disclaimer for cautious explanations
        disclaimer = self.disclaimer if action == "explain_cautious" else ""
        
        return ExplanationResult(
            response_text=response,
            coping_suggestions=rag_data.get("coping", [])[:2],
            disclaimer=disclaimer,
            used_llm=self.use_llm,
            raw_state=primary_state
        )
    
    def _generate_clarification(
        self,
        user_input: str,
        questions: List[str],
        rag_data: Dict
    ) -> str:
        empathy = rag_data.get("empathy", "I want to understand what you're going through.")
        
        if questions:
            question = questions[0]
        else:
            question = "Could you share a bit more about what's been on your mind?"
        
        if self.use_llm:
            try:
                prompt = CLARIFICATION_PROMPT.format(
                    user_input=user_input,
                    questions=questions
                )
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"LLM clarification failed: {e}")
        
        return f"{empathy}\n\n{question}"
    
    def _generate_template(
        self,
        state: str,
        evidence: Dict[str, List[str]],
        rag_data: Dict,
        action: str
    ) -> str:
        empathy = rag_data.get("empathy", "I hear you.")
        description = rag_data.get("description", "")
        coping = rag_data.get("coping", [])
        
        # Build evidence summary
        evidence_parts = []
        if evidence.get("emotions"):
            evidence_parts.append(f"feeling {', '.join(evidence['emotions'])}")
        if evidence.get("symptoms"):
            evidence_parts.append(f"experiencing {', '.join(evidence['symptoms'])}")
        if evidence.get("triggers"):
            evidence_parts.append(f"related to {', '.join(evidence['triggers'])}")
        
        evidence_summary = " and ".join(evidence_parts) if evidence_parts else "what you shared"
        
        # Build response
        response = f"Thank you for sharing. {empathy}\n\n"
        response += f"Based on {evidence_summary}, this sounds like it may relate to {description.lower()}\n\n"
        
        if coping:
            response += "Some things that might help:\n"
            for tip in coping[:2]:
                response += f"- {tip}\n"
        
        response += "\nHow does that resonate with you?"
        
        if action == "explain_cautious":
            response += f"\n\n{self.disclaimer}"
        
        return response
    
    def _generate_with_llm(
        self,
        state: str,
        evidence: Dict[str, List[str]],
        rag_data: Dict,
        action: str
    ) -> str:
        if not self.client:
            return self._generate_template(state, evidence, rag_data, action)
        
        try:
            prompt = REPHRASE_PROMPT.format(
                state=state,
                evidence=str(evidence),
                coping=rag_data.get("coping", []),
                empathy=rag_data.get("empathy", "")
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_template(state, evidence, rag_data, action)


_explainer_instance: Optional[LLMExplanationAgent] = None


def get_explainer(api_key: Optional[str] = None) -> LLMExplanationAgent:
    global _explainer_instance
    if _explainer_instance is None:
        _explainer_instance = LLMExplanationAgent(api_key)
    return _explainer_instance


def generate_explanation(
    primary_state: str,
    evidence: Dict[str, List[str]],
    confidence_decision: Dict[str, Any],
    user_input: str = "",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    explainer = get_explainer(api_key)
    result = explainer.explain(primary_state, evidence, confidence_decision, user_input)
    
    return {
        "response_text": result.response_text,
        "coping_suggestions": result.coping_suggestions,
        "disclaimer": result.disclaimer,
        "used_llm": result.used_llm,
        "raw_state": result.raw_state
    }



if __name__ == "__main__":
    print("LLM Explanation Agent Test (Groq)")
    print("=" * 60)
    
    test_cases = [
        (
            "AcademicStress",
            {"emotions": ["stress"], "symptoms": [], "triggers": ["academic"]},
            {"action": "explain", "clarification_questions": []},
            "Academic stress case"
        ),
        (
            "AnxietyRisk",
            {"emotions": ["anxiety"], "symptoms": ["insomnia"], "triggers": []},
            {"action": "explain_cautious", "clarification_questions": []},
            "Anxiety with caution"
        ),
        (
            "NeedsMoreContext",
            {"emotions": [], "symptoms": [], "triggers": []},
            {"action": "ask_clarification", "clarification_questions": ["What's been on your mind lately?"]},
            "Clarification needed"
        )
    ]
    
    for state, evidence, decision, description in test_cases:
        result = generate_explanation(state, evidence, decision, user_input="I'm stressed")
        print(f"\n{description}")
        print(f"Used LLM: {result['used_llm']}")
        print(f"Response:\n{result['response_text'][:300]}...")
