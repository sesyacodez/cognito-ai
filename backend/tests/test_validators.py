import unittest

from pydantic import ValidationError

from utils.validators import DecomposerOutput, normalize_decomposer_output


def _make_modules(count: int, start_order: int = 1) -> list:
    return [
        {
            "id": f"m{i}",
            "title": f"Module {i}",
            "outcome": f"Outcome {i}.",
            "order": i,
        }
        for i in range(start_order, start_order + count)
    ]


def _make_payload(count: int) -> dict:
    return {"roadmap": {"topic": "Test Topic", "modules": _make_modules(count)}}


class ValidatorFlexibleCountTests(unittest.TestCase):
    def test_one_module_passes(self):
        parsed = DecomposerOutput.model_validate(_make_payload(1))
        self.assertEqual(len(parsed.roadmap.modules), 1)

    def test_three_modules_pass(self):
        parsed = DecomposerOutput.model_validate(_make_payload(3))
        self.assertEqual(len(parsed.roadmap.modules), 3)

    def test_seven_modules_pass(self):
        parsed = DecomposerOutput.model_validate(_make_payload(7))
        self.assertEqual(len(parsed.roadmap.modules), 7)

    def test_zero_modules_fail(self):
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(_make_payload(0))

    def test_eight_modules_fail(self):
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(_make_payload(8))

    def test_rejects_duplicate_order(self):
        modules = _make_modules(3)
        modules[1]["order"] = 1  # duplicate
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(
                {"roadmap": {"topic": "T", "modules": modules}}
            )

    def test_rejects_non_sequential_order(self):
        modules = [
            {"id": "m1", "title": "A", "outcome": "A", "order": 1},
            {"id": "m2", "title": "B", "outcome": "B", "order": 3},  # gap
        ]
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(
                {"roadmap": {"topic": "T", "modules": modules}}
            )

    def test_rejects_empty_title(self):
        modules = _make_modules(2)
        modules[0]["title"] = ""
        with self.assertRaises(ValidationError):
            DecomposerOutput.model_validate(
                {"roadmap": {"topic": "T", "modules": modules}}
            )


class NormalizeDecomposerOutputTests(unittest.TestCase):
    def test_normalization_learn_mode(self):
        result = normalize_decomposer_output(_make_payload(3), mode="learn")
        self.assertIn("roadmap_id", result)
        self.assertEqual(result["mode"], "learn")
        self.assertEqual(len(result["modules"]), 3)
        self.assertEqual([m["index"] for m in result["modules"]], [0, 1, 2])
        # Each module should include outcome
        for mod in result["modules"]:
            self.assertIn("outcome", mod)

    def test_normalization_solve_mode(self):
        result = normalize_decomposer_output(_make_payload(1), mode="solve")
        self.assertEqual(result["mode"], "solve")
        self.assertEqual(len(result["modules"]), 1)
        self.assertEqual(result["modules"][0]["index"], 0)

    def test_roadmap_id_is_uuid4(self):
        import uuid
        result = normalize_decomposer_output(_make_payload(2))
        # Should not raise
        parsed = uuid.UUID(result["roadmap_id"], version=4)
        self.assertEqual(parsed.version, 4)

    def test_modules_sorted_by_order(self):
        # Provide modules in reverse order; normalization should sort them
        payload = {
            "roadmap": {
                "topic": "T",
                "modules": [
                    {"id": "m3", "title": "C", "outcome": "C", "order": 3},
                    {"id": "m1", "title": "A", "outcome": "A", "order": 1},
                    {"id": "m2", "title": "B", "outcome": "B", "order": 2},
                ],
            }
        }
        result = normalize_decomposer_output(payload)
        self.assertEqual([m["index"] for m in result["modules"]], [0, 1, 2])
        self.assertEqual([m["title"] for m in result["modules"]], ["A", "B", "C"])


if __name__ == "__main__":
    unittest.main()
