import re
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from agents.confidence_gate import evaluate_confidence
from agents.llm_explainer import generate_explanation
from agents.ml_extractor import extract_signals
from agents.session_memory import get_session
from agents.symbolic_reasoner import get_rule_version, reason_from_signals


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


# =============================================================================
# TIER 1: Exact phrase matching (highest confidence, instant)
# =============================================================================

CRISIS_PHRASES_SELF = [
    # --- Suicidal ideation (direct) ---
    "kill myself", "want to die", "end my life", "better off dead",
    "wish i was dead", "wish i were dead", "wish i could die",
    "i want to be dead", "i'd rather be dead", "rather die",
    "going to kill myself", "gonna kill myself", "planning to kill myself",
    "thinking about killing myself", "thinking of killing myself",
    "end it all", "ending it all", "ending it tonight",
    "no reason to live", "no reason to be alive", "no point in living",
    "don't want to be alive", "don't want to exist", "don't want to be here",
    "not worth living", "life isn't worth",

    # --- Self-harm (direct) ---
    "hurt myself", "harm myself", "cutting myself", "cut myself",
    "self-harm", "self harm", "self-harming",
    "slit my wrists", "slit my throat",
    "overdose", "take all my pills", "swallow pills",
    "hang myself", "hanging myself",
    "jump off", "jump from", "throw myself",
    "shoot myself", "drown myself", "poison myself",
    "burn myself", "starve myself to death",

    # --- Passive / indirect suicidal ---
    "sleep forever", "never wake up",
    "everyone would be happier without me",
    "burden to everyone", "burden to my family",
    "world would be better without me",
    "better off without me",
    "no one would miss me", "nobody would care if i",
    "disappear forever", "just disappear",
    "won't be around much longer", "not gonna be here",
]

CRISIS_PHRASES_OTHERS = [
    # --- Harm to others ---
    "kill someone", "kill them", "kill him", "kill her",
    "want to kill", "going to kill", "gonna kill",
    "murder", "hurt someone badly", "hurt them badly",
    "want to hurt people", "want to harm people",
    "shoot up", "shoot everyone", "shoot them",
    "stab someone", "stab them", "stab him", "stab her",
    "bomb", "blow up",
    "make them pay with their life", "they deserve to die",
]

# =============================================================================
# TIER 2: Contextual regex patterns (catches indirect phrasing)
# =============================================================================

CONTEXTUAL_PATTERNS = [
    # "I can't do this/take this/go on anymore"
    (r"\b(i\s+)?(can'?t|cannot|couldn'?t)\s+(take|handle|do|bear|stand|survive)\s+(it|this|life|things|anything)\s+(any\s*more|anymore|any\s*longer)", "suicidal_ideation"),

    # "There's no way out / no escape / no hope" (Handling "absolutely", "just", etc.)
    (r"\b(there'?s|there\s+is)\s+(absolutely\s+|just\s+)?no\s+(way\s+out|escape|hope|future|point)", "suicidal_ideation"),

    # "I give up on life / I've given up"
    (r"\b(i('?ve| have)?\s+(give|given)\s+up\s+on\s+(life|living|everything))", "suicidal_ideation"),

    # "I just want the pain/suffering to stop/end"
    (r"\bi\s+just\s+want\s+(the\s+)?(pain|suffering|hurt|misery|agony)\s+to\s+(stop|end|go away|be over)", "suicidal_ideation"),

    # "I want it to be over / want this to end"
    (r"\bi\s+want\s+(it|this|everything|life)\s+to\s+(be\s+over|end|stop)", "suicidal_ideation"),

    # "I'm done with life / done with everything"
    (r"\bi'?m\s+done\s+with\s+(life|living|everything|this\s+world|all\s+of\s+(this|it))", "suicidal_ideation"),

    # "I've been thinking about death a lot"
    (r"\b(thinking|thought)\s+(about|of)\s+(death|dying|suicide|killing|ending)", "suicidal_ideation"),

    # "I have a plan to ..." (planning language)
    (r"\bi\s+(have|got|made)\s+a\s+plan\s+to\s+(die|end|kill|hurt|harm)", "suicidal_ideation"),

    # "I wrote a note / goodbye letter / will"
    (r"\b(wrote|writing|write)\s+(a\s+)?(suicide\s+note|goodbye\s+letter|farewell\s+letter|final\s+letter|my\s+will)", "suicidal_ideation"),

    # "Giving away my things / saying goodbye to everyone"
    (r"\b(giving\s+away\s+(my|all)\s+(stuff|things|possessions)|saying\s+goodbye\s+to\s+every(one|body))", "suicidal_ideation"),

    # "I want to hurt/harm/attack someone/people"
    (r"\b(i|i'?m)\s+((gonna)|((want|need|going|plan)\s+to))\s+(hurt|harm|attack|injure)\s+(him|her|them|someone|people|everyone|everybody)\b", "harm_to_others"),

    # "I'm going to do something terrible/violent"
    (r"\bi'?m\s+(going|gonna)\s+(to\s+)?do\s+something\s+(terrible|violent|horrible|awful|drastic)", "harm_to_others"),

    # "I cannot keep myself safe"
    (r"\b(i\s+)?(can'?t|cannot|don'?t\s+think\s+i\s+can)\s+keep\s+myself\s+safe\b", "suicidal_ideation"),

    # Passive death wish: "I wish I would not wake up"
    (r"\b(wish|hope)(?:\s+\w+){0,4}\s+(not|never)\s+(to\s+)?wake\s+up\b", "suicidal_ideation"),

    # Access to a method combined with farewell language
    (r"\b(pills?|gun|knife|rope)\b.{0,80}\b(saying\s+goodbye|goodbye\s+letter|farewell|final\s+message)\b", "suicidal_ideation"),

    # Threats toward a specifically named relationship or role
    (r"\b(i|i'?m)\s+((gonna)|((want|need|going|plan)\s+to))\s+"
     r"(hurt|harm|attack|injure|kill)\s+(my\s+)?"
     r"(boss|teacher|partner|parent|mother|father|friend|classmate|coworker|roommate|family)\b", "harm_to_others"),
]

MEDICAL_RED_FLAG_PATTERNS = [
    r"\b(chest\s+(pain|hurts?|tightness|pressure))\b.{0,80}\b(can'?t\s+breathe|cannot\s+breathe|short\s+of\s+breath|faint(?:ing)?|collapse[sd]?|dizz(?:y|iness))\b",
    r"\b(can'?t\s+breathe|cannot\s+breathe|short\s+of\s+breath)\b.{0,80}\b(chest\s+(pain|hurts?|tightness|pressure))\b",
]

# =============================================================================
# TIER 3: False-positive idiom filter (clever, context-aware)
# =============================================================================

# Idiom patterns that LOOK like crisis but are actually safe expressions.
# Each is (regex_pattern, list_of_words_that_must_NOT_accompany_it_for_it_to_be_safe)
# If the idiom matches AND none of the amplifiers are present → it's a false positive.

FALSE_POSITIVE_IDIOMS = [
    # "X is killing me" / "killing it" (academic/work stress or slang)
    r"\b(it'?s|is|are|this is|that'?s|exam|test|homework|work|class|assignment|project|deadline|finals?)\s+(is\s+)?(killing|gonna kill)\s+(me|us)\b",

    # "dying of laughter / boredom / embarrassment / curiosity"
    r"\b(dying|die|died)\s+(of|from|with)\s+(laughter|boredom|embarrassment|curiosity|hunger|thirst|cringe|excitement|anticipation|jealousy)\b",

    # "I'm dead" / "I'm so dead" (slang for surprised/screwed)
    r"\b(i'?m\s+(so\s+)?dead|that'?s\s+dead|dead\s+serious|deadass)\b",

    # "dead tired / dead exhausted / dead weight"
    r"\b(dead\s+(tired|exhausted|bored|weight|wrong|silent|quiet|serious|last|end|center|heat|line|lock|pan|ringer))\b",

    # "I could kill for a ..." (wanting something badly)
    r"\b(could\s+kill\s+for\s+(a|an|some))\b",

    # "you're killing it" / "she killed it" (doing great)
    r"\b(killed?\s+it|killing\s+it|killed?\s+the\s+(game|exam|test|interview|presentation))\b",

    # "killer headache / killer workout / killer app"
    r"\b(killer\s+(headache|migraine|workout|app|deal|feature|look|outfit|song|move|instinct))\b",

    # "a]die-hard fan / die hard"
    r"\b(die[\s-]?hard)\b",

    # "I'd die for ..." (expressing enthusiasm)
    r"\b(i'?d\s+die\s+for\s+(that|this|some|a|an|pizza|food|chocolate))\b",

    # "this/that kills me" (funny)
    r"\b(this|that)\s+(kills|slays)\s+me\b",

    # "drop dead gorgeous"
    r"\bdrop\s+dead\s+(gorgeous|beautiful|handsome)\b",

    # "over my dead body"
    r"\bover\s+my\s+dead\s+body\b",

    # "suicide mission / suicide squad / suicide pass" (metaphorical)
    r"\b(suicide\s+(mission|squad|pass|play|door|run|bunt))\b",

    # "scared/bored/worried to death"
    r"\b(scared|bored|worried|sick|tired|loved|tickled|done|frozen|starved)\s+to\s+death\b",
]

# Words that re-escalate even if an idiom matches (override the idiom filter)
# If ANY of these appear alongside the idiom, treat it as real crisis
ESCALATION_OVERRIDES = [
    "suicide", "suicidal", "kill myself", "end my life", "self-harm",
    "hurt myself", "harm myself", "want to die", "overdose",
    "jump off", "hang myself", "slit", "cutting myself",
    "no reason to live", "better off dead", "wish i was dead",
    "pills", "gun", "rope", "bridge", "knife",  # method mentions
]


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def _token_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    shorter = min(len(left), len(right))
    longer = max(len(left), len(right))
    if longer - shorter > 2:
        return 0.0
    matches = sum(1 for a, b in zip(left, right) if a == b)
    return matches / longer


def _contains_fuzzy_token(text_lower: str, target: str) -> bool:
    target_lower = target.lower()
    # First check for exact multi-word match
    if target_lower in text_lower:
        return True
    
    # Check single token fuzzy match
    for token in re.findall(r"[a-z']+", text_lower):
        if token == target_lower:
            return True
        if _token_similarity(token, target_lower) >= 0.7:
            return True
    
    # For multi-word targets, check if all words are present with fuzzy matching
    target_words = target_lower.split()
    if len(target_words) > 1:
        text_tokens = re.findall(r"[a-z']+", text_lower)
        all_found = True
        for t_word in target_words:
            found = False
            for token in text_tokens:
                if token == t_word or _token_similarity(token, t_word) >= 0.7:
                    found = True
                    break
            if not found:
                all_found = False
                break
        if all_found:
            return True
            
    return False


def _history_has_recent_user_crisis(history_text: str) -> bool:
    if not history_text:
        return False
    history_lower = _normalize_text(history_text)
    indicators = (
        CRISIS_PHRASES_SELF
        + CRISIS_PHRASES_OTHERS
        + ["wanna die", "suicide", "suicidal", "i will suicide", "suicdie"]
    )
    return any(indicator in history_lower for indicator in indicators) or any(
        re.search(pattern, history_lower)
        for pattern in (
            r"\b(i\s+)?(can'?t|cannot|couldn'?t)\s+(take|handle|do|bear|stand|survive)\s+(it|this|life|things|anything)\s+(any\s*more|anymore|any\s*longer)",
            r"\b(there'?s|there\s+is)\s+(absolutely\s+|just\s+)?no\s+(way\s+out|escape|hope|future|point)",
        )
    )


def _is_explicitly_denied(text: str, phrase: str) -> bool:
    """Return True only when every occurrence is directly scoped by a denial."""
    phrase_starts = [
        match.start() for match in re.finditer(re.escape(phrase), text)
    ]
    if not phrase_starts:
        return False

    denial_pattern = (
        r"(?:\bdon't\b|\bdo not\b|\bdidn't\b|\bdid not\b|\bnever\b|"
        r"\bnot\b)(?:\s+\w+){0,4}\s*$"
    )
    return all(
        re.search(
            denial_pattern,
            text[max(0, phrase_start - 45):phrase_start]
        )
        for phrase_start in phrase_starts
    )


def check_crisis(
    text: str,
    extraction_result: Dict[str, Any],
    conversation_history: str | None = None,
) -> Optional[Dict[str, Any]]:
    """Three-tier crisis detection: exact phrases → contextual patterns → idiom filter.
    
    Returns crisis intervention dict if a genuine crisis is detected, None otherwise.
    """
    text_lower = _normalize_text(text)

    # Acute physical red flags must not be mislabeled as panic without first
    # directing the user to urgent medical assessment.
    for pattern in MEDICAL_RED_FLAG_PATTERNS:
        if re.search(pattern, text_lower):
            return {
                "response_text": (
                    "Chest pain together with trouble breathing can need urgent "
                    "medical attention. Please call emergency services now or ask "
                    "someone nearby to help you get immediate care."
                ),
                "primary_state": "Urgent Medical Concern",
                "confidence": "high",
                "action_taken": "crisis_intervention",
                "crisis_type": "medical_emergency",
                "evidence_summary": {
                    "symptoms": ["Chest Pain", "Breathing Difficulty"],
                    "emotions": [],
                    "triggers": ["Medical Red Flag"],
                    "keyword": "[medical red flag]"
                },
                "clarification_questions": [],
                "disclaimer": "URGENT: Seek immediate medical care."
            }

    # First, always check history for recent crisis, because if user is in crisis, any short utterance should trigger crisis
    if conversation_history and _history_has_recent_user_crisis(conversation_history):
        # If history has crisis, any short message like "kill", "die", "help", "please", "suicide" triggers crisis
        triggered_phrase = f"[context] {text_lower}"
        crisis_type = "suicidal_ideation"
        return {
            "response_text": (
                "I hear how much pain you're in right now. Please, you don't have to go through "
                "this alone. There are people who want to listen and help you stay safe. "
                "Your life matters."
            ),
            "primary_state": "Crisis (Suicidal Ideation)",
            "confidence": "high",
            "action_taken": "crisis_intervention",
            "crisis_type": crisis_type,
            "evidence_summary": {
                "symptoms": ["Suicidal Ideation"],
                "emotions": ["Despair"],
                "triggers": ["Crisis"],
                "keyword": triggered_phrase,
            },
            "clarification_questions": [],
            "disclaimer": "URGENT: Immediate professional support is recommended.",
        }

    # ── Step 1: Check if this is a false-positive idiom FIRST ─────────────
    # We check idioms early because they need to gate the result.
    idiom_matched = False
    for idiom_pattern in FALSE_POSITIVE_IDIOMS:
        if re.search(idiom_pattern, text_lower):
            idiom_matched = True
            break

    # If an idiom matched, check if there are ALSO real escalation signals.
    # If no escalation overrides → it's safe, skip crisis.
    if idiom_matched:
        has_escalation = any(esc in text_lower for esc in ESCALATION_OVERRIDES)
        if not has_escalation:
            return None  # Safe idiom, no crisis

    # ── Step 1b: Short crisis utterances and typo-level variants ──────────
    # Check fuzzy for suicidal phrases - expanded list
    crisis_keywords = ["die", "suicide", "suicidal", "suicdie", "kill", "wanna die", "want to die", "will suicide"]
    for keyword in crisis_keywords:
        if _contains_fuzzy_token(text_lower, keyword):
            triggered_phrase = f"[fuzzy] {keyword}"
            crisis_type = "suicidal_ideation"
            return {
                "response_text": (
                    "I hear how much pain you're in right now. Please, you don't have to go through "
                    "this alone. There are people who want to listen and help you stay safe. "
                    "Your life matters."
                ),
                "primary_state": "Crisis (Suicidal Ideation)",
                "confidence": "high",
                "action_taken": "crisis_intervention",
                "crisis_type": crisis_type,
                "evidence_summary": {
                    "symptoms": ["Suicidal Ideation"],
                    "emotions": ["Despair"],
                    "triggers": ["Crisis"],
                    "keyword": triggered_phrase,
                },
                "clarification_questions": [],
                "disclaimer": "URGENT: Immediate professional support is recommended.",
            }

    # ── Step 2: Tier 1 — Exact phrase matching ────────────────────────────
    triggered_phrase = None
    crisis_type = None

    for phrase in CRISIS_PHRASES_SELF:
        if phrase in text_lower and not _is_explicitly_denied(text_lower, phrase):
            triggered_phrase = phrase
            # Distinguish suicidal ideation vs self-harm
            self_harm_markers = ["cut", "slit", "burn", "harm", "hurt myself", "self-harm", "self harm"]
            crisis_type = "self_harm" if any(m in phrase for m in self_harm_markers) else "suicidal_ideation"
            break

    if not triggered_phrase:
        for phrase in CRISIS_PHRASES_OTHERS:
            if phrase in text_lower:
                triggered_phrase = phrase
                crisis_type = "harm_to_others"
                break

    # ── Step 3: Tier 2 — Contextual regex patterns ────────────────────────
    if not triggered_phrase:
        for pattern, ptype in CONTEXTUAL_PATTERNS:
            if re.search(pattern, text_lower):
                triggered_phrase = f"[pattern] {pattern[:40]}..."
                crisis_type = ptype
                break

    # ── Step 4: No crisis detected ────────────────────────────────────────
    if not triggered_phrase:
        return None

    # ── Step 5: Negation check ────────────────────────────────────────────
    # ── Step 6: Build crisis response ─────────────────────────────────────
    if crisis_type == "harm_to_others":
        response_text = (
            "I can hear you're going through something really intense right now. "
            "These feelings are serious, and it's important that you talk to someone "
            "who can help. Please reach out to a professional — they're trained to "
            "help in exactly these moments."
        )
        primary_state = "Crisis (Harm Risk)"
        symptoms = ["Violent Ideation"]
        emotions = ["Rage/Distress"]
    elif crisis_type == "self_harm":
        response_text = (
            "I hear how much you're hurting right now. You don't deserve to be in this much pain. "
            "Please, you don't have to go through this alone — there are people trained to help. "
            "Reaching out is the bravest thing you can do."
        )
        primary_state = "Crisis (Self-Harm)"
        symptoms = ["Self-Harm Ideation"]
        emotions = ["Despair"]
    else:  # suicidal_ideation
        response_text = (
            "I hear how much pain you're in right now. Please, you don't have to go through "
            "this alone. There are people who want to listen and help you stay safe. "
            "Your life matters."
        )
        primary_state = "Crisis (Suicidal Ideation)"
        symptoms = ["Suicidal Ideation"]
        emotions = ["Despair"]

    return {
        "response_text": response_text,
        "primary_state": primary_state,
        "confidence": "high",
        "action_taken": "crisis_intervention",
        "crisis_type": crisis_type,
        "evidence_summary": {
            "symptoms": symptoms,
            "emotions": emotions,
            "triggers": ["Crisis"],
            "keyword": triggered_phrase
        },
        "clarification_questions": [],
        "disclaimer": "URGENT: Immediate professional support is recommended."
    }


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
    history_text = "\n".join(
        str(message.get("content", ""))
        for message in (previous_messages or [])
        if message.get("role") == "user"
    )
    
    # 1. Extraction first (to get negation context)
    extraction_result = extract_signals(user_input)
    debug_info["extraction"] = extraction_result

    # 2. Crisis Interceptor (now aware of negation)
    crisis_result = check_crisis(user_input, extraction_result, history_text)
    if crisis_result:
        crisis_type = crisis_result.get("crisis_type")
        result = PipelineResult(
            session_id=session_id,
            response_text=crisis_result["response_text"],
            primary_state=crisis_result["primary_state"],
            confidence=crisis_result["confidence"],
            action_taken=crisis_result["action_taken"],
            evidence_summary=crisis_result["evidence_summary"],
            clarification_questions=crisis_result["clarification_questions"],
            disclaimer=crisis_result["disclaimer"],
            debug={
                "crisis_detected": True,
                "crisis_type": crisis_type,
                "keyword": crisis_result["evidence_summary"]["keyword"],
                "rules_fired": [f"SAFETY_{crisis_type or 'CRISIS'}"],
                "rule_version": get_rule_version(),
                "confidence_rationale": {
                    "reason": "Explicit safety rule matched",
                    "evidence_categories": 1,
                },
                "used_llm": False,
                "llm_provider": None,
            }
        )
        return asdict(result)
    
    # Session is already hydrated/fetched at step 0 if needed, but 'session' variable scope
    # needs to be ensured if step 0 wasn't triggered or if we need to ensure it's loaded.
    # Actually, we can just rely on the 'session' var from step 0 if it exists, or fetch it if not.
    # But for cleaner code, let's just ensure we have 'session' object.
    
    if 'session' not in locals():
         session = get_session(session_id)
    
    session_context = session.get_context()
    conversation_history = session.get_formatted_history(limit=5)
    
    persistence = session_context.persistence_detected
    
    emotions = [
        e["label"] for e in extraction_result.get("emotions", [])
        if not e.get("negated", False)
    ]
    symptoms = [
        s["label"] for s in extraction_result.get("symptoms", [])
        if not s.get("negated", False)
    ]
    triggers = [
        t["label"] for t in extraction_result.get("triggers", [])
        if not t.get("negated", False)
    ]
    
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
    debug_info["rules_fired"] = reasoning_result.get("rules_fired", [])
    debug_info["rule_version"] = reasoning_result.get(
        "rule_version", get_rule_version()
    )
    debug_info["confidence_rationale"] = {
        "reason": confidence_decision.get("reason", "Rule and evidence coverage"),
        "evidence_categories": sum(
            bool(items) for items in (emotions, symptoms, triggers)
        ),
        "needs_clarification": reasoning_result.get(
            "needs_clarification", False
        ),
    }
    
    explanation_result = generate_explanation(
        primary_state=reasoning_result.get("primary_state", "NeedsMoreContext"),
        evidence=reasoning_result.get("evidence_used", {}),
        confidence_decision=confidence_decision,
        user_input=user_input,
        api_key=openai_api_key,
        history_context=conversation_history
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
                    api_key=openai_api_key,
                    history_context=conversation_history
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
    debug_info["used_llm"] = explanation_result.get("used_llm", False)
    debug_info["llm_provider"] = explanation_result.get("llm_provider")
    
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
    crisis_type = result.get("debug", {}).get("crisis_type")
    debug = result.get("debug", {})
    response = {
        "session_id": result["session_id"],
        "response": result["response_text"],
        "state": result["primary_state"],
        "confidence": result["confidence"],
        "action": result["action_taken"],
        "evidence": result["evidence_summary"],
        "follow_up_questions": result["clarification_questions"],
        "disclaimer": result["disclaimer"],
        "rules_fired": debug.get("rules_fired", []),
        "rule_version": debug.get("rule_version", get_rule_version()),
        "confidence_rationale": debug.get("confidence_rationale", {}),
        "used_fallback": not debug.get("used_llm", False),
        "provider": debug.get("llm_provider"),
    }
    if crisis_type:
        response["crisis_type"] = crisis_type
    return response


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
    
    for text, exp in zip(test_inputs, expected, strict=False):
        result = process_message(test_session, text)
        state = result.get("state", "None")
        action = result.get("action", "unknown")
        
        print(f"{text:<40} | {exp:<20} | {state:<20} | {action:<20}")
    
    print("\n" + "=" * 70)
    print("Pipeline test complete.")
