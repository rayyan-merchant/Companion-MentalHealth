
import re
from agents.ml_extractor import MLSignalExtractor

def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())

def _token_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    shorter = min(len(left), len(right))
    longer = max(len(left), len(right))
    if longer - shorter > 2:
        return 0.0
    matches = sum(1 for a, b in zip(left, right, strict=False) if a == b)
    return matches / longer

def _contains_fuzzy_token(text_lower: str, target: str) -> bool:
    target_lower = target.lower()
    if target_lower in text_lower:
        return True
    for token in re.findall(r"[a-z']+", text_lower):
        if token == target_lower:
            return True
        if _token_similarity(token, target_lower) >= 0.7:
            return True
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

CRISIS_PHRASES_SELF = [
    "kill myself", "want to die", "end my life", "better off dead",
    "wish i was dead", "wish i were dead", "wish i could die",
    "i want to be dead", "i'd rather be dead", "rather die",
    "going to kill myself", "gonna kill myself", "planning to kill myself",
    "thinking about killing myself", "thinking of killing myself",
    "end it all", "ending it all", "ending it tonight",
    "no reason to live", "no reason to be alive", "no point in living",
    "don't want to be alive", "don't want to exist", "don't want to be here",
    "not worth living", "life isn't worth",
    "hurt myself", "harm myself", "cutting myself", "cut myself",
    "self-harm", "self harm", "self-harming",
    "slit my wrists", "slit my throat",
    "overdose", "take all my pills", "swallow pills",
    "hang myself", "hanging myself",
    "jump off", "jump from", "throw myself",
    "shoot myself", "drown myself", "poison myself",
    "burn myself", "starve myself to death",
    "sleep forever", "never wake up",
    "everyone would be happier without me",
    "burden to everyone", "burden to my family",
    "world would be better without me",
    "better off without me",
    "no one would miss me", "nobody would care if i",
    "disappear forever", "just disappear",
    "won't be around much longer", "not gonna be here",
]

def _is_explicitly_denied(text: str, phrase: str) -> bool:
    phrase_starts = [match.start() for match in re.finditer(re.escape(phrase), text)]
    if not phrase_starts:
        return False
    denial_pattern = (
        r"(?:\bdon't\b|\bdo not\b|\bdidn't\b|\bdid not\b|\bnever\b|"
        r"\bnot\b)(?:\s+\w+){0,4}\s*$"
    )
    return all(
        re.search(
            denial_pattern,
            text[max(0, phrase_start -45):phrase_start]
        )
        for phrase_start in phrase_starts
    )

def check_crisis_debug(text: str):
    text_lower = _normalize_text(text)
    print("text_lower:", text_lower)
    crisis_keywords = ["die", "suicide", "suicidal", "suicdie", "kill", "wanna die", "want to die", "will suicide"]
    print("\nChecking crisis keywords:", crisis_keywords)
    for keyword in crisis_keywords:
        print(f"\nChecking keyword: {keyword}")
        has_fuzzy = _contains_fuzzy_token(text_lower, keyword)
        print(f"Has fuzzy match: {has_fuzzy}")
        if has_fuzzy:
            is_denied = False
            print("\nChecking exact phrases in CRISIS_PHRASES_SELF present:", [ep for ep in CRISIS_PHRASES_SELF if ep in text_lower])
            for exact_phrase in CRISIS_PHRASES_SELF:
                if exact_phrase in text_lower:
                    print("Found exact phrase:", exact_phrase)
                    if _is_explicitly_denied(text, exact_phrase):
                        print("Exact phrase is denied, setting is_denied=True")
                        is_denied = True
                        break
            if keyword in text_lower and _is_explicitly_denied(text, keyword):
                print("Keyword is denied, setting is_denied=True")
                is_denied = True
            print(f"is_denied: {is_denied}")
            if not is_denied:
                print("Returning crisis result")
                return True
    return False

if __name__ == "__main__":
    test_text = "I don't want to die; I want help."
    print("Testing:", test_text)
    print("Result:", check_crisis_debug(test_text))
