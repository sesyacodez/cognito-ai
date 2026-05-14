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
    if skill_name == "progress_updater":
        return {
            "xp_earned": 100,
            "total_xp": 100,
            "stars_remaining": 3,
            "status": "in_progress",
            "correctness": True,
        }
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


def _mock_run_skill_roadmap_dynamic(skill_name, mode="learn", **kwargs):
    if skill_name != "decomposer":
        raise AssertionError(f"Unexpected skill: {skill_name}")

    topic = kwargs.get("topic", "General Learning Path")
    return {
        "roadmap_id": "dynamic-roadmap-id",
        "mode": mode,
        "modules": [
            {
                "id": "m1",
                "title": f"{topic}: Foundations",
                "index": 0,
                "outcome": "Understand the core foundations.",
            },
            {
                "id": "m2",
                "title": f"{topic}: Guided Practice",
                "index": 1,
                "outcome": "Apply concepts in structured exercises.",
            },
            {
                "id": "m3",
                "title": f"{topic}: Real Application",
                "index": 2,
                "outcome": "Complete a practical mini-project.",
            },
        ],
    }


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

    def test_roadmaps_post_narrow_learn_topic_returns_roadmap(self):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Database Design", "mode": "learn"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["kind"], "roadmap")
        roadmap = payload["roadmap"]
        self.assertIn("roadmap_id", roadmap)
        self.assertIn("mode", roadmap)
        self.assertIn("modules", roadmap)
        self.assertEqual(roadmap["topic"], "Database Design")
        self.assertGreaterEqual(len(roadmap["modules"]), 1)
        for i, module in enumerate(roadmap["modules"]):
            self.assertEqual(module["index"], i)

    def test_roadmaps_post_broad_topic_returns_curriculum_preview(self):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Machine Learning", "mode": "learn"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["kind"], "curriculum_preview")
        plan = payload["plan"]
        self.assertEqual(plan["mode"], "learn")
        self.assertGreaterEqual(len(plan["courses"]), 2)
        self.assertLessEqual(len(plan["courses"]), 6)

    def test_roadmaps_post_force_roadmap_bypasses_curriculum_split(self):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps(
                {"topic": "Machine Learning", "mode": "learn", "force_roadmap": True}
            ),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["kind"], "roadmap")
        self.assertGreaterEqual(len(payload["roadmap"]["modules"]), 1)

    def test_roadmaps_post_solve_mode_returns_contract_shape(self):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Build a REST API", "mode": "solve"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["kind"], "roadmap")
        roadmap = payload["roadmap"]
        self.assertIn(roadmap["mode"], ["learn", "solve"])
        self.assertGreaterEqual(len(roadmap["modules"]), 1)

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
        payload = response.json()
        self.assertEqual(payload["kind"], "roadmap")
        self.assertEqual(payload["roadmap"]["mode"], "learn")

    def test_roadmaps_post_persists_and_lists_for_user(self):
        create_response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Database Design", "mode": "learn"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(create_response.status_code, 201)
        created = create_response.json()
        self.assertEqual(created["kind"], "roadmap")
        roadmap_id = created["roadmap"]["roadmap_id"]

        list_response = self.client.get("/api/roadmaps", **self.auth_headers)
        self.assertEqual(list_response.status_code, 200)
        roadmaps = list_response.json()
        matching = [item for item in roadmaps if item["roadmap_id"] == roadmap_id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["topic"], "Database Design")
        self.assertEqual(matching[0]["type"], "topic")
        self.assertGreaterEqual(len(matching[0]["modules"]), 1)

    @patch("apps.roadmaps.services.run_skill", side_effect=_mock_run_skill_roadmap_dynamic)
    def test_roadmaps_post_uses_dynamic_module_count_from_decomposer(self, _mock_run_skill):
        response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "Git Basics", "mode": "learn"}),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["kind"], "roadmap")
        roadmap = payload["roadmap"]
        self.assertEqual(len(roadmap["modules"]), 3)
        self.assertEqual([module["index"] for module in roadmap["modules"]], [0, 1, 2])
        self.assertTrue(all("Git Basics" in module["title"] for module in roadmap["modules"]))

    def test_roadmap_detail_returns_only_owner_roadmap(self):
        create_response = self.client.post(
            "/api/roadmaps",
            data=json.dumps({"topic": "REST APIs", "mode": "solve"}),
            content_type="application/json",
            **self.auth_headers,
        )
        created = create_response.json()
        roadmap_id = created["roadmap"]["roadmap_id"]

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
            data=json.dumps({"question_id": question_id, "answer": "Answer 1"}),
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
            data=json.dumps({"question_id": question_id, "answer": "Answer 1"}),
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

    # ── Dashboard endpoint smoke tests ────────────────────────────────────────

    def test_dashboard_get_returns_contract_shape(self):
        """GET /api/dashboard returns expected top-level keys."""
        response = self.client.get("/api/dashboard", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("total_xp", payload)
        self.assertIn("total_stars", payload)
        self.assertIn("lessons_completed", payload)
        self.assertIn("lessons_in_progress", payload)
        self.assertIn("current_streak", payload)
        self.assertIn("longest_streak", payload)
        self.assertIn("recent_activity", payload)
        self.assertIsInstance(payload["recent_activity"], list)

    def test_dashboard_post_not_allowed(self):
        """POST /api/dashboard should return 405 Method Not Allowed."""
        response = self.client.post("/api/dashboard")
        self.assertEqual(response.status_code, 405)

    # ── Curriculum endpoint smoke tests ───────────────────────────────────────

    def test_curriculum_create_persists_and_eagerly_expands_first_course(self):
        courses_payload = [
            {"index": 0, "title": "Linear Algebra", "outcome": "Comfortably manipulate vectors and matrices."},
            {"index": 1, "title": "Probability", "outcome": "Reason about uncertainty in models."},
            {"index": 2, "title": "Supervised Learning", "outcome": "Train and evaluate predictive models."},
        ]

        response = self.client.post(
            "/api/curriculums",
            data=json.dumps(
                {"topic": "Machine Learning", "mode": "learn", "courses": courses_payload}
            ),
            content_type="application/json",
            **self.auth_headers,
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertIn("curriculum_id", payload)
        self.assertEqual(payload["topic"], "Machine Learning")
        self.assertEqual(len(payload["courses"]), 3)
        self.assertIsNotNone(payload.get("first_course_id"))
        self.assertIsNotNone(payload.get("first_roadmap"))
        first_course = payload["courses"][0]
        self.assertTrue(first_course["expanded"])
        self.assertEqual(payload["courses"][1]["expanded"], False)

    def test_curriculum_list_returns_user_curriculums(self):
        self.client.post(
            "/api/curriculums",
            data=json.dumps(
                {
                    "topic": "Web Development",
                    "mode": "learn",
                    "courses": [
                        {"index": 0, "title": "HTML & CSS", "outcome": "Build static layouts."},
                        {"index": 1, "title": "JavaScript", "outcome": "Make pages interactive."},
                    ],
                }
            ),
            content_type="application/json",
            **self.auth_headers,
        )

        response = self.client.get("/api/curriculums", **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        items = response.json()
        self.assertGreaterEqual(len(items), 1)
        self.assertEqual(items[0]["topic"], "Web Development")

    def test_curriculum_expand_is_idempotent(self):
        create_response = self.client.post(
            "/api/curriculums",
            data=json.dumps(
                {
                    "topic": "Data Science",
                    "mode": "learn",
                    "courses": [
                        {"index": 0, "title": "Pandas", "outcome": "Wrangle tabular data."},
                        {"index": 1, "title": "Visualization", "outcome": "Communicate findings."},
                    ],
                }
            ),
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(create_response.status_code, 201)
        created = create_response.json()
        curriculum_id = created["curriculum_id"]
        second_course_id = created["courses"][1]["id"]

        first_expand = self.client.post(
            f"/api/curriculums/{curriculum_id}/courses/{second_course_id}/expand",
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(first_expand.status_code, 200)
        first_roadmap_id = first_expand.json()["roadmap"]["roadmap_id"]

        second_expand = self.client.post(
            f"/api/curriculums/{curriculum_id}/courses/{second_course_id}/expand",
            content_type="application/json",
            **self.auth_headers,
        )
        self.assertEqual(second_expand.status_code, 200)
        self.assertEqual(second_expand.json()["roadmap"]["roadmap_id"], first_roadmap_id)

    def test_curriculum_detail_requires_auth(self):
        response = self.client.get("/api/curriculums")
        self.assertEqual(response.status_code, 401)
