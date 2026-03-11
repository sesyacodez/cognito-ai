import unittest
from unittest.mock import patch

from utils.firebase_auth import FirebaseAuthError, verify_firebase_token


class FirebaseAuthTests(unittest.TestCase):
    @patch("utils.firebase_auth.auth.verify_id_token")
    @patch("utils.firebase_auth.get_app")
    @patch("utils.firebase_auth.initialize_app")
    def test_verify_token_success(self, mock_init, mock_get_app, mock_verify):
        mock_get_app.return_value = object()
        mock_verify.return_value = {
            "uid": "firebase-uid-1",
            "email": "user@example.com",
            "name": "Student",
        }

        result = verify_firebase_token("token")

        self.assertEqual(result["uid"], "firebase-uid-1")
        self.assertEqual(result["email"], "user@example.com")
        self.assertEqual(result["name"], "Student")
        mock_init.assert_not_called()

    @patch("utils.firebase_auth.auth.verify_id_token", side_effect=Exception("expired"))
    @patch("utils.firebase_auth.get_app")
    def test_verify_token_expired(self, _mock_get_app, _mock_verify):
        with self.assertRaises(FirebaseAuthError):
            verify_firebase_token("expired-token")

    def test_verify_token_missing(self):
        with self.assertRaises(FirebaseAuthError):
            verify_firebase_token("")


if __name__ == "__main__":
    unittest.main()
