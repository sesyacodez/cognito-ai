import unittest

from pydantic import ValidationError

from utils.validators import DecomposerOutput, normalize_decomposer_output


VALID_DECOMPOSER_OUTPUT = {
    "roadmap": {
        "topic": "Intro to SQL",
        "modules": [
            {"id": "m1", "title": "SQL Basics", "outcome": "Learn selects.", "order": 1},
            {"id": "m2", "title": "Filtering", "outcome": "Learn where.", "order": 2},
            {"id": "m3", "title": "Aggregations", "outcome": "Learn count.", "order": 3},
            {"id": "m4", "title": "Joins", "outcome": "Learn joins.", "order": 4},
            {"id": "m5", "title": "Practice", "outcome": "Apply skills.", "order": 5},
        ],
    }
}


class ValidatorTests(unittest.TestCase):
    def test_valid_output_and_normalization(self):
        parsed = DecomposerOutput.model_validate(VALID_DECOMPOSER_OUTPUT)
        self.assertEqual(len(parsed.roadmap.modules), 5)

        normalized = normalize_decomposer_output(VALID_DECOMPOSER_OUTPUT)
        indexes = [module["index"] for module in normalized["modules"]]
        self.assertEqual(indexes, [0, 1, 2, 3, 4])

    def test_rejects_four_modules(self):
        invalid = {
            "roadmap": {
                "topic": "Topic",
                "modules": VALID_DECOMPOSER_OUTPUT["roadmap"]["modules"][:4],
            }
        }
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(invalid)

    def test_rejects_six_modules(self):
        extra_module = {
            "id": "m6",
            "title": "Extra",
            "outcome": "Should fail.",
            "order": 6,
        }
        invalid = {
            "roadmap": {
                "topic": "Topic",
                "modules": VALID_DECOMPOSER_OUTPUT["roadmap"]["modules"] + [extra_module],
            }
        }
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(invalid)

    def test_rejects_duplicate_order(self):
        invalid = {
            "roadmap": {
                "topic": "Topic",
                "modules": [
                    {"id": "m1", "title": "A", "outcome": "A", "order": 1},
                    {"id": "m2", "title": "B", "outcome": "B", "order": 1},
                    {"id": "m3", "title": "C", "outcome": "C", "order": 3},
                    {"id": "m4", "title": "D", "outcome": "D", "order": 4},
                    {"id": "m5", "title": "E", "outcome": "E", "order": 5},
                ],
            }
        }
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(invalid)

    def test_rejects_empty_title(self):
        invalid = {
            "roadmap": {
                "topic": "Topic",
                "modules": [
                    {"id": "m1", "title": "", "outcome": "A", "order": 1},
                    {"id": "m2", "title": "B", "outcome": "B", "order": 2},
                    {"id": "m3", "title": "C", "outcome": "C", "order": 3},
                    {"id": "m4", "title": "D", "outcome": "D", "order": 4},
                    {"id": "m5", "title": "E", "outcome": "E", "order": 5},
                ],
            }
        }
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(invalid)


if __name__ == "__main__":
    unittest.main()
