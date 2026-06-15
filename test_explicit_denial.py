
import re

def _is_explicitly_denied(text: str, phrase: str) -> bool:
    """Return True only when every occurrence is directly scoped by a denial."""
    phrase_starts = [
        match.start() for match in re.finditer(re.escape(phrase), text)]
    if not phrase_starts:
        return False

    denial_pattern = (
        r"(?:\bdon't\b|\bdo not\b|\bdidn't\b|\bdid not\b|\bnever\b|"
        r"\bnot\b)(?:\s+\w+){0,4}\s*$"
    )
    print("Checking phrase:", repr(phrase))
    print("Phrase starts found at positions:", phrase_starts)
    results = []
    for phrase_start in phrase_starts:
        substring = text[max(0, phrase_start - 45):phrase_start]
        print(f"Substring for denial check:", repr(substring))
        match = re.search(denial_pattern, substring)
        results.append(bool(match))
        print("Denial found:", bool(match))
    return all(results)

test_text = "I don't want to die; I want help."
print("Is 'want to die' explicitly denied?", _is_explicitly_denied(test_text, "want to die"))
print("Is 'die' explicitly denied?", _is_explicitly_denied(test_text, "die"))
