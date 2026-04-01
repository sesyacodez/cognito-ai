import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from utils.auth_stub_store import reset_auth_store
from utils.firebase_auth import FirebaseAuthError
from utils.lesson_stub_store import reset_lesson_store


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


def _mock_run_skill_lesson(skill_name, mode="learn", **kwargs):
    """Pre-built normalized lesson dict for smoke testing."""
    return {
        "lesson_id": "smoke-lesson-id",
        "mode": mode,
        "micro_theory": "This is the micro-theory for the test topic.",
        "questions": [
            {"id": "q1", "prompt": "Easy question?", "difficulty": "easy", "answer_key": "Answer 1"},
            {"id": "q2", "prompt": "Medium question?", "difficulty": "medium", "answer_key": "Answer 2"},
            {"id": "q3", "prompt": "Hard question?", "difficulty": "hard", "answer_key": "Answer 3"},
        ],
    }


def _mock_run_skill_evaluation(skill_name, mode="learn", **kwargs):
    """Pre-built evaluation dict for smoke testing."""
    return {
        "correct": True,
        "next_prompt": "Great! What happens when you change the input?",
        "hint": None,
    }


class ApiContractSmokeTests(SimpleTestCase):
    def setUp(self):
        reset_auth_store()
        reset_lesson_store()

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

    # ── Lesson endpoint smoke tests ───────────────────────────────────────────

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_lesson)
    def test_lesson_get_returns_contract_shape(self, _mock):
        """GET /api/lessons/{id} returns micro_theory and questions without answer_key."""
        response = self.client.get(
            "/api/lessons/test-lesson-123?module_topic=Python+Loops&mode=learn"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("lesson_id", payload)
        self.assertIn("micro_theory", payload)
        self.assertIn("questions", payload)
        self.assertEqual(len(payload["questions"]), 3)
        # answer_key must NOT be exposed in the GET response
        for q in payload["questions"]:
            self.assertNotIn("answer_key", q)
            self.assertIn("prompt", q)
            self.assertIn("difficulty", q)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_lesson)
    def test_lesson_get_is_cached_on_second_request(self, mock_run):
        """Second GET for same lesson_id uses cache (skill called only once)."""
        self.client.get("/api/lessons/cached-lesson-id?module_topic=Loops")
        self.client.get("/api/lessons/cached-lesson-id?module_topic=Loops")

        # run_skill should only be called once (second request hits cache)
        self.assertEqual(mock_run.call_count, 1)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_evaluation)
    def test_lesson_answer_returns_contract_shape(self, _mock):
        """POST /api/lessons/{id}/answer returns correct, next_prompt, and progress."""
        response = self.client.post(
            "/api/lessons/test-lesson-123/answer",
            data=json.dumps({"question_id": "q1", "answer": "A loop repeats code."}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("correct", payload)
        self.assertIn("next_prompt", payload)
        self.assertIn("progress", payload)
        progress = payload["progress"]
        self.assertIn("xp", progress)
        self.assertIn("stars_remaining", progress)
        self.assertIn("status", progress)
        self.assertIn(progress["status"], ["not_started", "in_progress", "completed"])

    def test_lesson_answer_missing_fields_returns_400(self):
        """POST /api/lessons/{id}/answer without required fields → 400."""
        response = self.client.post(
            "/api/lessons/test-lesson-123/answer",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_evaluation)
    def test_lesson_hint_returns_contract_shape(self, _mock):
        """POST /api/lessons/{id}/hint returns hint and stars_remaining."""
        response = self.client.post(
            "/api/lessons/test-lesson-123/hint",
            data=json.dumps({"question_id": "q1", "hint_level": 1}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("hint", payload)
        self.assertIn("stars_remaining", payload)
        self.assertIsInstance(payload["stars_remaining"], int)
        self.assertGreaterEqual(payload["stars_remaining"], 0)

    def test_lesson_answer_invalid_json_returns_400(self):
        """POST /api/lessons/{id}/answer with invalid JSON → 400."""
        response = self.client.post(
            "/api/lessons/test-lesson-123/answer",
            data="{not-json}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_lesson_hint_invalid_json_returns_400(self):
        """POST /api/lessons/{id}/hint with invalid JSON → 400."""
        response = self.client.post(
            "/api/lessons/test-lesson-123/hint",
            data="{not-json}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
