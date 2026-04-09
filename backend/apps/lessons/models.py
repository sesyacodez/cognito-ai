from __future__ import annotations

import uuid

from django.db import models

from apps.users.models import User


class Lesson(models.Model):
    class Mode(models.TextChoices):
        LEARN = "learn", "Learn"
        SOLVE = "solve", "Solve"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson_key = models.CharField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    module_topic = models.CharField(max_length=255)
    mode = models.CharField(max_length=10, choices=Mode.choices, default=Mode.LEARN)
    micro_theory = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return self.lesson_key


class LessonQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions")
    question_key = models.CharField(max_length=255)
    prompt = models.TextField()
    difficulty = models.CharField(max_length=10)
    answer_key = models.TextField()
    position = models.IntegerField()

    class Meta:
        db_table = "questions"
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["lesson", "question_key"], name="unique_question_key_per_lesson"),
            models.UniqueConstraint(fields=["lesson", "position"], name="unique_question_position_per_lesson"),
        ]

    def __str__(self) -> str:
        return f"{self.lesson.lesson_key}:{self.question_key}"


class LessonState(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_states")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="states")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    stars_remaining = models.PositiveSmallIntegerField(default=3)
    xp_earned = models.IntegerField(default=0)
    last_question = models.ForeignKey(
        LessonQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="last_question_states",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lesson_states"
        constraints = [
            models.UniqueConstraint(fields=["user", "lesson"], name="unique_lesson_state_per_user"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.lesson_id}"


class QuestionAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson_state = models.ForeignKey(LessonState, on_delete=models.CASCADE, related_name="attempts")
    question = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE, related_name="attempts")
    answer = models.TextField(blank=True, default="")
    correct = models.BooleanField(null=True, blank=True)
    hint_level = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "question_attempts"
        ordering = ["created_at"]
