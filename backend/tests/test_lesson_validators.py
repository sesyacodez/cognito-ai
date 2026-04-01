import unittest

from pydantic import ValidationError


class LessonValidatorTests(unittest.TestCase):

    # ── normalize_lesson_output ───────────────────────────────────────────────

    def test_valid_lesson_passes(self):
        """A correctly shaped lesson payload normalizes to the expected output shape."""
        from utils.validators import normalize_lesson_output
        data = {
            "lesson": {
                "micro_theory": "This is the theory explaining the concept clearly.",
                "questions": [
                    {"id": "q1", "prompt": "Easy question?", "difficulty": "easy", "answer_key": "Answer 1"},
                    {"id": "q2", "prompt": "Medium question?", "difficulty": "medium", "answer_key": "Answer 2"},
                    {"id": "q3", "prompt": "Hard question?", "difficulty": "hard", "answer_key": "Answer 3"},
                ],
            }
        }
        result = normalize_lesson_output(data, mode="learn")

        self.assertIn("lesson_id", result)
        self.assertEqual(result["mode"], "learn")
        self.assertEqual(result["micro_theory"], data["lesson"]["micro_theory"])
        self.assertEqual(len(result["questions"]), 3)

    def test_wrong_number_of_questions_rejected(self):
        """Fewer or more than 3 questions raises ValidationError."""
        from utils.validators import normalize_lesson_output
        data_two = {
            "lesson": {
                "micro_theory": "Theory here.",
                "questions": [
                    {"id": "q1", "prompt": "Q?", "difficulty": "easy", "answer_key": "A"},
                    {"id": "q2", "prompt": "Q?", "difficulty": "medium", "answer_key": "A"},
                ],
            }
        }
        with self.assertRaises(ValidationError):
            normalize_lesson_output(data_two)

        data_four = {
            "lesson": {
                "micro_theory": "Theory here.",
                "questions": [
                    {"id": f"q{i}", "prompt": "Q?", "difficulty": "easy", "answer_key": "A"}
                    for i in range(4)
                ],
            }
        }
        with self.assertRaises(ValidationError):
            normalize_lesson_output(data_four)

    def test_invalid_difficulty_rejected(self):
        """An invalid difficulty value (not easy/medium/hard) raises ValidationError."""
        from utils.validators import normalize_lesson_output
        data = {
            "lesson": {
                "micro_theory": "Theory here.",
                "questions": [
                    {"id": "q1", "prompt": "Q?", "difficulty": "beginner", "answer_key": "A"},
                    {"id": "q2", "prompt": "Q?", "difficulty": "medium", "answer_key": "A"},
                    {"id": "q3", "prompt": "Q?", "difficulty": "hard", "answer_key": "A"},
                ],
            }
        }
        with self.assertRaises(ValidationError):
            normalize_lesson_output(data)

    def test_empty_micro_theory_rejected(self):
        """An empty micro_theory string raises ValidationError."""
        from utils.validators import normalize_lesson_output
        data = {
            "lesson": {
                "micro_theory": "",
                "questions": [
                    {"id": "q1", "prompt": "Q?", "difficulty": "easy", "answer_key": "A"},
                    {"id": "q2", "prompt": "Q?", "difficulty": "medium", "answer_key": "A"},
                    {"id": "q3", "prompt": "Q?", "difficulty": "hard", "answer_key": "A"},
                ],
            }
        }
        with self.assertRaises(ValidationError):
            normalize_lesson_output(data)

    def test_missing_answer_key_rejected(self):
        """A question without answer_key raises ValidationError."""
        from utils.validators import normalize_lesson_output
        data = {
            "lesson": {
                "micro_theory": "Some theory.",
                "questions": [
                    {"id": "q1", "prompt": "Q?", "difficulty": "easy"},
                    {"id": "q2", "prompt": "Q?", "difficulty": "medium", "answer_key": "A"},
                    {"id": "q3", "prompt": "Q?", "difficulty": "hard", "answer_key": "A"},
                ],
            }
        }
        with self.assertRaises(ValidationError):
            normalize_lesson_output(data)

    def test_answer_key_present_in_output(self):
        """Normalized output includes answer_key for use in evaluation caching."""
        from utils.validators import normalize_lesson_output
        data = {
            "lesson": {
                "micro_theory": "Theory here.",
                "questions": [
                    {"id": "q1", "prompt": "Q?", "difficulty": "easy", "answer_key": "The real answer."},
                    {"id": "q2", "prompt": "Q?", "difficulty": "medium", "answer_key": "Another answer."},
                    {"id": "q3", "prompt": "Q?", "difficulty": "hard", "answer_key": "Complex answer."},
                ],
            }
        }
        result = normalize_lesson_output(data)
        # answer_key MUST be present in the normalized output (views strip it from GET responses)
        self.assertEqual(result["questions"][0]["answer_key"], "The real answer.")

    # ── normalize_evaluation_output ───────────────────────────────────────────

    def test_valid_evaluation_passes(self):
        """A correctly shaped evaluation normalizes successfully."""
        from utils.validators import normalize_evaluation_output
        data = {"correct": True, "next_prompt": "Now explain why this works."}
        result = normalize_evaluation_output(data)
        self.assertTrue(result["correct"])
        self.assertEqual(result["next_prompt"], "Now explain why this works.")

    def test_evaluation_with_hint_passes(self):
        """Evaluation with optional hint field normalizes successfully."""
        from utils.validators import normalize_evaluation_output
        data = {"correct": False, "next_prompt": "Think again.", "hint": "Consider the base case."}
        result = normalize_evaluation_output(data)
        self.assertEqual(result["hint"], "Consider the base case.")

    def test_evaluation_missing_next_prompt_rejected(self):
        """Evaluation without next_prompt raises ValidationError."""
        from utils.validators import normalize_evaluation_output
        with self.assertRaises(ValidationError):
            normalize_evaluation_output({"correct": True})

    def test_evaluation_missing_correct_rejected(self):
        """Evaluation without correct bool raises ValidationError."""
        from utils.validators import normalize_evaluation_output
        with self.assertRaises(ValidationError):
            normalize_evaluation_output({"next_prompt": "Think again."})


if __name__ == "__main__":
    unittest.main()
