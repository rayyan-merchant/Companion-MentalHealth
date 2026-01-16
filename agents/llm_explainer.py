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
        "strategies": {
            "default": [
                "Breaking tasks into smaller, manageable pieces can help reduce overwhelm.",
                "Reviewing your schedule to find small pockets of rest."
            ],
            "academic": [
                "Try the **Pomodoro Technique**: 25 minutes of focused work followed by a 5-minute break.",
                "Use **'Chunking'**: Break large assignments into tiny, actionable steps (e.g., 'Open laptop' -> 'Read title').",
                "Practice **Active Recall**: Test yourself instead of just re-reading notes."
            ],
            "social": [
                "Study groups can help, but ensure they are productive and supportive.",
                "Set boundaries on when you are available to help others."
            ]
        },
        "empathy": "Academic pressure can feel relentless. It makes sense that you're feeling this way."
    },
    "AnxietyRisk": {
        "description": "Signs of elevated anxiety including worry, restlessness, and sleep difficulties.",
        "strategies": {
            "default": [
                "Practice **4-7-8 Breathing**: Inhale for 4, hold for 7, exhale for 8.",
                "Try **Progressive Muscle Relaxation**: Tense and release muscle groups from toes to head."
            ],
            "financial": [
                "Set a specific **'Worry Time'** (e.g., 20 mins at 4 PM) to process concerns, then distract yourself.",
                "Focus on one small, actionable financial step you can take today."
            ],
            "health": [
                "Limit Googling symptoms; set a timer if you must check.",
                "Practice grounding: Name 5 things you can see and 4 things you can feel."
            ]
        },
        "empathy": "Anxiety can be exhausting. You're doing the best you can."
    },
    "DepressiveSpectrum": {
        "description": "Patterns associated with low mood, withdrawal, and loss of interest.",
        "strategies": {
            "default": [
                "**Behavioral Activation**: Do one small thing you used to enjoy, even if you don't feel like it.",
                "Get 10 minutes of **morning sunlight** to help regulate your mood."
            ],
            "social": [
                "Send a low-pressure text (e.g., a meme) to one friend.",
                "You don't have to 'perform' happiness; just being around others can help."
            ],
            "work": [
                "Set the bar lower for 'good enough' today.",
                "Focus on completing just one high-priority task."
            ]
        },
        "empathy": "It takes a lot of strength just to keep going when you feel this way."
    },
    "PanicRisk": {
        "description": "Signs of acute panic or high anxiety with physical symptoms.",
        "strategies": {
            "default": [
                "**5-4-3-2-1 Grounding**: 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.",
                "Splash cold water on your face to activate the 'Mammalian Dive Reflex' and slow your heart."
            ],
            "social": [
                "If in a crowd, find a quiet corner or restroom to center yourself for 5 minutes.",
                "Focus on a single object in the room and describe it in detail."
            ]
        },
        "empathy": "Panic attacks are terrifying, but they are temporary. You are safe."
    },
    "SleepDisturbance": {
        "description": "Difficulties falling or staying asleep.",
        "strategies": {
            "default": [
                "**Brain Dump**: Write down all your worries 1 hour before bed so your brain doesn't have to hold them.",
                "Keep your room cool and dark to signal your body it's time to rest."
            ],
            "academic": [
                "No studying in bed. Keep the bed strictly for sleep.",
                "Set a firm 'shutdown time' for schoolwork at least 1 hour before sleep."
            ]
        },
        "empathy": "Not sleeping well makes everything else feel harder."
    },
    "SocialIsolation": {
        "description": "Pulling away from others or feeling disconnected.",
        "strategies": {
            "default": [
                "Text one person just to say 'thinking of you'.",
                "Go to a public place (like a cafe) just to be around people without pressure to interact."
            ],
            "social": [
                "It's okay to say 'I'm not up for a big hangout, but can we grab coffee for 20 mins?'",
                "Focus on quality over quantity of interactions."
            ]
        },
        "empathy": "Loneliness is painful. Reaching out feels heavy, but small steps count."
    },
    "NeedsMoreContext": {
        "description": "More information is needed.",
        "strategies": {
            "default": []
        },
        "empathy": "I'm listening. Take your time."
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
Available Coping Strategies (Grouped by Category):
{coping}
Empathy Note: {empathy}

Generate a response that:
1. Acknowledges what the person shared (1-2 sentences)
2. Gently reflects the identified pattern (1 sentence)
3. Selects 1-2 MOST RELEVANT coping suggestions based on the evidence (e.g., if evidence mentions exams, pick ACADEMIC strategies).
4. Do NOT list all strategies. Pick the best ones.
5. Ends with an open, supportive question

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
        self.api_keys = []
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.use_llm = False
        
        # Load keys from arg or env
        if api_key:
            self.api_keys = [k.strip() for k in api_key.split(",") if k.strip()]
        else:
            env_keys = os.getenv("GROQ_API_KEY", "")
            self.api_keys = [k.strip() for k in env_keys.split(",") if k.strip()]
            
        if GROQ_AVAILABLE and self.api_keys:
            self.use_llm = True
            print(f"LLM enabled with {len(self.api_keys)} keys. Model: {self.model}")
        elif not GROQ_AVAILABLE:
            print("Warning: groq not installed. LLM explanations disabled.")
        else:
            print("Warning: No API keys found. LLM explanations disabled.")
        
        self.rag_db = RAG_SNIPPETS
        self.disclaimer = (
            "This is an observational assessment, not a diagnosis. "
            "If you're experiencing ongoing distress, please consider speaking with "
            "a counselor or mental health professional."
        )

    def _get_client(self):
        """Get a Groq client with a random key from the pool."""
        import random
        if not self.api_keys:
            return None
        
        # Simple random selection for load balancing
        selected_key = random.choice(self.api_keys)
        try:
            return Groq(api_key=selected_key)
        except Exception as e:
            print(f"Failed to create client with key ...{selected_key[-4:]}: {e}")
            return None

    def explain(
        self,
        primary_state: str,
        evidence: Dict[str, List[str]],
        confidence_decision: Dict[str, Any],
        user_input: str = ""
    ) -> ExplanationResult:

        action = confidence_decision.get("action", "explain")
        questions = confidence_decision.get("clarification_questions", [])
        
        # Get RAG snippet for the primary state
        primary_rag = self.rag_db.get(primary_state, self.rag_db["NeedsMoreContext"])
        
        # Cross-Pollination: Gather strategies from other states based on evidence
        aggregated_strategies = primary_rag.get("strategies", {}).copy()
        
        symptoms = set(evidence.get("symptoms", []))
        emotions = set(evidence.get("emotions", []))
        
        # 1. Sleep Issues
        if "insomnia" in symptoms or "fatigue" in symptoms:
            sleep_rag = self.rag_db.get("SleepDisturbance", {})
            if sleep_rag:
                sleep_tips = sleep_rag.get("strategies", {}).get("default", [])
                if sleep_tips:
                    existing = aggregated_strategies.get("sleep", [])
                    aggregated_strategies["sleep"] = existing + sleep_tips

        # 2. Anxiety/Panic (if not primary)
        if ("anxiety" in emotions or "restlessness" in symptoms) and primary_state != "AnxietyRisk":
             anx_rag = self.rag_db.get("AnxietyRisk", {})
             if anx_rag:
                 anx_tips = anx_rag.get("strategies", {}).get("default", [])
                 if anx_tips:
                     aggregated_strategies["calming"] = aggregated_strategies.get("calming", []) + anx_tips
        
        # 3. Social Isolation (if not primary)
        if "withdrawal" in symptoms or "loneliness" in emotions:
            iso_rag = self.rag_db.get("SocialIsolation", {})
            if iso_rag:
                iso_tips = iso_rag.get("strategies", {}).get("default", [])
                if iso_tips:
                     aggregated_strategies["social_connection"] = aggregated_strategies.get("social_connection", []) + iso_tips

        # Create a temporary RAG object with aggregated strategies for generation
        generation_rag = primary_rag.copy()
        generation_rag["strategies"] = aggregated_strategies
        
        # Handle clarification case
        if action == "ask_clarification":
            response = self._generate_clarification(user_input, questions, generation_rag)
            return ExplanationResult(
                response_text=response,
                coping_suggestions=[],
                disclaimer="",
                used_llm=self.use_llm,
                raw_state=primary_state
            )
        
        # Generate explanation
        if self.use_llm:
            response = self._generate_with_llm(primary_state, evidence, generation_rag, action)
        else:
            response = self._generate_template(primary_state, evidence, generation_rag, action)
        
        # Add disclaimer for cautious explanations
        disclaimer = self.disclaimer if action == "explain_cautious" else ""
        
        return ExplanationResult(
            response_text=response,
            coping_suggestions=generation_rag.get("strategies", {}).get("default", [])[:2],
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
            # Retry logic for picking a working key
            attempts = 0
            max_attempts = len(self.api_keys) * 2 # Try a few times
            
            while attempts < max_attempts:
                client = self._get_client()
                if not client:
                    break
                    
                try:
                    prompt = CLARIFICATION_PROMPT.format(
                        user_input=user_input,
                        questions=questions
                    )
                    response = client.chat.completions.create(
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
                    print(f"LLM clarification attempt {attempts+1} failed: {e}")
                    attempts += 1
            
            print("All LLM keys failed for clarification. Falling back to template.")
        
        return f"{empathy}\n\n{question}"
    
    def _generate_template(
        self,
        state: str,
        evidence: Dict[str, List[str]],
        rag_data: Dict,
        action: str
    ) -> str:
        # Template logic (unchanged)
        empathy = rag_data.get("empathy", "I hear you.")
        description = rag_data.get("description", "")
        # Get strategies dict
        all_strategies = rag_data.get("strategies", {"default": []})
        
        # Select best category based on triggers
        triggers = evidence.get("triggers", [])
        selected_category = "default"
        
        for trigger in triggers:
            if trigger in ["academic", "exam", "grades", "classes"]:
                if "academic" in all_strategies:
                    selected_category = "academic"
                    break
            elif trigger in ["social", "relationship", "family", "friends"]:
                if "social" in all_strategies:
                    selected_category = "social"
                    break
            elif trigger in ["financial", "money", "work", "job"]:
                if "financial" in all_strategies:
                    selected_category = "financial"
                elif "work" in all_strategies:
                    selected_category = "work"
                    break
                     
        coping = all_strategies.get(selected_category, all_strategies.get("default", []))
        
        evidence_parts = []
        if evidence.get("emotions"):
            evidence_parts.append(f"feeling {', '.join(evidence['emotions'])}")
        if evidence.get("symptoms"):
            evidence_parts.append(f"experiencing {', '.join(evidence['symptoms'])}")
        if evidence.get("triggers"):
            evidence_parts.append(f"related to {', '.join(evidence['triggers'])}")
        
        evidence_summary = " and ".join(evidence_parts) if evidence_parts else "what you shared"
        
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
        if not self.use_llm:
            return self._generate_template(state, evidence, rag_data, action)
        
        # Flatten strategies for LLM awareness
        all_strategies = rag_data.get("strategies", {})
        flat_strategies = []
        for cat, tips in all_strategies.items():
            flat_strategies.append(f"{cat.upper()}: {', '.join(tips)}")
        
        prompt = REPHRASE_PROMPT.format(
            state=state,
            evidence=str(evidence),
            coping="\n".join(flat_strategies),
            empathy=rag_data.get("empathy", "")
        )
        
        # Retry logic
        attempts = 0
        max_attempts = len(self.api_keys) * 2
        
        while attempts < max_attempts:
            client = self._get_client()
            if not client:
                break
                
            try:
                response = client.chat.completions.create(
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
                print(f"LLM generation attempt {attempts+1} failed: {e}")
                attempts += 1
        
        print("All LLM keys failed. Falling back to template.")
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
