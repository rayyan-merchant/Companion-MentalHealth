import unittest
import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()
        self.client.get("/api/config/public")

    def tearDown(self):
        self.client_context.__exit__(None, None, None)

    def csrf_headers(self):
        return {"X-CSRF-Token": self.client.cookies["companion_csrf"]}

    def signup(self, prefix="api-test"):
        email = f"{prefix}-{uuid.uuid4().hex[:12]}@example.com"
        response = self.client.post(
            "/api/auth/signup",
            headers=self.csrf_headers(),
            json={"email": email, "password": "LongTestPassword123"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return email, response.json()["user"]

    def test_cookie_auth_and_csrf_enforcement(self):
        _, user = self.signup()
        self.assertNotIn("access_token", user)
        self.assertIn("companion_session", self.client.cookies)

        response = self.client.post("/api/sessions", json={})
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            "/api/sessions",
            headers=self.csrf_headers(),
            json={},
        )
        self.assertEqual(response.status_code, 201)

    def test_cross_user_conversation_returns_404(self):
        self.signup("owner")
        created = self.client.post(
            "/api/sessions",
            headers=self.csrf_headers(),
            json={},
        ).json()
        session_id = created["session_id"]
        self.client.post("/api/auth/logout", headers=self.csrf_headers())

        self.client.get("/api/config/public")
        self.signup("other")
        response = self.client.get(f"/api/sessions/{session_id}")
        self.assertEqual(response.status_code, 404)

    def test_message_idempotency_returns_same_exchange(self):
        self.signup("idempotent")
        session = self.client.post(
            "/api/sessions",
            headers=self.csrf_headers(),
            json={},
        ).json()
        payload = {
            "text": "I feel stressed about exams",
            "client_message_id": f"client-{uuid.uuid4()}",
        }
        with patch("backend.session_routes.process_message") as pipeline:
            pipeline.return_value = {
                "session_id": session["session_id"],
                "response": "That pressure sounds difficult.",
                "state": "AcademicStress",
                "confidence": "high",
                "action": "explain",
                "evidence": {
                    "emotions": ["stress"],
                    "symptoms": [],
                    "triggers": ["academic"],
                },
                "follow_up_questions": [],
                "disclaimer": "",
                "rules_fired": ["R_ACS_02"],
                "rule_version": "1.0.0",
                "confidence_rationale": {"evidence_categories": 2},
                "used_fallback": True,
                "provider": None,
            }
            first = self.client.post(
                f"/api/sessions/{session['session_id']}/message",
                headers=self.csrf_headers(),
                json=payload,
            )
            second = self.client.post(
                f"/api/sessions/{session['session_id']}/message",
                headers=self.csrf_headers(),
                json=payload,
            )
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(
            first.json()["assistant_message_id"],
            second.json()["assistant_message_id"],
        )
        self.assertEqual(pipeline.call_count, 1)


if __name__ == "__main__":
    unittest.main()
