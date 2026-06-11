import unittest

from backend.session_routes import _deterministic_insight


class DashboardInsightTests(unittest.TestCase):
    def test_offline_insight_does_not_repeat_message_content(self):
        history = "\n".join(
            [
                "User: private first reflection",
                "Companion: response",
                "User: private second reflection",
            ]
        )

        insight = _deterministic_insight(history)

        self.assertIn("2 recent reflections", insight)
        self.assertNotIn("private", insight)


if __name__ == "__main__":
    unittest.main()
