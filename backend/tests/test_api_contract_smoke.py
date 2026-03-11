import json
from unittest.mock import patch

from django.test import SimpleTestCase

from utils.auth_stub_store import reset_auth_store
from utils.firebase_auth import FirebaseAuthError


class ApiContractSmokeTests(SimpleTestCase):
    def setUp(self):
        reset_auth_store()

    def test_roadmaps_get_returns_list(self):
        response = self.client.get("/api/roadmaps")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_roadmaps_post_returns_placeholder_shape(self):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Machine Learning"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn("roadmap_id", payload)
        self.assertIn("modules", payload)
        self.assertEqual(len(payload["modules"]), 5)
        self.assertEqual(
            [module["index"] for module in payload["modules"]],
            [0, 1, 2, 3, 4],
        )

    def test_roadmaps_post_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/roadmaps",
            data="{not-json}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

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
