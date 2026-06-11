import json
import unittest
from pathlib import Path

from agents.ml_extractor import MLSignalExtractor
from agents.pipeline import check_crisis
from agents.symbolic_reasoner import reason_from_signals


class EvaluationHarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = Path(__file__).parent.parent / "evaluation" / "cases.v1.jsonl"
        cls.cases = [
            json.loads(line)
            for line in corpus.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.extractor = MLSignalExtractor(use_embeddings=False)

    def test_versioned_evaluation_corpus(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                extraction = self.extractor.extract(case["text"]).to_dict()
                crisis = check_crisis(case["text"], extraction)
                expected_crisis = case.get("expect_crisis")
                if expected_crisis:
                    self.assertIsNotNone(crisis)
                    self.assertEqual(crisis["crisis_type"], expected_crisis)
                    continue
                self.assertIsNone(crisis)
                emotions = [
                    item["label"] for item in extraction.get("emotions", [])
                    if not item.get("negated", False)
                ]
                symptoms = [
                    item["label"] for item in extraction.get("symptoms", [])
                    if not item.get("negated", False)
                ]
                triggers = [
                    item["label"] for item in extraction.get("triggers", [])
                    if not item.get("negated", False)
                ]
                reasoning = reason_from_signals(emotions, symptoms, triggers)
                if case.get("expect_state"):
                    self.assertEqual(
                        reasoning["primary_state"], case["expect_state"]
                    )
                if case.get("forbid_state"):
                    self.assertNotEqual(
                        reasoning["primary_state"], case["forbid_state"]
                    )
                if case.get("expect_rule"):
                    self.assertIn(
                        case["expect_rule"], reasoning["rules_fired"]
                    )


if __name__ == "__main__":
    unittest.main()
