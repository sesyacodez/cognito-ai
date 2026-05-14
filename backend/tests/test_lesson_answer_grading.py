"""
Lesson answer endpoint: deterministic correctness overrides model `correct` flag.
"""

import json
from unittest.mock import patch

from django.test import TestCase

from utils.lesson_stub_store import reset_lesson_store, save_lesson
from utils.progress_store import reset_progress_store


from agent.runner import AgentError


_GRADING_LESSON = {
    "lesson_id": "grading-lesson",
    "mode": "learn",
    "micro_theory": "Theory.",
    "questions": [
        {
            "id": "q-grade",
            "prompt": "What is the magic word?",
            "difficulty": "easy",
            "answer_key": "plugh",
        },
    ],
}


def _progress_side(skill_name, mode="learn", **kwargs):
    if skill_name == "progress_updater":
        from skills.progress_updater import run as pu_run

        return pu_run(kwargs, mode=kwargs.get("mode", "learn"))
    raise AssertionError(f"Unexpected skill: {skill_name}")


class LessonAnswerGradingPolicyTests(TestCase):
    def setUp(self):
        reset_lesson_store()
        reset_progress_store()
        save_lesson("grading-lesson", _GRADING_LESSON)

    @patch("apps.lessons.views.run_skill")
    def test_model_correct_true_but_key_mismatch_is_incorrect(self, mock_run):
        def side_effect(skill_name, mode="learn", **kwargs):
            if skill_name == "socratic_tutor":
                return {"correct": True, "next_prompt": "Great!", "hint": None}
            if skill_name == "progress_updater":
                return _progress_side(skill_name, mode=mode, **kwargs)
            raise AssertionError(skill_name)

        mock_run.side_effect = side_effect

        response = self.client.post(
            "/api/lessons/grading-lesson/answer",
            data=json.dumps({"question_id": "q-grade", "answer": "wrong answer"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["correct"])
        self.assertEqual(mock_run.call_count, 2)

    @patch("apps.lessons.views.run_skill")
    def test_model_correct_false_but_key_match_is_correct(self, mock_run):
        def side_effect(skill_name, mode="learn", **kwargs):
            if skill_name == "socratic_tutor":
                return {"correct": False, "next_prompt": "Try again.", "hint": None}
            if skill_name == "progress_updater":
                return _progress_side(skill_name, mode=mode, **kwargs)
            raise AssertionError(skill_name)

        mock_run.side_effect = side_effect

        response = self.client.post(
            "/api/lessons/grading-lesson/answer",
            data=json.dumps({"question_id": "q-grade", "answer": "plugh"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["correct"])
        self.assertEqual(response.json()["next_prompt"], "Try again.")

    @patch("apps.lessons.views.run_skill")
    def test_placeholder_uses_deterministic_when_tutor_raises_agent_error(self, mock_run):
        def side_effect(skill_name, mode="learn", **kwargs):
            if skill_name == "socratic_tutor":
                raise AgentError("no api")
            if skill_name == "progress_updater":
                return _progress_side(skill_name, mode=mode, **kwargs)
            raise AssertionError(skill_name)

        mock_run.side_effect = side_effect

        response = self.client.post(
            "/api/lessons/grading-lesson/answer",
            data=json.dumps({"question_id": "q-grade", "answer": "plugh"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["correct"])
        self.assertIn("Great job", body["next_prompt"])
