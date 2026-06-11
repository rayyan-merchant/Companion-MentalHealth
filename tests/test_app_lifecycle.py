import unittest

from fastapi.testclient import TestClient

from backend.main import app


class AppLifecycleTests(unittest.TestCase):
    def test_resources_can_restart_on_a_new_event_loop(self):
        with TestClient(app) as first_client:
            first = first_client.get("/api/config/public")

        with TestClient(app) as second_client:
            second = second_client.get("/api/config/public")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)


if __name__ == "__main__":
    unittest.main()
