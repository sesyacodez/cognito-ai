"""Unit tests for deterministic answer grading."""

import unittest

from utils.answer_grading import is_answer_correct_against_key


class AnswerGradingTests(unittest.TestCase):
    def test_exact_match_case_insensitive(self):
        self.assertTrue(is_answer_correct_against_key("  Answer ONE  ", "answer one"))

    def test_substring_student_contains_key(self):
        self.assertTrue(
            is_answer_correct_against_key(
                "The answer is recursion because it calls itself",
                "recursion",
            )
        )

    def test_empty_student_false(self):
        self.assertFalse(is_answer_correct_against_key("", "anything"))
        self.assertFalse(is_answer_correct_against_key("   ", "x"))

    def test_empty_key_false(self):
        self.assertFalse(is_answer_correct_against_key("hello", ""))
        self.assertFalse(is_answer_correct_against_key("hello", "   "))

    def test_pipe_alternatives(self):
        self.assertTrue(is_answer_correct_against_key("y", "yes|y|true"))
        self.assertTrue(is_answer_correct_against_key("TRUE", "yes|y|true"))
        self.assertFalse(is_answer_correct_against_key("no", "yes|y|true"))

    def test_wrong_answer(self):
        self.assertFalse(is_answer_correct_against_key("completely off", "expected phrase"))


if __name__ == "__main__":
    unittest.main()
