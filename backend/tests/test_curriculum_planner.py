import unittest
from unittest.mock import patch

from agent.runner import AgentError
from apps.roadmaps.curriculum_services import plan_curriculum
from skills import curriculum_planner
from utils.validators import ValidationError


class CurriculumPlannerNormalizationTests(unittest.TestCase):
    def test_normalizes_valid_payload(self):
        result = curriculum_planner.run(
            {
                "curriculum": {
                    "topic": "Machine Learning",
                    "courses": [
                        {"id": "u-1", "title": "Linear Algebra", "outcome": "Vectors and matrices.", "order": 1},
                        {"id": "u-2", "title": "Probability", "outcome": "Reason about uncertainty.", "order": 2},
                        {"id": "u-3", "title": "Supervised Learning", "outcome": "Train and evaluate models.", "order": 3},
                    ],
                }
            }
        )
        self.assertEqual(result["topic"], "Machine Learning")
        self.assertEqual(len(result["courses"]), 3)
        self.assertEqual(result["courses"][0]["index"], 0)
        self.assertEqual(result["courses"][2]["index"], 2)

    def test_rejects_too_few_courses(self):
        with self.assertRaises(ValidationError):
            curriculum_planner.run(
                {
                    "curriculum": {
                        "topic": "Machine Learning",
                        "courses": [
                            {"id": "u-1", "title": "Only", "outcome": "Single.", "order": 1},
                        ],
                    }
                }
            )

    def test_rejects_too_many_courses(self):
        with self.assertRaises(ValidationError):
            curriculum_planner.run(
                {
                    "curriculum": {
                        "topic": "Mega Topic",
                        "courses": [
                            {"id": f"u-{i}", "title": f"Course {i}", "outcome": "x", "order": i + 1}
                            for i in range(7)
                        ],
                    }
                }
            )


class PlanCurriculumServiceTests(unittest.TestCase):
    @patch("apps.roadmaps.curriculum_services.run_skill")
    def test_uses_agent_when_available(self, mock_run_skill):
        mock_run_skill.return_value = {
            "topic": "Web Development",
            "mode": "learn",
            "courses": [
                {"id": "u-1", "title": "HTML", "outcome": "Layouts.", "index": 0},
                {"id": "u-2", "title": "CSS", "outcome": "Styling.", "index": 1},
                {"id": "u-3", "title": "JavaScript", "outcome": "Interactivity.", "index": 2},
            ],
        }
        plan = plan_curriculum("Web Development")
        self.assertEqual(plan["source"], "agent")
        self.assertEqual(len(plan["courses"]), 3)
        self.assertEqual(plan["topic"], "Web Development")

    @patch("apps.roadmaps.curriculum_services.run_skill", side_effect=AgentError("offline"))
    def test_falls_back_to_placeholder_on_agent_error(self, _mock_run_skill):
        plan = plan_curriculum("Web Development")
        self.assertEqual(plan["source"], "placeholder")
        self.assertGreaterEqual(len(plan["courses"]), 2)
        self.assertLessEqual(len(plan["courses"]), 6)


if __name__ == "__main__":
    unittest.main()
