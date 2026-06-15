
import sys
sys.path.insert(0, '.')
from agents.pipeline import check_crisis, _is_explicitly_denied
from agents.ml_extractor import MLSignalExtractor

extractor = MLSignalExtractor(use_embeddings=False)

text = "I don't want to die; I want help."
extraction = extractor.extract(text).to_dict()
print("Testing check_crisis on:", text)
result = check_crisis(text, extraction)
print("check_crisis result:", result)
print("Expected: None (explicit denial)")

print("\n_is_explicitly_denied checks:")
print("  'die' :", _is_explicitly_denied(text, "die"))
print("  'want to die' :", _is_explicitly_denied(text, "want to die"))
print("  'I don't want to die' :", _is_explicitly_denied(text, "I don't want to die"))
