import unittest

from utils.lesson_state import (
    calculate_xp,
    calculate_stars,
    transition_status,
    evaluate_answer_local,
    validate_transition,
    safe_transition_status,
    InvalidTransitionError,
    VALID_TRANSITIONS,
)


class LessonStateTests(unittest.TestCase):

    # ── calculate_xp ─────────────────────────────────────────────────────────

    def test_xp_correct_no_hints(self):
        self.assertEqual(calculate_xp(correct=True, hint_level=0), 100)

    def test_xp_correct_hint_level_1(self):
        self.assertEqual(calculate_xp(correct=True, hint_level=1), 75)

    def test_xp_correct_hint_level_2(self):
        self.assertEqual(calculate_xp(correct=True, hint_level=2), 50)

    def test_xp_correct_hint_level_3(self):
        self.assertEqual(calculate_xp(correct=True, hint_level=3), 25)

    def test_xp_incorrect_always_zero(self):
        for hint_level in range(4):
            with self.subTest(hint_level=hint_level):
                self.assertEqual(calculate_xp(correct=False, hint_level=hint_level), 0)

    # ── calculate_stars ───────────────────────────────────────────────────────

    def test_stars_no_hints_full(self):
        self.assertEqual(calculate_stars(hint_usage=0), 3)

    def test_stars_one_hint_deducted(self):
        self.assertEqual(calculate_stars(hint_usage=1), 2)

    def test_stars_two_hints_deducted(self):
        self.assertEqual(calculate_stars(hint_usage=2), 1)

    def test_stars_three_hints_zero(self):
        self.assertEqual(calculate_stars(hint_usage=3), 0)

    def test_stars_never_negative(self):
        self.assertEqual(calculate_stars(hint_usage=10), 0)

    # ── transition_status ─────────────────────────────────────────────────────

    def test_status_not_started_at_zero(self):
        self.assertEqual(transition_status("not_started", 0, 3), "not_started")

    def test_status_in_progress(self):
        self.assertEqual(transition_status("not_started", 1, 3), "in_progress")
        self.assertEqual(transition_status("in_progress", 2, 3), "in_progress")

    def test_status_completed(self):
        self.assertEqual(transition_status("in_progress", 3, 3), "completed")

    def test_status_completed_with_single_question(self):
        self.assertEqual(transition_status("in_progress", 1, 1), "completed")

    # ── validate_transition (safety checks) ───────────────────────────────────

    def test_valid_not_started_to_in_progress(self):
        validate_transition("not_started", "in_progress")

    def test_valid_not_started_to_completed(self):
        validate_transition("not_started", "completed")

    def test_valid_in_progress_to_completed(self):
        validate_transition("in_progress", "completed")

    def test_valid_in_progress_stays(self):
        validate_transition("in_progress", "in_progress")

    def test_valid_completed_stays(self):
        validate_transition("completed", "completed")

    def test_invalid_completed_to_in_progress(self):
        with self.assertRaises(InvalidTransitionError):
            validate_transition("completed", "in_progress")

    def test_invalid_completed_to_not_started(self):
        with self.assertRaises(InvalidTransitionError):
            validate_transition("completed", "not_started")

    def test_invalid_in_progress_to_not_started(self):
        with self.assertRaises(InvalidTransitionError):
            validate_transition("in_progress", "not_started")

    # ── safe_transition_status ────────────────────────────────────────────────

    def test_safe_transition_normal_flow(self):
        self.assertEqual(safe_transition_status("not_started", 1, 3), "in_progress")
        self.assertEqual(safe_transition_status("in_progress", 3, 3), "completed")

    def test_safe_transition_blocks_regression(self):
        self.assertEqual(safe_transition_status("completed", 0, 3), "completed")

    def test_safe_transition_single_question_lesson(self):
        self.assertEqual(safe_transition_status("not_started", 1, 1), "completed")

    # ── evaluate_answer_local ─────────────────────────────────────────────────

    def test_local_eval_exact_match(self):
        self.assertTrue(evaluate_answer_local("The answer is here.", "the answer is here."))

    def test_local_eval_key_in_answer(self):
        self.assertTrue(evaluate_answer_local(
            "I believe the answer is related to iteration and loops.",
            "iteration"
        ))

    def test_local_eval_empty_answer(self):
        self.assertFalse(evaluate_answer_local("", "something"))


if __name__ == "__main__":
    unittest.main()
