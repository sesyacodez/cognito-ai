import unittest

from utils.roadmap_complexity import (
    estimate_module_count,
    is_broad_topic,
    trim_modules_to_estimated_count,
)


class EstimateModuleCountTests(unittest.TestCase):
    def test_atomic_method_returns_one(self):
        self.assertEqual(estimate_module_count("split str method in python"), 1)
        self.assertEqual(estimate_module_count("len function"), 1)

    def test_narrow_topic_stays_small(self):
        self.assertEqual(estimate_module_count("python loops"), 3)

    def test_broad_topic_grows(self):
        self.assertEqual(estimate_module_count("complete machine learning roadmap"), 6)

    def test_solve_mode_is_independent(self):
        self.assertEqual(estimate_module_count("Build a CLI", mode="solve"), 1)
        self.assertEqual(
            estimate_module_count(
                "Build a distributed task queue with retries and metrics handlers",
                mode="solve",
            ),
            3,
        )
        self.assertEqual(
            estimate_module_count(
                "Build a distributed task queue with retries metrics dashboards CI integration tests",
                mode="solve",
            ),
            5,
        )


class IsBroadTopicTests(unittest.TestCase):
    def test_known_broad_domains_are_broad(self):
        self.assertTrue(is_broad_topic("machine learning"))
        self.assertTrue(is_broad_topic("Web Development"))
        self.assertTrue(is_broad_topic("learn data science"))

    def test_atomic_topic_is_not_broad(self):
        self.assertFalse(is_broad_topic("split str method in python"))
        self.assertFalse(is_broad_topic("python len function"))

    def test_narrow_topic_is_not_broad(self):
        self.assertFalse(is_broad_topic("python loops"))
        self.assertFalse(is_broad_topic("intro to sql"))

    def test_broad_term_with_scope_is_broad(self):
        self.assertTrue(is_broad_topic("complete python curriculum"))
        self.assertTrue(is_broad_topic("comprehensive devops fundamentals"))

    def test_solve_mode_never_broad(self):
        self.assertFalse(is_broad_topic("machine learning", mode="solve"))
        self.assertFalse(is_broad_topic("complete devops curriculum", mode="solve"))

    def test_empty_topic_is_not_broad(self):
        self.assertFalse(is_broad_topic(""))
        self.assertFalse(is_broad_topic("   "))


class TrimModulesTests(unittest.TestCase):
    def test_trims_atomic_topic_to_one_module(self):
        modules = [{"index": i} for i in range(5)]
        trimmed = trim_modules_to_estimated_count(modules, "split str method in python")
        self.assertEqual(len(trimmed), 1)

    def test_keeps_modules_within_estimate(self):
        modules = [{"index": i} for i in range(3)]
        trimmed = trim_modules_to_estimated_count(modules, "complete machine learning roadmap")
        self.assertEqual(len(trimmed), 3)


if __name__ == "__main__":
    unittest.main()
