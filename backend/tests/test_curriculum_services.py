from unittest.mock import patch

from django.test import TestCase

from apps.roadmaps.curriculum_services import (
    create_curriculum_for_user,
    expand_course,
    serialize_curriculum,
)
from apps.roadmaps.models import Curriculum, CurriculumCourse
from apps.users.models import User


def _create_user(email: str = "curr-user@example.com") -> User:
    return User.objects.create_password_user(email=email, password="pw-12345", name="Curr User")


class CreateCurriculumForUserTests(TestCase):
    def setUp(self):
        self.user = _create_user()
        self.courses = [
            {"index": 0, "title": "Linear Algebra", "outcome": "Vectors and matrices."},
            {"index": 1, "title": "Probability", "outcome": "Reason about uncertainty."},
            {"index": 2, "title": "Supervised Learning", "outcome": "Train models."},
        ]

    def test_persists_curriculum_and_courses(self):
        curriculum = create_curriculum_for_user(
            self.user,
            topic="Machine Learning",
            mode="learn",
            courses=self.courses,
        )
        self.assertIsInstance(curriculum, Curriculum)
        self.assertEqual(curriculum.topic, "Machine Learning")
        self.assertEqual(curriculum.courses.count(), 3)
        first = curriculum.courses.order_by("index").first()
        self.assertIsNotNone(first.roadmap_id)

    def test_rejects_empty_course_list(self):
        with self.assertRaises(ValueError):
            create_curriculum_for_user(self.user, topic="Topic", mode="learn", courses=[])


class ExpandCourseTests(TestCase):
    def setUp(self):
        self.user = _create_user()
        self.curriculum = create_curriculum_for_user(
            self.user,
            topic="Data Science",
            mode="learn",
            courses=[
                {"index": 0, "title": "Pandas", "outcome": "Wrangle tabular data."},
                {"index": 1, "title": "Visualization", "outcome": "Communicate findings."},
            ],
        )

    def test_expand_is_idempotent(self):
        course = self.curriculum.courses.order_by("index").last()
        first = expand_course(course, user=self.user)
        first_id = first.id

        course.refresh_from_db()
        second = expand_course(course, user=self.user)
        self.assertEqual(second.id, first_id)


class SerializeCurriculumTests(TestCase):
    def setUp(self):
        self.user = _create_user()
        self.curriculum = create_curriculum_for_user(
            self.user,
            topic="Web Development",
            mode="learn",
            courses=[
                {"index": 0, "title": "HTML", "outcome": "Layouts."},
                {"index": 1, "title": "CSS", "outcome": "Styling."},
            ],
        )

    def test_serialization_includes_rollup_fields(self):
        data = serialize_curriculum(self.curriculum, module_progress={})
        self.assertIn("course_count", data)
        self.assertIn("completed_courses", data)
        self.assertIn("module_count", data)
        self.assertEqual(data["course_count"], 2)
        self.assertEqual(data["completed_courses"], 0)
        for course in data["courses"]:
            self.assertIn("status", course)
            self.assertIn("expanded", course)
