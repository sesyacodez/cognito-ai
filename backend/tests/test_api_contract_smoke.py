import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from utils.auth_stub_store import reset_auth_store
from utils.firebase_auth import FirebaseAuthError


def _mock_run_skill_learn(skill_name, mode="learn", **kwargs):
    """Pre-built normalized roadmap dict for learn mode (3 modules)."""
    return {
        "roadmap_id": "test-uuid-1234",
        "mode": mode,
        "modules": [
            {"id": f"m{i}", "title": f"Module {i}", "outcome": f"Outcome {i}", "index": i - 1}
            for i in range(1, 4)
        ],
    }


def _mock_run_skill_solve(skill_name, mode="solve", **kwargs):
    """Pre-built normalized roadmap dict for solve mode (1 module)."""
    return {
        "roadmap_id": "test-uuid-5678",
        "mode": "solve",
        "modules": [
            {"id": "m1", "title": "Build the thing", "outcome": "Working project", "index": 0}
        ],
    }


class ApiContractSmokeTests(SimpleTestCase):
    def setUp(self):
        reset_auth_store()

    def test_roadmaps_get_returns_list(self):
        response = self.client.get("/api/roadmaps")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @patch("apps.roadmaps.views.run_skill", side_effect=_mock_run_skill_learn)
    def test_roadmaps_post_learn_mode_returns_contract_shape(self, _mock):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Machine Learning", "mode": "learn"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn("roadmap_id", payload)
        self.assertIn("mode", payload)
        self.assertIn("modules", payload)
        self.assertGreaterEqual(len(payload["modules"]), 1)
        for i, module in enumerate(payload["modules"]):
            self.assertEqual(module["index"], i)

    @patch("apps.roadmaps.views.run_skill", side_effect=_mock_run_skill_solve)
    def test_roadmaps_post_solve_mode_returns_contract_shape(self, _mock):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Build a REST API", "mode": "solve"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["mode"], "solve")
        self.assertGreaterEqual(len(payload["modules"]), 1)

    def test_roadmaps_post_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/roadmaps",
            data="{not-json}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("apps.roadmaps.views.run_skill", side_effect=_mock_run_skill_learn)
    def test_roadmaps_post_defaults_to_learn_mode(self, _mock):
        """Omitting mode defaults to learn."""
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Python"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["mode"], "learn")

    def test_auth_register_and_login_contract(self):
        register_response = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "smoke@example.com",
                    "password": "secret-123",
                    "name": "Smoke User",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(register_response.status_code, 201)
        register_payload = register_response.json()
        self.assertIn("session_token", register_payload)
        self.assertIn("user", register_payload)

        login_response = self.client.post(
            "/api/auth/login",
            data=json.dumps(
                {
                    "email": "smoke@example.com",
                    "password": "secret-123",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)
        login_payload = login_response.json()
        self.assertIn("session_token", login_payload)
        self.assertIn("user", login_payload)

    @patch(
        "apps.auth.views.verify_firebase_token",
        side_effect=FirebaseAuthError("invalid"),
    )
    def test_firebase_login_contract_with_dev_fallback(self, _mock_verify):
        response = self.client.post(
            "/api/auth/firebase-login",
            data=json.dumps({"id_token": "smoke-token"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("session_token", payload)
        self.assertIn("user", payload)
