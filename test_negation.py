
from agents.pipeline import check_crisis, _is_explicitly_denied
from agents.ml_extractor import extract_signals

test_text = "I don't want to die; I want help."
extraction = extract_signals(test_text)
print("extraction result:", extraction)

print("\n_is_explicitly_denied with 'want to die':", _is_explicitly_denied(test_text, "want to die"))
print("_is_explicitly_denied with 'die':", _is_explicitly_denied(test_text, "die"))
