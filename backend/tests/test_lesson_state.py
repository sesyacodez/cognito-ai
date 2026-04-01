import unittest


class LessonStateTests(unittest.TestCase):

    # ── calculate_xp ─────────────────────────────────────────────────────────

    def test_xp_correct_no_hints(self):
        """Correct answer with no hints → full 100 XP."""
        from utils.lesson_state import calculate_xp
        self.assertEqual(calculate_xp(correct=True, hint_level=0), 100)

    def test_xp_correct_hint_level_1(self):
        """Correct with hint level 1 → 75 XP."""
        from utils.lesson_state import calculate_xp
        self.assertEqual(calculate_xp(correct=True, hint_level=1), 75)

    def test_xp_correct_hint_level_2(self):
        """Correct with hint level 2 → 50 XP."""
        from utils.lesson_state import calculate_xp
        self.assertEqual(calculate_xp(correct=True, hint_level=2), 50)

    def test_xp_correct_hint_level_3(self):
        """Correct with hint level 3 → 25 XP."""
        from utils.lesson_state import calculate_xp
        self.assertEqual(calculate_xp(correct=True, hint_level=3), 25)

    def test_xp_incorrect_always_zero(self):
        """Any incorrect answer → 0 XP regardless of hint level."""
        from utils.lesson_state import calculate_xp
        for hint_level in range(4):
            with self.subTest(hint_level=hint_level):
                self.assertEqual(calculate_xp(correct=False, hint_level=hint_level), 0)

    # ── calculate_stars ───────────────────────────────────────────────────────

    def test_stars_no_hints_full(self):
        """No hints used → 3 stars."""
        from utils.lesson_state import calculate_stars
        self.assertEqual(calculate_stars(hint_usage=0), 3)

    def test_stars_one_hint_deducted(self):
        """One hint → 2 stars remaining."""
        from utils.lesson_state import calculate_stars
        self.assertEqual(calculate_stars(hint_usage=1), 2)

    def test_stars_two_hints_deducted(self):
        """Two hints → 1 star remaining."""
        from utils.lesson_state import calculate_stars
        self.assertEqual(calculate_stars(hint_usage=2), 1)

    def test_stars_three_hints_zero(self):
        """Three hints → 0 stars remaining."""
        from utils.lesson_state import calculate_stars
        self.assertEqual(calculate_stars(hint_usage=3), 0)

    def test_stars_never_negative(self):
        """Stars can never drop below 0."""
        from utils.lesson_state import calculate_stars
        self.assertEqual(calculate_stars(hint_usage=10), 0)

    # ── transition_status ─────────────────────────────────────────────────────

    def test_status_not_started_at_zero(self):
        """0 questions answered → not_started."""
        from utils.lesson_state import transition_status
        self.assertEqual(transition_status("not_started", 0, 3), "not_started")

    def test_status_in_progress(self):
        """1 or 2 of 3 questions answered → in_progress."""
        from utils.lesson_state import transition_status
        self.assertEqual(transition_status("not_started", 1, 3), "in_progress")
        self.assertEqual(transition_status("in_progress", 2, 3), "in_progress")

    def test_status_completed(self):
        """All 3 questions answered → completed."""
        from utils.lesson_state import transition_status
        self.assertEqual(transition_status("in_progress", 3, 3), "completed")

    def test_status_completed_with_single_question(self):
        """Single-question lesson → completed when 1 is answered."""
        from utils.lesson_state import transition_status
        self.assertEqual(transition_status("in_progress", 1, 1), "completed")

    # ── evaluate_answer_local ─────────────────────────────────────────────────

    def test_local_eval_exact_match(self):
        """Exact match (case-insensitive) → True."""
        from utils.lesson_state import evaluate_answer_local
        self.assertTrue(evaluate_answer_local("The answer is here.", "the answer is here."))

    def test_local_eval_key_in_answer(self):
        """Answer_key substring found in student_answer → True."""
        from utils.lesson_state import evaluate_answer_local
        self.assertTrue(evaluate_answer_local(
            "I believe the answer is related to iteration and loops.",
            "iteration"
        ))

    def test_local_eval_empty_answer(self):
        """Empty student answer → False."""
        from utils.lesson_state import evaluate_answer_local
        self.assertFalse(evaluate_answer_local("", "something"))


if __name__ == "__main__":
    unittest.main()
