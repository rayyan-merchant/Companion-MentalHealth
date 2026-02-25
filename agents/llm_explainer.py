from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import os
import random

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
    print("Warning: groq not installed. Groq LLM disabled.")

try:
    from google import genai
    from google.genai import types as genai_types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Gemini LLM disabled.")



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

REFERENCE EMPATHY:
"{empathy}"

TASK:
Write a warm, empathetic response that validates the user's experience and seamlessly integrates 1-2 relevant coping strategies from the reference list.
Do not explicitly say "I suggest strategies". Weave them into the conversation naturally.

Keep the response under 100 words. Do NOT use clinical language."""

CLARIFICATION_PROMPT = """
CONTEXT:
{conversation_history}

USER INPUT: "{user_input}"

The system needs more information to help. 
Suggested questions from logic: {questions}

TASK:
Write a gentle, empathetic response that validates the user's input and naturally asks ONE of the suggested questions (or a better contextual one) to understand their situation better.
Do not list the questions. Weave ONE into the conversation naturally.
"""


INSIGHT_PROMPT = """
CONTEXT:
{conversation_history}

TASK:
Based *strictly* on the recent conversation history above, provide a single, warm, psychological observation or insight for the user.
Focus on:
1. Validating their feelings (e.g., "It's understandable that exams are causing stress...")
2. Noting positive traits or efforts (e.g., "...but your persistence in studying is evident.")
3. Connecting patterns if visible (e.g., "You seem to feel more anxious late at night.")

DO NOT diagnose. DO NOT give advice. Just a supportive observation.
Keep it under 2 sentences.
Speak directly to the user ("You...").
"""

@dataclass
class ExplanationResult:
    """Output from the LLM explainer."""
    response_text: str
    coping_suggestions: List[str]
    disclaimer: str
    used_llm: bool
    llm_provider: Optional[str] = None
    raw_state: Optional[str] = None
    insight: Optional[str] = None  # Added for dashboard insights


class LLMExplanationAgent:

    def __init__(self, api_key: Optional[str] = None):
        self.groq_keys = []
        self.gemini_keys = []
        self.model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.gemini_model = os.getenv("GEMINI_LLM_MODEL", "gemini-2.0-flash")
        self.use_groq = False
        self.use_gemini = False
        
        # Load Groq keys from arg or env
        if api_key:
            self.groq_keys = [k.strip() for k in api_key.split(",") if k.strip()]
        else:
            env_keys = os.getenv("GROQ_API_KEY", "")
            self.groq_keys = [k.strip() for k in env_keys.split(",") if k.strip()]
        
        if GROQ_AVAILABLE and self.groq_keys:
            self.use_groq = True
            print(f"[LLM] Groq: {len(self.groq_keys)} keys loaded. Model: {self.model}")
        elif not GROQ_AVAILABLE:
            print("[LLM] Groq: SDK not installed.")
        else:
            print("[LLM] Groq: No API keys found.")
        
        # Load Gemini keys from env
        gemini_env = os.getenv("GEMINI_API_KEY", "")
        self.gemini_keys = [k.strip() for k in gemini_env.split(",") if k.strip()]
        
        if GEMINI_AVAILABLE and self.gemini_keys:
            self.use_gemini = True
            print(f"[LLM] Gemini: {len(self.gemini_keys)} keys loaded. Model: {self.gemini_model}")
        elif not GEMINI_AVAILABLE:
            print("[LLM] Gemini: SDK not installed.")
        else:
            print("[LLM] Gemini: No API keys found.")
        
        if not self.use_groq and not self.use_gemini:
            print("[LLM] WARNING: No LLM providers available! Using template fallback only.")
        
        self.rag_db = RAG_SNIPPETS
        self.disclaimer = (
            "This is an observational assessment, not a diagnosis. "
            "If you're experiencing ongoing distress, please consider speaking with "
            "a counselor or mental health professional."
        )

    @property
    def use_llm(self) -> bool:
        """Backward compatibility: True if any LLM provider is available."""
        return self.use_groq or self.use_gemini

    # Keep backward-compat property for pipeline references to api_keys
    @property
    def api_keys(self):
        return self.groq_keys

    def _get_groq_client(self):
        """Get a Groq client with a random key from the pool."""
        if not self.groq_keys:
            return None
        
        selected_key = random.choice(self.groq_keys)
        try:
            return Groq(api_key=selected_key)
        except Exception as e:
            print(f"[LLM] Groq client creation failed (key ...{selected_key[-4:]}): {e}")
            return None

    def _call_groq(self, system_prompt: str, user_prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Try calling Groq with retry across keys. Returns response text or None."""
        if not self.use_groq:
            return None
        
        attempts = 0
        max_attempts = min(len(self.groq_keys) * 2, 6)
        
        while attempts < max_attempts:
            client = self._get_groq_client()
            if not client:
                break
            
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"[LLM] Groq attempt {attempts+1} failed: {e}")
                attempts += 1
        
        print("[LLM] All Groq keys exhausted.")
        return None

    def _call_gemini(self, system_prompt: str, user_prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Try calling Gemini with retry across keys. Returns response text or None."""
        if not self.use_gemini:
            return None
        
        for i, key in enumerate(self.gemini_keys):
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model=self.gemini_model,
                    contents=user_prompt,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                    )
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"[LLM] Gemini attempt {i+1} failed (key ...{key[-4:]}): {e}")
        
        print("[LLM] All Gemini keys exhausted.")
        return None

    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Tuple[Optional[str], Optional[str]]:
        """Call LLM with Groq-first, Gemini-fallback strategy.
        Returns (response_text, provider_name) or (None, None)."""
        
        # Try Groq first (faster, higher throughput)
        result = self._call_groq(system_prompt, user_prompt, max_tokens, temperature)
        if result:
            return result, "groq"
        
        # Fallback to Gemini
        print("[LLM] Falling back to Gemini...")
        result = self._call_gemini(system_prompt, user_prompt, max_tokens, temperature)
        if result:
            return result, "gemini"
        
        return None, None

    def explain(
        self,
        primary_state: str,
        evidence: Dict[str, List[str]],
        confidence_decision: Dict[str, Any],
        user_input: str = "",
        history_context: str = ""
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
            response, provider = self._generate_clarification(user_input, questions, generation_rag, history_context)
            return ExplanationResult(
                response_text=response,
                coping_suggestions=[],
                disclaimer="",
                used_llm=provider is not None,
                llm_provider=provider,
                raw_state=primary_state
            )
        
        # Generate explanation
        if self.use_llm:
            response, provider = self._generate_with_llm(primary_state, evidence, generation_rag, action, history_context)
        else:
            response = self._generate_template(primary_state, evidence, generation_rag, action)
            provider = None
        
        # Add disclaimer for cautious explanations
        disclaimer = self.disclaimer if action == "explain_cautious" else ""
        
        return ExplanationResult(
            response_text=response,
            coping_suggestions=generation_rag.get("strategies", {}).get("default", [])[:2],
            disclaimer=disclaimer,
            used_llm=provider is not None,
            llm_provider=provider,
            raw_state=primary_state
        )
    
    def _generate_clarification(
        self,
        user_input: str,
        questions: List[str],
        rag_data: Dict,
        history_context: str = ""
    ) -> Tuple[str, Optional[str]]:
        empathy = rag_data.get("empathy", "I want to understand what you're going through.")
        
        if questions:
            question = questions[0]
        else:
            question = "Could you share a bit more about what's been on your mind?"
        
        if self.use_llm:
            prompt = CLARIFICATION_PROMPT.format(
                conversation_history=history_context,
                user_input=user_input,
                questions=questions
            )
            result, provider = self._call_llm(SYSTEM_PROMPT, prompt, max_tokens=80, temperature=0.7)
            if result:
                return result, provider
            
            print("[LLM] All providers failed for clarification. Falling back to template.")
        
        return f"{empathy}\n\n{question}", None
    
    def _generate_template(
        self,
        state: str,
        evidence: Dict[str, List[str]],
        rag_data: Dict,
        action: str
    ) -> str:
        empathy = rag_data.get("empathy", "I hear you.")
        description = rag_data.get("description", "")
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
        action: str,
        history_context: str = ""
    ) -> Tuple[str, Optional[str]]:
        if not self.use_llm:
            return self._generate_template(state, evidence, rag_data, action), None
        
        # Flatten strategies for LLM awareness
        all_strategies = rag_data.get("strategies", {})
        flat_strategies = []
        for cat, tips in all_strategies.items():
            flat_strategies.append(f"{cat.upper()}: {', '.join(tips)}")
        
        # Truncate history if too long (safety mechanism)
        if len(history_context) > 2000:
            history_context = "..." + history_context[-2000:]
            
        prompt = REPHRASE_PROMPT.format(
            conversation_history=history_context,
            state=state,
            evidence=str(evidence),
            coping="\n".join(flat_strategies),
            empathy=rag_data.get("empathy", "")
        )
        
        result, provider = self._call_llm(SYSTEM_PROMPT, prompt, max_tokens=150, temperature=0.7)
        if result:
            return result, provider
        
        print("[LLM] All providers failed. Falling back to template.")
        return self._generate_template(state, evidence, rag_data, action), None

    def generate_insight(self, conversation_history: str) -> Optional[str]:
        """Generate a dashboard insight from chat history."""
        if not self.use_llm:
            return None
            
        # Truncate if too long
        if len(conversation_history) > 3000:
            conversation_history = "..." + conversation_history[-3000:]
            
        prompt = INSIGHT_PROMPT.format(conversation_history=conversation_history)
        
        # Lower temperature for more grounded insights
        result, _ = self._call_llm(SYSTEM_PROMPT, prompt, max_tokens=100, temperature=0.6)
        return result


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
    api_key: Optional[str] = None,
    history_context: str = ""
) -> Dict[str, Any]:
    explainer = get_explainer(api_key)
    result = explainer.explain(primary_state, evidence, confidence_decision, user_input, history_context)
    
    return {
        "response_text": result.response_text,
        "coping_suggestions": result.coping_suggestions,
        "disclaimer": result.disclaimer,
        "used_llm": result.used_llm,
        "llm_provider": result.llm_provider,
        "raw_state": result.raw_state
    }


def generate_dashboard_insight(conversation_history: str, api_key: Optional[str] = None) -> Optional[str]:
    """Generate a standalone insight for the dashboard."""
    explainer = get_explainer(api_key)
    return explainer.generate_insight(conversation_history)


if __name__ == "__main__":
    print("LLM Explanation Agent Test (Groq + Gemini)")
    print("=" * 60)
    
    explainer = get_explainer()
    print(f"\nGroq available: {explainer.use_groq}")
    print(f"Gemini available: {explainer.use_gemini}")
    print(f"Any LLM available: {explainer.use_llm}")
    
    test_cases = [
        (
            "AcademicStress",
            {"emotions": ["stress"], "symptoms": [], "triggers": ["academic"]},
            {"action": "explain", "clarification_questions": []},
            "Academic stress case"
        )
    ]
    
    for state, evidence, decision, description in test_cases:
        result = generate_explanation(state, evidence, decision, user_input="I'm stressed")
        print(f"\n{description}")
        print(f"Used LLM: {result['used_llm']} (Provider: {result['llm_provider']})")
        print(f"Response:\n{result['response_text'][:300]}...")

