import json
import unittest
from unittest.mock import MagicMock, patch


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_openrouter_response(evaluation: dict) -> MagicMock:
    """Build a mock httpx Response with a valid socratic_tutor tool-call reply."""
    tool_args = {"evaluation": evaluation}
    response_data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "socratic_tutor",
                                "arguments": json.dumps(tool_args),
                            }
                        }
                    ],
                }
            }
        ]
    }
    mock_resp = MagicMock()
    mock_resp.json.return_value = response_data
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def _correct_evaluation() -> dict:
    return {
        "correct": True,
        "next_prompt": "Excellent! Now how does this apply to asynchronous contexts?",
        "hint": None,
    }


def _incorrect_evaluation() -> dict:
    return {
        "correct": False,
        "next_prompt": "Think about what happens when the loop counter reaches zero. What does that imply?",
        "hint": None,
    }


def _hint_evaluation(hint_text: str) -> dict:
    return {
        "correct": False,
        "next_prompt": "Does that help clarify things?",
        "hint": hint_text,
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

class SocraticTutorSkillTests(unittest.TestCase):

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_correct_answer_returns_guiding_question(self, mock_post):
        """Correct answer → correct=True + follow-up Socratic question."""
        mock_post.return_value = _make_openrouter_response(_correct_evaluation())

        from agent.runner import run_skill
        result = run_skill(
            "socratic_tutor",
            mode="learn",
            student_answer="A loop iterates until the condition is false.",
            question_prompt="What does a loop do?",
            hint_level=0,
        )

        self.assertTrue(result["correct"])
        self.assertIn("next_prompt", result)
        self.assertGreater(len(result["next_prompt"]), 0)
        mock_post.assert_called_once()

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_incorrect_answer_returns_guiding_question_without_answer(self, mock_post):
        """Incorrect answer → correct=False + guiding question, NOT the direct answer."""
        mock_post.return_value = _make_openrouter_response(_incorrect_evaluation())

        from agent.runner import run_skill
        result = run_skill(
            "socratic_tutor",
            mode="learn",
            student_answer="A loop runs exactly twice.",
            question_prompt="What does a loop do?",
            hint_level=0,
        )

        self.assertFalse(result["correct"])
        self.assertIn("next_prompt", result)
        # The next_prompt should not contain nothing (must be a real question)
        self.assertGreater(len(result["next_prompt"]), 0)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_hint_level_1_returns_gentle_nudge(self, mock_post):
        """hint_level=1 → gentle nudge hint returned."""
        mock_post.return_value = _make_openrouter_response(
            _hint_evaluation("Think about what 'iteration' means.")
        )

        from agent.runner import run_skill
        result = run_skill(
            "socratic_tutor",
            mode="learn",
            student_answer="",
            question_prompt="What does a loop do?",
            hint_level=1,
        )

        self.assertIn("hint", result)
        self.assertIsNotNone(result["hint"])
        self.assertGreater(len(result["hint"]), 0)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_hint_level_3_returns_strong_hint(self, mock_post):
        """hint_level=3 → strong hint present, but not the final answer."""
        mock_post.return_value = _make_openrouter_response(
            _hint_evaluation("A loop runs a block of code repeatedly based on a condition.")
        )

        from agent.runner import run_skill
        result = run_skill(
            "socratic_tutor",
            mode="learn",
            student_answer="",
            question_prompt="What does a loop do? Expected: It repeats code while condition is true.",
            hint_level=3,
        )

        self.assertIn("hint", result)
        self.assertIsNotNone(result["hint"])

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_retry_on_first_bad_response(self, mock_post):
        """First call returns malformed; second call succeeds."""
        bad_response = MagicMock()
        bad_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "tool_calls": []}}]
        }
        bad_response.raise_for_status = MagicMock()

        good_response = _make_openrouter_response(_correct_evaluation())
        mock_post.side_effect = [bad_response, good_response]

        from agent.runner import run_skill
        result = run_skill(
            "socratic_tutor",
            mode="learn",
            student_answer="A loop repeats code.",
            question_prompt="What does a loop do?",
            hint_level=0,
        )

        self.assertIn("correct", result)
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_both_attempts_fail_raises_agent_error(self, mock_post):
        """Both calls return bad responses → AgentError raised."""
        bad_response = MagicMock()
        bad_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "tool_calls": []}}]
        }
        bad_response.raise_for_status = MagicMock()
        mock_post.return_value = bad_response

        from agent.runner import AgentError, run_skill
        with self.assertRaises(AgentError):
            run_skill(
                "socratic_tutor",
                mode="learn",
                student_answer="something",
                question_prompt="What is X?",
                hint_level=0,
            )
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key", "SOCRATIC_TUTOR_MODEL": "custom/tutor:free"})
    @patch("agent.runner.httpx.post")
    def test_uses_socratic_tutor_model_env_var(self, mock_post):
        """SOCRATIC_TUTOR_MODEL env var is passed to OpenRouter."""
        mock_post.return_value = _make_openrouter_response(_correct_evaluation())

        from agent.runner import run_skill
        run_skill(
            "socratic_tutor",
            mode="learn",
            student_answer="An answer.",
            question_prompt="A question?",
            hint_level=0,
        )

        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][1]
        self.assertEqual(payload["model"], "custom/tutor:free")


if __name__ == "__main__":
    unittest.main()
