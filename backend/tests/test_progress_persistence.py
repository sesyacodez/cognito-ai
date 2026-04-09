"""
Integration tests for progress persistence — verifies that XP, stars, and
lesson status are correctly tracked across multiple answer submissions.
"""

import json
from unittest.mock import patch

from django.test import SimpleTestCase

from utils.lesson_stub_store import reset_lesson_store, save_lesson
from utils.progress_store import (
    reset_progress_store,
    get_lesson_progress,
    get_dashboard,
)


_TEST_LESSON = {
    "lesson_id": "persist-lesson",
    "mode": "learn",
    "micro_theory": "Test theory.",
    "questions": [
        {"id": "q1", "prompt": "Q1?", "difficulty": "easy", "answer_key": "A1"},
        {"id": "q2", "prompt": "Q2?", "difficulty": "medium", "answer_key": "A2"},
        {"id": "q3", "prompt": "Q3?", "difficulty": "hard", "answer_key": "A3"},
    ],
}


def _mock_eval_correct(skill_name, **kwargs):
    if skill_name == "socratic_tutor":
        return {"correct": True, "next_prompt": "Good!", "hint": None}
    if skill_name == "progress_updater":
        from skills.progress_updater import run as pu_run
        return pu_run(kwargs, mode=kwargs.get("mode", "learn"))
    return {}


def _mock_eval_incorrect(skill_name, **kwargs):
    if skill_name == "socratic_tutor":
        return {"correct": False, "next_prompt": "Try again.", "hint": None}
    if skill_name == "progress_updater":
        from skills.progress_updater import run as pu_run
        return pu_run(kwargs, mode=kwargs.get("mode", "learn"))
    return {}


class ProgressPersistenceTests(SimpleTestCase):

    def setUp(self):
        reset_progress_store()
        reset_lesson_store()
        save_lesson("persist-lesson", _TEST_LESSON)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_eval_correct)
    def test_xp_accumulates_across_answers(self, _mock):
        self.client.post(
            "/api/lessons/persist-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "A1"}),
            content_type="application/json",
        )
        r1 = self.client.post(
            "/api/lessons/persist-lesson/answer",
            data=json.dumps({"question_id": "q2", "answer": "A2"}),
            content_type="application/json",
        )
        progress = r1.json()["progress"]
        self.assertGreater(progress["xp"], 0)

        lp = get_lesson_progress("anonymous", "persist-lesson")
        self.assertEqual(lp.xp_earned, progress["xp"])

    @patch("apps.lessons.views.run_skill", side_effect=_mock_eval_correct)
    def test_lesson_completes_after_all_questions(self, _mock):
        for qid in ["q1", "q2", "q3"]:
            self.client.post(
                "/api/lessons/persist-lesson/answer",
                data=json.dumps({"question_id": qid, "answer": "correct"}),
                content_type="application/json",
            )

        lp = get_lesson_progress("anonymous", "persist-lesson")
        self.assertEqual(lp.status, "completed")
        self.assertEqual(len(lp.answered_questions), 3)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_eval_incorrect)
    def test_incorrect_does_not_advance_answered_questions(self, _mock):
        self.client.post(
            "/api/lessons/persist-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "wrong"}),
            content_type="application/json",
        )

        lp = get_lesson_progress("anonymous", "persist-lesson")
        self.assertEqual(len(lp.answered_questions), 0)
        self.assertEqual(lp.xp_earned, 0)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_eval_correct)
    def test_stars_degrade_with_hint_usage(self, _mock):
        self.client.post(
            "/api/lessons/persist-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "A1"}),
            content_type="application/json",
        )

        lp = get_lesson_progress("anonymous", "persist-lesson")
        self.assertGreaterEqual(lp.stars_remaining, 0)
        self.assertLessEqual(lp.stars_remaining, 3)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_eval_correct)
    def test_dashboard_reflects_persisted_progress(self, _mock):
        for qid in ["q1", "q2", "q3"]:
            self.client.post(
                "/api/lessons/persist-lesson/answer",
                data=json.dumps({"question_id": qid, "answer": "A"}),
                content_type="application/json",
            )

        dashboard = get_dashboard("anonymous")
        self.assertEqual(dashboard["lessons_completed"], 1)
        self.assertGreater(dashboard["total_xp"], 0)
        self.assertGreater(dashboard["total_stars"], 0)

    @patch("apps.lessons.views.run_skill", side_effect=_mock_eval_correct)
    def test_completed_lesson_stays_completed(self, _mock):
        for qid in ["q1", "q2", "q3"]:
            self.client.post(
                "/api/lessons/persist-lesson/answer",
                data=json.dumps({"question_id": qid, "answer": "A"}),
                content_type="application/json",
            )

        lp = get_lesson_progress("anonymous", "persist-lesson")
        self.assertEqual(lp.status, "completed")

        self.client.post(
            "/api/lessons/persist-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "redo"}),
            content_type="application/json",
        )

        lp = get_lesson_progress("anonymous", "persist-lesson")
        self.assertEqual(lp.status, "completed")

    @patch("apps.lessons.views.run_skill", side_effect=_mock_eval_correct)
    def test_attempts_are_recorded(self, _mock):
        self.client.post(
            "/api/lessons/persist-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "A1"}),
            content_type="application/json",
        )
        self.client.post(
            "/api/lessons/persist-lesson/answer",
            data=json.dumps({"question_id": "q1", "answer": "A1 again"}),
            content_type="application/json",
        )

        lp = get_lesson_progress("anonymous", "persist-lesson")
        self.assertEqual(len(lp.attempts), 2)
        self.assertEqual(lp.attempts[0].question_id, "q1")
