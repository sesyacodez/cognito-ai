import json
import unittest
from unittest.mock import MagicMock, patch


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_openrouter_response(modules: list, topic: str = "Test Topic") -> MagicMock:
    """Build a mock httpx Response that looks like a valid OpenRouter tool-call reply."""
    tool_args = {
        "topic": topic,
        "mode": "learn",
        "roadmap": {
            "topic": topic,
            "modules": modules,
        },
    }
    response_data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "decomposer",
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


def _three_modules(topic: str = "Test Topic") -> list:
    return [
        {"id": f"uuid-{i}", "title": f"Module {i}", "outcome": f"Outcome {i}", "order": i}
        for i in range(1, 4)
    ]


def _one_module(topic: str = "Build a REST API") -> list:
    return [
        {"id": "uuid-1", "title": "Build the API", "outcome": "Working REST API", "order": 1}
    ]


# ── Tests ─────────────────────────────────────────────────────────────────────

class DecomposerSkillRunnerTests(unittest.TestCase):

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_happy_path_learn(self, mock_post):
        """Valid model response → normalized dict with UUID4 roadmap_id and 3 modules."""
        mock_post.return_value = _make_openrouter_response(_three_modules())

        from agent.runner import run_skill
        result = run_skill("decomposer", mode="learn", topic="Intro to Python")

        self.assertIn("roadmap_id", result)
        self.assertEqual(result["mode"], "learn")
        self.assertEqual(len(result["modules"]), 3)
        self.assertEqual([m["index"] for m in result["modules"]], [0, 1, 2])
        mock_post.assert_called_once()

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_happy_path_solve_single_module(self, mock_post):
        """Simple problem → solve mode → 1 module normalized."""
        resp_data = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "function": {
                                    "name": "decomposer",
                                    "arguments": json.dumps({
                                        "topic": "Build a REST API",
                                        "mode": "solve",
                                        "roadmap": {
                                            "topic": "Build a REST API",
                                            "modules": _one_module(),
                                        },
                                    }),
                                }
                            }
                        ],
                    }
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = resp_data
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        from agent.runner import run_skill
        result = run_skill("decomposer", mode="solve", topic="Build a REST API")

        self.assertEqual(len(result["modules"]), 1)
        self.assertEqual(result["mode"], "solve")
        self.assertEqual(result["modules"][0]["index"], 0)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"})
    @patch("agent.runner.httpx.post")
    def test_retry_on_first_bad_json(self, mock_post):
        """First call returns empty tool_calls; second call succeeds → result returned."""
        bad_response = MagicMock()
        bad_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "tool_calls": []}}]
        }
        bad_response.raise_for_status = MagicMock()

        good_response = _make_openrouter_response(_three_modules())
        mock_post.side_effect = [bad_response, good_response]

        from agent.runner import run_skill
        result = run_skill("decomposer", mode="learn", topic="Python")

        self.assertIn("roadmap_id", result)
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
            run_skill("decomposer", mode="learn", topic="Python")
        self.assertEqual(mock_post.call_count, 2)

    @patch.dict("os.environ", {"OPENROUTER_API_KEY": ""})
    @patch("agent.runner.httpx.post")
    def test_missing_api_key_raises_agent_error_immediately(self, mock_post):
        """If OPENROUTER_API_KEY is not set, AgentError is raised before any network call."""
        from agent.runner import AgentError, run_skill

        with self.assertRaises(AgentError):
            run_skill("decomposer", mode="learn", topic="Python")
        mock_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
