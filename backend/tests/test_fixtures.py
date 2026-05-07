import unittest

from utils.fixtures import get_adaptive_placeholder_roadmap, get_placeholder_roadmap
from utils.roadmap_complexity import estimate_module_count


class FixtureTests(unittest.TestCase):
    def test_placeholder_has_five_modules(self):
        response = get_placeholder_roadmap("Linear Algebra")
        self.assertEqual(len(response["modules"]), 5)

    def test_placeholder_indexes_are_zero_to_four(self):
        response = get_placeholder_roadmap("Linear Algebra")
        indexes = [module["index"] for module in response["modules"]]
        self.assertEqual(indexes, [0, 1, 2, 3, 4])

    def test_placeholder_has_roadmap_id(self):
        response = get_placeholder_roadmap("Linear Algebra")
        self.assertTrue(response["roadmap_id"])
        self.assertIn("placeholder-", response["roadmap_id"])

    def test_placeholder_shape_matches_contract(self):
        response = get_placeholder_roadmap("Linear Algebra")
        self.assertIn("roadmap_id", response)
        self.assertIn("mode", response)
        self.assertIn("modules", response)
        for module in response["modules"]:
            self.assertIn("id", module)
            self.assertIn("title", module)
            self.assertIn("index", module)
            self.assertIn("outcome", module)

    def test_placeholder_topic_used_in_titles(self):
        response = get_placeholder_roadmap("Python Basics")
        for module in response["modules"]:
            self.assertIn("Python Basics", module["title"])

    def test_adaptive_placeholder_uses_one_module_for_atomic_python_method(self):
        response = get_adaptive_placeholder_roadmap("split str method in python")
        self.assertEqual(len(response["modules"]), 1)

    def test_estimate_module_count_keeps_atomic_python_method_short(self):
        self.assertEqual(estimate_module_count("split str method in python"), 1)

    def test_estimate_module_count_allows_broad_topics_to_expand(self):
        self.assertEqual(estimate_module_count("complete machine learning roadmap"), 6)


if __name__ == "__main__":
    unittest.main()
