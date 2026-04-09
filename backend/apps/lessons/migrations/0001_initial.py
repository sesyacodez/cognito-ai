import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lesson",
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
                (
                    "lesson_key",
                    models.CharField(db_index=True, max_length=255, unique=True),
                ),
                ("title", models.CharField(max_length=255)),
                ("module_topic", models.CharField(max_length=255)),
                (
                    "mode",
                    models.CharField(
                        choices=[("learn", "Learn"), ("solve", "Solve")],
                        default="learn",
                        max_length=10,
                    ),
                ),
                ("micro_theory", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "lessons",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="LessonQuestion",
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
                ("question_key", models.CharField(max_length=255)),
                ("prompt", models.TextField()),
                ("difficulty", models.CharField(max_length=10)),
                ("answer_key", models.TextField()),
                ("position", models.IntegerField()),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="lessons.lesson",
                    ),
                ),
            ],
            options={
                "db_table": "questions",
                "ordering": ["position"],
            },
        ),
        migrations.CreateModel(
            name="LessonState",
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
                ("stars_remaining", models.PositiveSmallIntegerField(default=3)),
                ("xp_earned", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "last_question",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="last_question_states",
                        to="lessons.lessonquestion",
                    ),
                ),
                (
                    "lesson",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="states",
                        to="lessons.lesson",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lesson_states",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "lesson_states",
            },
        ),
        migrations.CreateModel(
            name="QuestionAttempt",
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
                ("answer", models.TextField(blank=True, default="")),
                ("correct", models.BooleanField(blank=True, null=True)),
                ("hint_level", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "lesson_state",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attempts",
                        to="lessons.lessonstate",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attempts",
                        to="lessons.lessonquestion",
                    ),
                ),
            ],
            options={
                "db_table": "question_attempts",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="lessonquestion",
            constraint=models.UniqueConstraint(fields=["lesson", "question_key"], name="unique_question_key_per_lesson"),
        ),
        migrations.AddConstraint(
            model_name="lessonquestion",
            constraint=models.UniqueConstraint(fields=["lesson", "position"], name="unique_question_position_per_lesson"),
        ),
        migrations.AddConstraint(
            model_name="lessonstate",
            constraint=models.UniqueConstraint(fields=["user", "lesson"], name="unique_lesson_state_per_user"),
        ),
    ]