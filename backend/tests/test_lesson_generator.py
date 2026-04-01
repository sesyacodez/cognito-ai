import json
import unittest
from unittest.mock import MagicMock, patch


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_openrouter_response(lesson: dict, module_topic: str = "Test Topic") -> MagicMock:
    """Build a mock httpx Response that looks like a valid OpenRouter tool-call reply."""
    tool_args = {
        "module_topic": module_topic,
        "mode": "learn",
        "lesson": lesson,
    }
    response_data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "lesson_generator",
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


def _valid_lesson(topic: str = "Test Topic") -> dict:
    return {
        "micro_theory": f"This is a concise explanation of {topic}. It covers the essential concepts clearly.",
        "questions": [
            {
                "id": "q-easy-1",
                "prompt": f"What is the basic definition of {topic}?",
                "difficulty": "easy",
                "answer_key": "The basic definition.",
            },
            {
                "id": "q-medium-1",
                "prompt": f"Explain a key application of {topic}.",
                "difficulty": "medium",
                "answer_key": "It enables structured learning.",
            },
            {
                "id": "q-hard-1",
                "prompt": f"Describe how {topic} handles edge cases.",
                "difficulty": "hard",
                "answer_key": "By using fallback mechanisms.",
            },
        ],
    }


# ── Tests ─────────────────────────────────────────────────────────────────────

class LessonGeneratorSkillRunnerTests(unittest.TestCase):

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_happy_path_learn(self, mock_post):
        """Valid model response → normalized lesson with 3 questions."""
        mock_post.return_value = _make_openrouter_response(_valid_lesson())

        from agent.runner import run_skill
        result = run_skill("lesson_generator", mode="learn", module_topic="Python Variables")

        self.assertIn("lesson_id", result)
        self.assertEqual(result["mode"], "learn")
        self.assertEqual(len(result["questions"]), 3)
        difficulties = {q["difficulty"] for q in result["questions"]}
        self.assertEqual(difficulties, {"easy", "medium", "hard"})
        mock_post.assert_called_once()

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_happy_path_solve_mode(self, mock_post):
        """Solve mode → theory framed as problem brief, questions as tasks."""
        solve_lesson = {
            "micro_theory": "Your task is to build a REST API endpoint that returns JSON data.",
            "questions": [
                {
                    "id": "q1",
                    "prompt": "Set up a basic Flask server with a /health endpoint.",
                    "difficulty": "easy",
                    "answer_key": "Flask app running with /health returning 200.",
                },
                {
                    "id": "q2",
                    "prompt": "Add a /data endpoint returning a list of records.",
                    "difficulty": "medium",
                    "answer_key": "Endpoint returns JSON list of dicts.",
                },
                {
                    "id": "q3",
                    "prompt": "Add pagination support: ?page= and ?limit= query params.",
                    "difficulty": "hard",
                    "answer_key": "Paginated response with total and items.",
                },
            ],
        }
        mock_post.return_value = _make_openrouter_response(solve_lesson, "Build a REST API")

        from agent.runner import run_skill
        result = run_skill("lesson_generator", mode="solve", module_topic="Build a REST API")

        self.assertEqual(result["mode"], "solve")
        self.assertEqual(len(result["questions"]), 3)
        mock_post.assert_called_once()

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_retry_on_first_bad_response(self, mock_post):
        """First call returns empty tool_calls; second call succeeds → result returned."""
        bad_response = MagicMock()
        bad_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "tool_calls": []}}]
        }
        bad_response.raise_for_status = MagicMock()

        good_response = _make_openrouter_response(_valid_lesson())
        mock_post.side_effect = [bad_response, good_response]

        from agent.runner import run_skill
        result = run_skill("lesson_generator", mode="learn", module_topic="Python")

        self.assertIn("lesson_id", result)
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_both_attempts_fail_raises_agent_error(self, mock_post):
        """Both calls return bad tool_calls → AgentError raised."""
        bad_response = MagicMock()
        bad_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "tool_calls": []}}]
        }
        bad_response.raise_for_status = MagicMock()
        mock_post.return_value = bad_response

        from agent.runner import AgentError, run_skill
        with self.assertRaises(AgentError):
            run_skill("lesson_generator", mode="learn", module_topic="Python")
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": ""})
    @patch("agent.runner.httpx.post")
    def test_missing_api_key_raises_agent_error_immediately(self, mock_post):
        """If OPENROUTER_API_KEY is not set, AgentError is raised before any network call."""
        from agent.runner import AgentError, run_skill
        with self.assertRaises(AgentError):
            run_skill("lesson_generator", mode="learn", module_topic="Python")
        mock_post.assert_not_called()

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key", "LESSON_GENERATOR_MODEL": "custom/model:free"})
    @patch("agent.runner.httpx.post")
    def test_uses_lesson_generator_model_env_var(self, mock_post):
        """LESSON_GENERATOR_MODEL env var is used instead of DECOMPOSER_MODEL."""
        mock_post.return_value = _make_openrouter_response(_valid_lesson())

        from agent.runner import run_skill
        run_skill("lesson_generator", mode="learn", module_topic="Python")

        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][1]
        self.assertEqual(payload["model"], "custom/model:free")


if __name__ == "__main__":
    unittest.main()
