"""Tests for POST /api/vision (image_to_text) with mocked OpenRouter."""

import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase


class VisionImageToTextTests(SimpleTestCase):
    def test_missing_image_returns_400(self):
        response = self.client.post(
            "/api/vision",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False)
    def test_missing_api_key_returns_503(self):
        response = self.client.post(
            "/api/vision",
            data=json.dumps({"image": "Zm9v"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "k"}, clear=False)
    @patch("apps.vision.views.httpx.post")
    def test_success_returns_text(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "  hello world  "}}],
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        response = self.client.post(
            "/api/vision",
            data=json.dumps({"image": "Zm9v", "mime_type": "image/png"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["text"], "hello world")
        mock_post.assert_called_once()

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "k"}, clear=False)
    @patch("apps.vision.views.httpx.post")
    def test_upstream_http_error_returns_502(self, mock_post):
        import httpx

        bad = MagicMock()
        bad.raise_for_status.side_effect = httpx.HTTPStatusError(
            "upstream",
            request=MagicMock(),
            response=MagicMock(status_code=502, text="bad"),
        )
        mock_post.return_value = bad

        response = self.client.post(
            "/api/vision",
            data=json.dumps({"image": "Zm9v"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 502)
