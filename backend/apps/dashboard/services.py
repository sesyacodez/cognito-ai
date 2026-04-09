from __future__ import annotations

from collections import defaultdict

from django.conf import settings
from django.utils import timezone

from apps.auth.services import resolve_user_from_bearer_token
from apps.lessons.models import LessonState, QuestionAttempt
from apps.roadmaps.models import Roadmap


def extract_bearer_token(request) -> str | None:
    header = request.headers.get("Authorization", "").strip()
    if not header.lower().startswith("bearer "):
        return None

    token = header.split(" ", 1)[1].strip()
    return token or None


def get_authenticated_user(request):
    token = extract_bearer_token(request)
    if token is None:
        return None

    return resolve_user_from_bearer_token(
        token,
        allow_firebase_fallback=settings.AUTH_STUB_ALLOW_FIREBASE_FALLBACK,
    )


def _calculate_streak_summary(attempts: list[QuestionAttempt]) -> dict:
    if not attempts:
        return {
            "current": 0,
            "longest": 0,
            "last_active_at": None,
        }

    study_dates = sorted({timezone.localdate(attempt.created_at) for attempt in attempts})
    if not study_dates:
        return {
            "current": 0,
            "longest": 0,
            "last_active_at": None,
        }

    longest_run = 1
    current_run = 1
    previous_date = study_dates[0]
    for study_date in study_dates[1:]:
        if (study_date - previous_date).days == 1:
            current_run += 1
        elif study_date != previous_date:
            longest_run = max(longest_run, current_run)
            current_run = 1
        previous_date = study_date

    longest_run = max(longest_run, current_run)

    return {
        "current": current_run,
        "longest": longest_run,
        "last_active_at": attempts[0].created_at.isoformat(),
    }


def _serialize_attempt(attempt: QuestionAttempt) -> dict:
    attempt_type = "answer" if attempt.answer else "hint"
    return {
        "kind": attempt_type,
        "lesson_id": attempt.lesson_state.lesson.lesson_key,
        "lesson_title": attempt.lesson_state.lesson.title,
        "question_id": attempt.question.question_key,
        "correct": attempt.correct,
        "hint_level": attempt.hint_level,
        "created_at": attempt.created_at.isoformat(),
    }


def build_dashboard_payload(user) -> dict:
    roadmaps = list(
        Roadmap.objects.filter(user=user)
        .prefetch_related("modules")
        .order_by("-created_at")
    )
    lesson_states = list(
        LessonState.objects.filter(user=user)
        .select_related("lesson", "last_question")
        .prefetch_related("lesson__questions")
        .order_by("-updated_at")
    )
    attempts = list(
        QuestionAttempt.objects.filter(lesson_state__user=user)
        .select_related("lesson_state__lesson", "question")
        .order_by("-created_at")
    )

    attempts_by_state: dict[str, list[QuestionAttempt]] = defaultdict(list)
    for attempt in attempts:
        attempts_by_state[str(attempt.lesson_state_id)].append(attempt)

    lesson_summaries = []
    answered_question_ids: set[str] = set()
    total_questions = 0
    total_xp = 0
    total_stars = 0
    completed_lessons = 0
    in_progress_lessons = 0
    not_started_lessons = 0

    for state in lesson_states:
        state_attempts = attempts_by_state.get(str(state.id), [])
        question_count = len(state.lesson.questions.all())
        answered_ids = {attempt.question_id for attempt in state_attempts if attempt.answer}
        answered_question_ids.update(str(question_id) for question_id in answered_ids)
        answered_count = len(answered_ids)
        progress_percent = int(round((answered_count / question_count) * 100)) if question_count else 0

        total_questions += question_count
        total_xp += state.xp_earned
        total_stars += state.stars_remaining

        if state.status == LessonState.Status.COMPLETED:
            completed_lessons += 1
        elif state.status == LessonState.Status.IN_PROGRESS:
            in_progress_lessons += 1
        else:
            not_started_lessons += 1

        lesson_summaries.append(
            {
                "lesson_id": state.lesson.lesson_key,
                "title": state.lesson.title,
                "module_topic": state.lesson.module_topic,
                "mode": state.lesson.mode,
                "status": state.status,
                "questions_total": question_count,
                "answered_questions": answered_count,
                "progress": progress_percent,
                "xp_earned": state.xp_earned,
                "stars_remaining": state.stars_remaining,
                "created_at": state.created_at.isoformat(),
                "updated_at": state.updated_at.isoformat(),
                "last_question_id": state.last_question.question_key if state.last_question else None,
            }
        )

    summary = {
        "roadmaps_total": len(roadmaps),
        "lessons_total": len(lesson_states),
        "completed_lessons": completed_lessons,
        "in_progress_lessons": in_progress_lessons,
        "not_started_lessons": not_started_lessons,
        "questions_total": total_questions,
        "questions_answered": len(answered_question_ids),
        "question_attempts": len(attempts),
        "xp_earned": total_xp,
        "stars_remaining": total_stars,
    }

    return {
        "summary": summary,
        "streak": _calculate_streak_summary(attempts),
        "roadmaps": [roadmap.to_api_dict() for roadmap in roadmaps],
        "lessons": lesson_summaries,
        "recent_activity": [_serialize_attempt(attempt) for attempt in attempts[:5]],
    }
