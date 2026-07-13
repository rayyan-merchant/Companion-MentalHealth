import os
import unittest
from unittest.mock import patch

from agents.ml_extractor import MLSignalExtractor
from agents.pipeline import check_crisis
from agents.symbolic_reasoner import reason_from_signals


class SafetyPipelineTests(unittest.TestCase):
    def setUp(self):
        self.extractor = MLSignalExtractor(use_embeddings=False)

    def extract(self, text):
        return self.extractor.extract(text).to_dict()

    def test_negated_depression_is_not_reasoning_evidence(self):
        extraction = self.extract("I'm not depressed, just tired.")
        depression = next(
            item for item in extraction["emotions"]
            if item["label"] == "depression"
        )

        self.assertTrue(depression["negated"])
        emotions = [
            item["label"] for item in extraction["emotions"]
            if not item["negated"]
        ]
        symptoms = [
            item["label"] for item in extraction["symptoms"]
            if not item["negated"]
        ]
        result = reason_from_signals(emotions, symptoms, [])
        self.assertNotEqual(result["primary_state"], "DepressiveSpectrum")

    def test_negated_anxiety_and_sleep_are_not_positive_signals(self):
        extraction = self.extract("I am not anxious and I do not have trouble sleeping.")
        positive_labels = {
            item["label"]
            for category in ("emotions", "symptoms")
            for item in extraction[category]
            if not item["negated"]
        }
        self.assertNotIn("anxiety", positive_labels)
        self.assertNotIn("insomnia", positive_labels)

    def test_explicit_denial_does_not_trigger_emergency_alert(self):
        text = "I don't want to die; I want help."
        self.assertIsNone(check_crisis(text, self.extract(text)))

    def test_later_affirmative_phrase_overrides_an_earlier_denial(self):
        text = "I didn't want to die before, but now I want to die."
        result = check_crisis(text, self.extract(text))
        self.assertEqual(result["crisis_type"], "suicidal_ideation")

    def test_common_variants_and_typos_trigger_crisis(self):
        for text in ("I wanna die", "I will suicide", "suicdie"):
            with self.subTest(text=text):
                result = check_crisis(text, self.extract(text))
                self.assertEqual(result["crisis_type"], "suicidal_ideation")

    def test_short_follow_up_in_crisis_context_triggers_crisis(self):
        history = "User: I want to die\nUser: I feel hopeless"
        result = check_crisis("kill", self.extract("kill"), history)
        self.assertEqual(result["crisis_type"], "suicidal_ideation")

    def test_safe_update_after_crisis_context_does_not_repeat_crisis(self):
        history = "User: I want to die\nUser: I feel hopeless"
        text = "I feel very happy right now"
        self.assertIsNone(check_crisis(text, self.extract(text), history))

    def test_help_request_after_crisis_context_still_triggers_crisis(self):
        history = "User: I want to die\nUser: I feel hopeless"
        text = "help please"
        result = check_crisis(text, self.extract(text), history)
        self.assertEqual(result["crisis_type"], "suicidal_ideation")

    def test_inability_to_stay_safe_triggers_crisis(self):
        text = "I cannot keep myself safe tonight."
        result = check_crisis(text, self.extract(text))
        self.assertEqual(result["crisis_type"], "suicidal_ideation")

    def test_method_access_plus_farewell_triggers_crisis(self):
        text = "I have pills beside me and I'm saying goodbye."
        result = check_crisis(text, self.extract(text))
        self.assertEqual(result["crisis_type"], "suicidal_ideation")

    def test_named_target_threat_triggers_harm_alert(self):
        text = "I want to hurt my boss."
        result = check_crisis(text, self.extract(text))
        self.assertEqual(result["crisis_type"], "harm_to_others")

    def test_chest_pain_and_breathing_difficulty_is_medical_red_flag(self):
        text = "My chest hurts and I can't breathe."
        result = check_crisis(text, self.extract(text))
        self.assertEqual(result["crisis_type"], "medical_emergency")

    def test_common_idiom_is_not_a_crisis(self):
        text = "My exam is killing me."
        self.assertIsNone(check_crisis(text, self.extract(text)))

    def test_embeddings_are_opt_in(self):
        with patch.dict(os.environ, {}, clear=True):
            extractor = MLSignalExtractor()
        self.assertFalse(extractor.use_embeddings)
        self.assertFalse(extractor._embedding_initialization_attempted)


if __name__ == "__main__":
    unittest.main()
