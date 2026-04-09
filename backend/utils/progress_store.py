"""
In-memory progress store for tracking per-user, per-lesson progress.

Mirrors the lesson_states and question_attempts tables from data-schema.md.
Will be replaced by DB-backed persistence when Supabase is fully wired.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class QuestionAttempt:
    id: str
    question_id: str
    answer: str
    correct: bool
    hint_level: int
    created_at: str


@dataclass
class LessonProgress:
    user_id: str
    lesson_id: str
    status: str = "not_started"
    stars_remaining: int = 3
    xp_earned: int = 0
    answered_questions: list[str] = field(default_factory=list)
    attempts: list[QuestionAttempt] = field(default_factory=list)
    last_question_id: str | None = None
    updated_at: str = ""

    def __post_init__(self):
        if not self.updated_at:
            self.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()


@dataclass
class UserDashboard:
    total_xp: int = 0
    total_stars: int = 0
    lessons_completed: int = 0
    lessons_in_progress: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    recent_activity: list[dict] = field(default_factory=list)


# user_id -> lesson_id -> LessonProgress
_progress: dict[str, dict[str, LessonProgress]] = {}

# user_id -> list of dates (ISO date strings) with activity
_activity_dates: dict[str, list[str]] = {}


def reset_progress_store() -> None:
    _progress.clear()
    _activity_dates.clear()


def get_lesson_progress(user_id: str, lesson_id: str) -> LessonProgress:
    user_progress = _progress.setdefault(user_id, {})
    if lesson_id not in user_progress:
        user_progress[lesson_id] = LessonProgress(user_id=user_id, lesson_id=lesson_id)
    return user_progress[lesson_id]


def update_lesson_progress(
    user_id: str,
    lesson_id: str,
    question_id: str,
    answer: str,
    correct: bool,
    hint_level: int,
    xp_earned: int,
    stars_remaining: int,
    new_status: str,
) -> LessonProgress:
    progress = get_lesson_progress(user_id, lesson_id)

    attempt = QuestionAttempt(
        id=str(uuid4()),
        question_id=question_id,
        answer=answer,
        correct=correct,
        hint_level=hint_level,
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
    progress.attempts.append(attempt)

    if question_id not in progress.answered_questions and correct:
        progress.answered_questions.append(question_id)

    progress.xp_earned += xp_earned
    progress.stars_remaining = min(progress.stars_remaining, stars_remaining)
    progress.status = new_status
    progress.last_question_id = question_id
    progress.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    _record_activity(user_id)
    return progress


def _record_activity(user_id: str) -> None:
    today = datetime.date.today().isoformat()
    dates = _activity_dates.setdefault(user_id, [])
    if not dates or dates[-1] != today:
        dates.append(today)


def _compute_streak(user_id: str) -> tuple[int, int]:
    dates = _activity_dates.get(user_id, [])
    if not dates:
        return 0, 0

    unique = sorted(set(dates))
    parsed = [datetime.date.fromisoformat(d) for d in unique]

    current = 1
    longest = 1
    streak = 1

    for i in range(len(parsed) - 1, 0, -1):
        if (parsed[i] - parsed[i - 1]).days == 1:
            streak += 1
        else:
            break

    today = datetime.date.today()
    if parsed[-1] != today and (today - parsed[-1]).days > 1:
        streak = 0

    current = streak
    temp = 1
    for i in range(1, len(parsed)):
        if (parsed[i] - parsed[i - 1]).days == 1:
            temp += 1
            longest = max(longest, temp)
        else:
            temp = 1
    longest = max(longest, temp)

    return current, longest


def get_dashboard(user_id: str) -> dict:
    user_progress = _progress.get(user_id, {})

    total_xp = 0
    total_stars = 0
    lessons_completed = 0
    lessons_in_progress = 0
    recent_activity = []

    for lesson_id, lp in user_progress.items():
        total_xp += lp.xp_earned
        total_stars += lp.stars_remaining
        if lp.status == "completed":
            lessons_completed += 1
        elif lp.status == "in_progress":
            lessons_in_progress += 1

        if lp.status != "not_started":
            recent_activity.append({
                "lesson_id": lp.lesson_id,
                "status": lp.status,
                "xp_earned": lp.xp_earned,
                "stars_earned": lp.stars_remaining,
                "updated_at": lp.updated_at,
            })

    recent_activity.sort(key=lambda a: a["updated_at"], reverse=True)
    recent_activity = recent_activity[:10]

    current_streak, longest_streak = _compute_streak(user_id)

    return {
        "total_xp": total_xp,
        "total_stars": total_stars,
        "lessons_completed": lessons_completed,
        "lessons_in_progress": lessons_in_progress,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "recent_activity": recent_activity,
    }
