
import sys
sys.path.insert(0, '.')

from agents.pipeline import check_crisis
from agents.ml_extractor import MLSignalExtractor

extractor = MLSignalExtractor(use_embeddings=False)

test_text = "I don't want to die; I want help."
extraction = extractor.extract(test_text).to_dict()

print("Calling check_crisis...")
result = check_crisis(test_text, extraction)

print("\nResult of check_crisis:")
print(result)
print("\nTest passed:", result is None)
