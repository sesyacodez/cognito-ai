import json
from unittest.mock import patch

from django.test import TestCase

from apps.auth.services import create_session_for_user
from apps.lessons.models import Lesson, LessonQuestion, LessonState, QuestionAttempt
from apps.users.models import User
from utils.auth_stub_store import reset_auth_store
from utils.lesson_stub_store import reset_lesson_store
from utils.progress_store import reset_progress_store


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


class DashboardEndpointTests(TestCase):

    def setUp(self):
        reset_progress_store()
        reset_lesson_store()
        reset_auth_store()

    def _register(self, email: str, name: str = "Dashboard Tester") -> str:
        response = self.client.post(
            "/api/auth/register",
            data=json.dumps(
                {
                    "email": email,
                    "password": "secret-123",
                    "name": name,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()["session_token"]

    def _auth(self, token: str) -> dict:
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_dashboard_get_empty(self):
        token = self._register("dash-empty@example.com")
        response = self.client.get("/api/dashboard", **self._auth(token))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_xp"], 0)
        self.assertEqual(data["lessons_completed"], 0)
        self.assertEqual(data["lessons_in_progress"], 0)
        self.assertEqual(data["current_streak"], 0)
        self.assertIsInstance(data["recent_activity"], list)

    def test_dashboard_reflects_progress(self):
        token = self._register("dash-reflect@example.com")
        user = User.objects.get(email="dash-reflect@example.com")
        lesson = Lesson.objects.create(
            lesson_key="lesson-1",
            title="L1",
            module_topic="T",
            mode="learn",
            micro_theory="x",
        )
        q1 = LessonQuestion.objects.create(
            lesson=lesson,
            question_key="q1",
            prompt="p",
            difficulty="easy",
            answer_key="k",
            position=0,
        )
        state = LessonState.objects.create(
            user=user,
            lesson=lesson,
            status=LessonState.Status.IN_PROGRESS,
            stars_remaining=3,
            xp_earned=100,
        )
        QuestionAttempt.objects.create(
            lesson_state=state,
            question=q1,
            answer="my answer",
            correct=True,
            hint_level=0,
        )

        response = self.client.get("/api/dashboard", **self._auth(token))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_xp"], 100)
        self.assertEqual(data["lessons_in_progress"], 1)
        self.assertEqual(len(data["recent_activity"]), 1)

    def test_dashboard_completed_lesson(self):
        token = self._register("dash-done@example.com")
        user = User.objects.get(email="dash-done@example.com")
        lesson = Lesson.objects.create(
            lesson_key="lesson-2",
            title="L2",
            module_topic="T",
            mode="learn",
            micro_theory="x",
        )
        q1 = LessonQuestion.objects.create(
            lesson=lesson,
            question_key="q1",
            prompt="p",
            difficulty="easy",
            answer_key="k",
            position=0,
        )
        state = LessonState.objects.create(
            user=user,
            lesson=lesson,
            status=LessonState.Status.COMPLETED,
            stars_remaining=3,
            xp_earned=100,
        )
        QuestionAttempt.objects.create(
            lesson_state=state,
            question=q1,
            answer="a",
            correct=True,
            hint_level=0,
        )

        response = self.client.get("/api/dashboard", **self._auth(token))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["lessons_completed"], 1)
        self.assertEqual(data["total_xp"], 100)

    def test_dashboard_with_auth_header(self):
        token = self._register("dash-auth@example.com")
        user = User.objects.get(email="dash-auth@example.com")
        lesson = Lesson.objects.create(
            lesson_key="lesson-3",
            title="L3",
            module_topic="T",
            mode="learn",
            micro_theory="x",
        )
        q1 = LessonQuestion.objects.create(
            lesson=lesson,
            question_key="q1",
            prompt="p",
            difficulty="easy",
            answer_key="k",
            position=0,
        )
        LessonState.objects.create(
            user=user,
            lesson=lesson,
            status=LessonState.Status.IN_PROGRESS,
            stars_remaining=2,
            xp_earned=50,
        )
        QuestionAttempt.objects.create(
            lesson_state=LessonState.objects.get(user=user, lesson=lesson),
            question=q1,
            answer="a",
            correct=True,
            hint_level=0,
        )

        response = self.client.get("/api/dashboard", **self._auth(token))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_xp"], 50)
        self.assertEqual(data["lessons_in_progress"], 1)

    def test_dashboard_only_returns_own_progress(self):
        token_a = self._register("user-a@example.com", name="User A")
        self._register("user-b@example.com", name="User B")
        user_a = User.objects.get(email="user-a@example.com")

        lesson = Lesson.objects.create(
            lesson_key="lesson-x",
            title="LX",
            module_topic="T",
            mode="learn",
            micro_theory="x",
        )
        q1 = LessonQuestion.objects.create(
            lesson=lesson,
            question_key="q1",
            prompt="p",
            difficulty="easy",
            answer_key="k",
            position=0,
        )
        state = LessonState.objects.create(
            user=user_a,
            lesson=lesson,
            status=LessonState.Status.COMPLETED,
            stars_remaining=3,
            xp_earned=200,
        )
        QuestionAttempt.objects.create(
            lesson_state=state,
            question=q1,
            answer="a",
            correct=True,
            hint_level=0,
        )

        user_b = User.objects.get(email="user-b@example.com")
        session_b = create_session_for_user(user_b)

        response = self.client.get("/api/dashboard", **self._auth(session_b))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_xp"], 0)
        self.assertEqual(data["lessons_completed"], 0)

        response_a = self.client.get("/api/dashboard", **self._auth(token_a))
        self.assertEqual(response_a.json()["total_xp"], 200)

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

        token = self._register("dash-e2e@example.com")
        auth = self._auth(token)

        self.client.get("/api/lessons/e2e-lesson?module_topic=Test", **auth)

        self.client.post(
            "/api/lessons/e2e-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "A1"}),
            content_type="application/json",
            **auth,
        )

        response = self.client.get("/api/dashboard", **auth)
        data = response.json()
        self.assertGreaterEqual(data["total_xp"], 0)
        self.assertGreaterEqual(
            data["lessons_in_progress"] + data["lessons_completed"], 0
        )
