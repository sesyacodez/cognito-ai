import json
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from utils.auth_stub_store import reset_auth_store
from utils.firebase_auth import FirebaseAuthError


class AuthStubTests(SimpleTestCase):
    def setUp(self):
        reset_auth_store()

    def test_register_returns_session_and_user(self):
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "student@example.com",
                    "password": "secret-123",
                    "name": "Student",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn("session_token", payload)
        self.assertEqual(payload["user"]["email"], "student@example.com")
        self.assertEqual(payload["user"]["name"], "Student")

    def test_login_returns_session_and_user(self):
        self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "student@example.com",
                    "password": "secret-123",
                    "name": "Student",
                }
            ),
            content_type="application/json",
        )

        response = self.client.post(
            "/api/auth/login",
            data=json.dumps(
                {
                    "email": "student@example.com",
                    "password": "secret-123",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("session_token", payload)
        self.assertEqual(payload["user"]["email"], "student@example.com")

    def test_firebase_login_accepts_dev_token(self):
        response = self.client.post(
            "/api/auth/firebase-login",
            data=json.dumps({"id_token": "dev-token-123"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("session_token", payload)
        self.assertIn("user", payload)
        self.assertIn("email", payload["user"])

    @override_settings(AUTH_STUB_ALLOW_FIREBASE_FALLBACK=False)
    @patch(
        "apps.auth.views.verify_firebase_token",
        side_effect=FirebaseAuthError("invalid"),
    )
    def test_firebase_login_returns_401_when_fallback_disabled(self, _mock_verify):
        response = self.client.post(
            "/api/auth/firebase-login",
            data=json.dumps({"id_token": "invalid-token"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_firebase_login_requires_id_token(self):
        response = self.client.post(
            "/api/auth/firebase-login",
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
