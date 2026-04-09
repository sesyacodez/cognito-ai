import json
from unittest.mock import patch

from django.test import TestCase

from apps.lessons.models import LessonState
from utils.auth_stub_store import reset_auth_store
from utils.firebase_auth import FirebaseAuthError
from utils.lesson_stub_store import reset_lesson_store
from utils.progress_store import reset_progress_store


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


def _mock_run_skill_lesson_flow(skill_name, mode="learn", **kwargs):
    if skill_name == "lesson_generator":
        return _mock_run_skill_lesson(skill_name, mode=mode, **kwargs)
    if skill_name == "socratic_tutor":
        return _mock_run_skill_evaluation(skill_name, mode=mode, **kwargs)
    raise AssertionError(f"Unexpected skill: {skill_name}")


class ApiContractSmokeTests(TestCase):
    def setUp(self):
        reset_auth_store()
        reset_lesson_store()
        reset_progress_store()
        register_response = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": "journey-user@example.com",
                    "password": "secret-123",
                    "name": "Journey User",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(register_response.status_code, 201)
        self.session_token = register_response.json()["session_token"]
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.session_token}"}
        self.lesson_headers = dict(self.auth_headers)

    def test_roadmaps_get_returns_list(self):
        response = self.client.get("/api/roadmaps", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_roadmaps_require_auth(self):
        response = self.client.get("/api/roadmaps")
        self.assertEqual(response.status_code, 401)

    def test_roadmaps_post_learn_mode_returns_contract_shape(self):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Machine Learning", "mode": "learn"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn("roadmap_id", payload)
        self.assertIn("mode", payload)
        self.assertIn("modules", payload)
        self.assertEqual(payload["topic"], "Machine Learning")
        self.assertGreaterEqual(len(payload["modules"]), 1)
        for i, module in enumerate(payload["modules"]):
            self.assertEqual(module["index"], i)

    def test_roadmaps_post_solve_mode_returns_contract_shape(self):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Build a REST API", "mode": "solve"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn(payload["mode"], ["learn", "solve"])
        self.assertGreaterEqual(len(payload["modules"]), 1)

    def test_roadmaps_post_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/roadmaps",
            data="{not-json}",
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_roadmaps_post_defaults_to_learn_mode(self):
        """Omitting mode defaults to learn."""
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Python"}),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["mode"], "learn")

    def test_roadmaps_post_persists_and_lists_for_user(self):
        create_response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Database Design", "mode": "learn"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(create_response.status_code, 201)
        roadmap_id = create_response.json()["roadmap_id"]

        list_response = self.client.get("/api/roadmaps", **self.auth_headers)
        self.assertEqual(list_response.status_code, 200)
        roadmaps = list_response.json()
        matching = [item for item in roadmaps if item["roadmap_id"] == roadmap_id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["topic"], "Database Design")
        self.assertEqual(matching[0]["type"], "topic")
        self.assertEqual(len(matching[0]["modules"]), 5)

    def test_roadmap_detail_returns_only_owner_roadmap(self):
        create_response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "REST APIs", "mode": "solve"}),
            content_type="application/json",
            **self.auth_headers,
        )
        roadmap_id = create_response.json()["roadmap_id"]

        detail_response = self.client.get(f"/api/roadmaps/{roadmap_id}", **self.auth_headers)
        self.assertEqual(detail_response.status_code, 200)
        payload = detail_response.json()
        self.assertEqual(payload["roadmap_id"], roadmap_id)
        self.assertEqual(payload["topic"], "REST APIs")
        self.assertEqual(payload["mode"], "solve")

    # ── Lesson persistence smoke tests ───────────────────────────────────────

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_lesson)
    def test_lesson_get_returns_contract_shape(self, _mock):
        response = self.client.get(
            "/api/lessons/test-lesson-123?module_topic=Python+Loops&mode=learn",
            **self.lesson_headers,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("lesson_id", payload)
        self.assertIn("micro_theory", payload)
        self.assertIn("questions", payload)
        self.assertEqual(len(payload["questions"]), 3)
        for q in payload["questions"]:
            self.assertNotIn("answer_key", q)
            self.assertIn("prompt", q)
            self.assertIn("difficulty", q)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_lesson)
    def test_lesson_get_is_cached_on_second_request(self, mock_run):
        self.client.get(
            "/api/lessons/cached-lesson-id?module_topic=Loops",
            **self.lesson_headers,
        )
        self.client.get(
            "/api/lessons/cached-lesson-id?module_topic=Loops",
            **self.lesson_headers,
        )

        self.assertEqual(mock_run.call_count, 1)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_lesson_flow)
    def test_lesson_answer_returns_contract_shape(self, _mock):
        lesson_response = self.client.get(
            "/api/lessons/test-lesson-123?module_topic=Python+Loops&mode=learn",
            **self.lesson_headers,
        )
        self.assertEqual(lesson_response.status_code, 200)
        lesson_payload = lesson_response.json()
        question_id = lesson_payload["questions"][0]["id"]

        response = self.client.post(
            "/api/lessons/test-lesson-123/answer",
            data=json.dumps({"question_id": question_id, "answer": "A loop repeats code."}),
            content_type="application/json",
            **self.lesson_headers,
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
        response = self.client.post(
            "/api/lessons/test-lesson-123/answer",
            data=json.dumps({}),
            content_type="application/json",
            **self.lesson_headers,
        )
        self.assertEqual(response.status_code, 400)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_lesson_flow)
    def test_lesson_hint_returns_contract_shape(self, _mock):
        lesson_response = self.client.get(
            "/api/lessons/test-lesson-123?module_topic=Python+Loops&mode=learn",
            **self.lesson_headers,
        )
        self.assertEqual(lesson_response.status_code, 200)
        lesson_payload = lesson_response.json()
        question_id = lesson_payload["questions"][0]["id"]

        response = self.client.post(
            "/api/lessons/test-lesson-123/hint",
            data=json.dumps({"question_id": question_id, "hint_level": 1}),
            content_type="application/json",
            **self.lesson_headers,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("hint", payload)
        self.assertIn("stars_remaining", payload)
        self.assertIsInstance(payload["stars_remaining"], int)
        self.assertGreaterEqual(payload["stars_remaining"], 0)

    def test_lesson_answer_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/lessons/test-lesson-123/answer",
            data="{not-json}",
            content_type="application/json",
            **self.lesson_headers,
        )
        self.assertEqual(response.status_code, 400)

    def test_lesson_hint_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/lessons/test-lesson-123/hint",
            data="{not-json}",
            content_type="application/json",
            **self.lesson_headers,
        )
        self.assertEqual(response.status_code, 400)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_run_skill_lesson_flow)
    def test_lesson_state_persists_after_answer(self, _mock):
        lesson_response = self.client.get(
            "/api/lessons/persisted-lesson?module_topic=Persistence+Test&mode=learn",
            **self.lesson_headers,
        )
        lesson_payload = lesson_response.json()
        question_id = lesson_payload["questions"][0]["id"]

        answer_response = self.client.post(
            "/api/lessons/persisted-lesson/answer",
            data=json.dumps({"question_id": question_id, "answer": "A loop repeats code."}),
            content_type="application/json",
            **self.lesson_headers,
        )
        self.assertEqual(answer_response.status_code, 200)

        state = LessonState.objects.get(lesson__lesson_key="persisted-lesson", user__email="journey-user@example.com")
        self.assertEqual(state.xp_earned, answer_response.json()["progress"]["xp"])
        self.assertIn(state.status, ["in_progress", "completed"])

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
