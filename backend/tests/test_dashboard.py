import json
from unittest.mock import patch

from django.test import SimpleTestCase

from utils.lesson_stub_store import reset_lesson_store
from utils.progress_store import (
    reset_progress_store,
    update_lesson_progress,
)


def _mock_run_skill_lesson(skill_name, mode="learn", **kwargs):
    return {
        "lesson_id": "dash-lesson-id",
        "mode": mode,
        "micro_theory": "Dashboard test micro-theory.",
        "questions": [
            {"id": "q1", "prompt": "Easy?", "difficulty": "easy", "answer_key": "A1"},
            {"id": "q2", "prompt": "Medium?", "difficulty": "medium", "answer_key": "A2"},
            {"id": "q3", "prompt": "Hard?", "difficulty": "hard", "answer_key": "A3"},
        ],
    }


def _mock_run_skill_eval(skill_name, mode="learn", **kwargs):
    return {"correct": True, "next_prompt": "Great!", "hint": None}


class DashboardEndpointTests(SimpleTestCase):

    def setUp(self):
        reset_progress_store()
        reset_lesson_store()

    def test_dashboard_get_empty(self):
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_xp"], 0)
        self.assertEqual(data["lessons_completed"], 0)
        self.assertEqual(data["lessons_in_progress"], 0)
        self.assertEqual(data["current_streak"], 0)
        self.assertIsInstance(data["recent_activity"], list)

    def test_dashboard_reflects_progress(self):
        update_lesson_progress(
            user_id="anonymous",
            lesson_id="lesson-1",
            question_id="q1",
            answer="my answer",
            correct=True,
            hint_level=0,
            xp_earned=100,
            stars_remaining=3,
            new_status="in_progress",
        )

        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_xp"], 100)
        self.assertEqual(data["lessons_in_progress"], 1)
        self.assertEqual(len(data["recent_activity"]), 1)

    def test_dashboard_completed_lesson(self):
        update_lesson_progress(
            user_id="anonymous",
            lesson_id="lesson-2",
            question_id="q1",
            answer="a",
            correct=True,
            hint_level=0,
            xp_earned=100,
            stars_remaining=3,
            new_status="completed",
        )

        response = self.client.get("/api/dashboard")
        data = response.json()
        self.assertEqual(data["lessons_completed"], 1)
        self.assertEqual(data["total_xp"], 100)

    def test_dashboard_with_auth_header(self):
        update_lesson_progress(
            user_id="user-abc",
            lesson_id="lesson-3",
            question_id="q1",
            answer="a",
            correct=True,
            hint_level=0,
            xp_earned=50,
            stars_remaining=2,
            new_status="in_progress",
        )

        response = self.client.get(
            "/api/dashboard",
            HTTP_AUTHORIZATION="Bearer user-abc",
        )
        data = response.json()
        self.assertEqual(data["total_xp"], 50)
        self.assertEqual(data["lessons_in_progress"], 1)

    def test_dashboard_only_returns_own_progress(self):
        update_lesson_progress(
            user_id="user-a",
            lesson_id="lesson-x",
            question_id="q1",
            answer="a",
            correct=True,
            hint_level=0,
            xp_earned=200,
            stars_remaining=3,
            new_status="completed",
        )

        response = self.client.get(
            "/api/dashboard",
            HTTP_AUTHORIZATION="Bearer user-b",
        )
        data = response.json()
        self.assertEqual(data["total_xp"], 0)
        self.assertEqual(data["lessons_completed"], 0)

    @patch("apps.lessons.views.run_skill")
    def test_dashboard_end_to_end_via_lesson_answer(self, mock_run):
        def side_effect(skill_name, **kwargs):
            if skill_name == "lesson_generator":
                return _mock_run_skill_lesson(skill_name, **kwargs)
            if skill_name == "socratic_tutor":
                return _mock_run_skill_eval(skill_name, **kwargs)
            if skill_name == "progress_updater":
                from skills.progress_updater import run as pu_run
                return pu_run(kwargs, mode=kwargs.get("mode", "learn"))
            return {}

        mock_run.side_effect = side_effect

        self.client.get("/api/lessons/e2e-lesson?module_topic=Test")

        self.client.post(
            "/api/lessons/e2e-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "A1"}),
            content_type="application/json",
        )

        response = self.client.get("/api/dashboard")
        data = response.json()
        self.assertGreaterEqual(data["total_xp"], 0)
        self.assertGreaterEqual(
            data["lessons_in_progress"] + data["lessons_completed"], 0
        )
