import unittest

from skills.progress_updater import (
    run,
    _compute_xp,
    _compute_stars,
    _next_status,
    VALID_TRANSITIONS,
    BASE_XP,
    SPEED_BONUS_XP,
    SPEED_BONUS_THRESHOLD,
)


class ComputeXpTests(unittest.TestCase):

    def test_correct_no_hints_no_bonus(self):
        self.assertEqual(_compute_xp(True, 0, 60), BASE_XP)

    def test_correct_no_hints_with_speed_bonus(self):
        self.assertEqual(_compute_xp(True, 0, 20), BASE_XP + SPEED_BONUS_XP)

    def test_correct_one_hint(self):
        self.assertEqual(_compute_xp(True, 1, 60), 75)

    def test_correct_two_hints(self):
        self.assertEqual(_compute_xp(True, 2, 60), 50)

    def test_correct_three_hints(self):
        self.assertEqual(_compute_xp(True, 3, 60), 25)

    def test_correct_four_hints_clamps_to_min(self):
        self.assertEqual(_compute_xp(True, 4, 60), 10)

    def test_incorrect_always_zero(self):
        for hints in range(5):
            self.assertEqual(_compute_xp(False, hints, 10), 0)

    def test_speed_bonus_at_threshold(self):
        self.assertEqual(_compute_xp(True, 0, SPEED_BONUS_THRESHOLD), BASE_XP + SPEED_BONUS_XP)

    def test_no_speed_bonus_above_threshold(self):
        self.assertEqual(_compute_xp(True, 0, SPEED_BONUS_THRESHOLD + 1), BASE_XP)

    def test_zero_timing_no_speed_bonus(self):
        self.assertEqual(_compute_xp(True, 0, 0), BASE_XP)


class ComputeStarsTests(unittest.TestCase):

    def test_no_hints_full_stars(self):
        self.assertEqual(_compute_stars(0), 3)

    def test_one_hint(self):
        self.assertEqual(_compute_stars(1), 2)

    def test_three_hints_zero_stars(self):
        self.assertEqual(_compute_stars(3), 0)

    def test_never_negative(self):
        self.assertEqual(_compute_stars(10), 0)


class NextStatusTests(unittest.TestCase):

    def test_not_started_to_in_progress(self):
        self.assertEqual(_next_status("not_started", 1, 3), "in_progress")

    def test_not_started_to_completed_single_question(self):
        self.assertEqual(_next_status("not_started", 1, 1), "completed")

    def test_in_progress_stays_in_progress(self):
        self.assertEqual(_next_status("in_progress", 2, 3), "in_progress")

    def test_in_progress_to_completed(self):
        self.assertEqual(_next_status("in_progress", 3, 3), "completed")

    def test_completed_stays_completed(self):
        self.assertEqual(_next_status("completed", 3, 3), "completed")

    def test_zero_answered_preserves_current(self):
        self.assertEqual(_next_status("not_started", 0, 3), "not_started")


class RunIntegrationTests(unittest.TestCase):

    def test_correct_answer_basic(self):
        result = run({
            "correctness": True,
            "hint_usage": 0,
            "timing_seconds": 60,
            "current_xp": 0,
            "current_status": "not_started",
            "answered_count": 1,
            "total_questions": 3,
        })
        self.assertEqual(result["xp_earned"], BASE_XP)
        self.assertEqual(result["total_xp"], BASE_XP)
        self.assertEqual(result["stars_remaining"], 3)
        self.assertEqual(result["status"], "in_progress")
        self.assertTrue(result["correctness"])

    def test_incorrect_answer(self):
        result = run({
            "correctness": False,
            "hint_usage": 0,
            "timing_seconds": 45,
            "current_xp": 100,
            "current_status": "in_progress",
            "answered_count": 1,
            "total_questions": 3,
        })
        self.assertEqual(result["xp_earned"], 0)
        self.assertEqual(result["total_xp"], 100)
        self.assertFalse(result["correctness"])

    def test_cumulative_xp(self):
        result = run({
            "correctness": True,
            "hint_usage": 1,
            "timing_seconds": 20,
            "current_xp": 200,
            "current_status": "in_progress",
            "answered_count": 3,
            "total_questions": 3,
        })
        expected_xp = 75 + SPEED_BONUS_XP
        self.assertEqual(result["xp_earned"], expected_xp)
        self.assertEqual(result["total_xp"], 200 + expected_xp)
        self.assertEqual(result["status"], "completed")

    def test_validation_rejects_bad_status(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            run({
                "correctness": True,
                "hint_usage": 0,
                "timing_seconds": 10,
                "current_xp": 0,
                "current_status": "banana",
                "answered_count": 1,
                "total_questions": 3,
            })


if __name__ == "__main__":
    unittest.main()
