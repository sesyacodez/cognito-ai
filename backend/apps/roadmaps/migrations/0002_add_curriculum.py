import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
        ("roadmaps", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Curriculum",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("topic", models.CharField(max_length=255)),
                (
                    "mode",
                    models.CharField(
                        choices=[("learn", "Learn"), ("solve", "Solve")],
                        default="learn",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="curriculums",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "curriculums",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CurriculumCourse",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("index", models.IntegerField()),
                ("title", models.CharField(max_length=255)),
                ("outcome", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not started"),
                            ("in_progress", "In progress"),
                            ("completed", "Completed"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                (
                    "curriculum",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courses",
                        to="roadmaps.curriculum",
                    ),
                ),
                (
                    "roadmap",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="roadmaps.roadmap",
                    ),
                ),
            ],
            options={
                "db_table": "curriculum_courses",
                "ordering": ["index"],
            },
        ),
        migrations.AddConstraint(
            model_name="curriculumcourse",
            constraint=models.UniqueConstraint(
                fields=["curriculum", "index"], name="unique_course_index_per_curriculum"
            ),
        ),
        migrations.AddConstraint(
            model_name="curriculumcourse",
            constraint=models.CheckConstraint(
                condition=models.Q(index__gte=0), name="course_index_non_negative"
            ),
        ),
    ]
