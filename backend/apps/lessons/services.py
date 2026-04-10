from __future__ import annotations

from django.conf import settings
from django.db import transaction

from agent.runner import AgentError, run_skill
from apps.auth.services import resolve_user_from_bearer_token
from apps.lessons.models import Lesson, LessonQuestion, LessonState, QuestionAttempt
from utils.fixtures import get_placeholder_lesson
from utils.lesson_state import calculate_xp, question_earns_star, transition_status


def normalize_mode(mode: str) -> str:
    return "solve" if str(mode).strip().lower() == "solve" else "learn"


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


def _lesson_payload_dict(lesson: Lesson, include_answers: bool = True) -> dict:
    questions = []
    for question in lesson.questions.all().order_by("position"):
        item = {
            "id": question.question_key,
            "prompt": question.prompt,
            "difficulty": question.difficulty,
        }
        if include_answers:
            item["answer_key"] = question.answer_key
        questions.append(item)

    return {
        "lesson_id": lesson.lesson_key,
        "mode": lesson.mode,
        "micro_theory": lesson.micro_theory,
        "questions": questions,
    }


@transaction.atomic
def upsert_lesson_payload(lesson_key: str, lesson_payload: dict, title: str, module_topic: str, mode: str) -> Lesson:
    normalized_key = str(lesson_key).strip()
    normalized_title = str(title).strip() or module_topic.strip() or normalized_key
    normalized_topic = str(module_topic).strip() or normalized_title
    normalized_mode = normalize_mode(mode)

    lesson = Lesson.objects.filter(lesson_key=normalized_key).first()
    if lesson is None:
        lesson = Lesson.objects.create(
            lesson_key=normalized_key,
            title=normalized_title,
            module_topic=normalized_topic,
            mode=normalized_mode,
            micro_theory=str(lesson_payload.get("micro_theory", "")).strip(),
        )
    else:
        lesson.title = normalized_title
        lesson.module_topic = normalized_topic
        lesson.mode = normalized_mode
        lesson.micro_theory = str(lesson_payload.get("micro_theory", "")).strip()
        lesson.save(update_fields=["title", "module_topic", "mode", "micro_theory", "updated_at"])
        lesson.questions.all().delete()

    questions = lesson_payload.get("questions", [])
    for index, question in enumerate(questions):
        LessonQuestion.objects.create(
            lesson=lesson,
            question_key=str(question.get("id", f"q{index + 1}")).strip(),
            prompt=str(question.get("prompt", "")).strip(),
            difficulty=str(question.get("difficulty", "easy")).strip(),
            answer_key=str(question.get("answer_key", "")).strip(),
            position=index,
        )

    return Lesson.objects.prefetch_related("questions").get(lesson_key=normalized_key)


def get_or_create_lesson(lesson_key: str, module_topic: str, mode: str) -> Lesson:
    lesson = Lesson.objects.prefetch_related("questions").filter(lesson_key=str(lesson_key).strip()).first()
    if lesson is not None:
        return lesson

    try:
        lesson_data = run_skill(
            "lesson_generator",
            mode=normalize_mode(mode),
            module_topic=module_topic,
        )
    except AgentError:
        lesson_data = get_placeholder_lesson(module_topic, mode=normalize_mode(mode))

    lesson_data["lesson_id"] = lesson_key
    return upsert_lesson_payload(
        lesson_key=lesson_key,
        lesson_payload=lesson_data,
        title=module_topic,
        module_topic=module_topic,
        mode=mode,
    )


def get_lesson_payload(lesson_key: str) -> dict | None:
    lesson = Lesson.objects.prefetch_related("questions").filter(lesson_key=str(lesson_key).strip()).first()
    if lesson is None:
        return None
    return _lesson_payload_dict(lesson, include_answers=True)


def get_public_lesson_payload(lesson_key: str) -> dict | None:
    lesson = Lesson.objects.prefetch_related("questions").filter(lesson_key=str(lesson_key).strip()).first()
    if lesson is None:
        return None
    return _lesson_payload_dict(lesson, include_answers=False)


def ensure_lesson_state(user, lesson: Lesson) -> LessonState:
    state, _ = LessonState.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={
            "status": LessonState.Status.NOT_STARTED,
            "stars_remaining": 0,
            "xp_earned": 0,
        },
    )
    return state


def get_question(lesson: Lesson, question_key: str) -> LessonQuestion | None:
    return lesson.questions.filter(question_key=str(question_key).strip()).first()


def ensure_question(lesson: Lesson, question_key: str) -> LessonQuestion:
    normalized_key = str(question_key).strip()
    question = get_question(lesson, normalized_key)
    if question is not None:
        return question

    position = lesson.questions.count()
    question = LessonQuestion.objects.create(
        lesson=lesson,
        question_key=normalized_key,
        prompt=normalized_key or "Placeholder question",
        difficulty="easy",
        answer_key="",
        position=position,
    )
    return question


def get_answered_question_count(state: LessonState) -> int:
    return (
        QuestionAttempt.objects.filter(lesson_state=state)
        .exclude(answer="")
        .values("question_id")
        .distinct()
        .count()
    )


def get_hint_count(state: LessonState, question: LessonQuestion) -> int:
    return QuestionAttempt.objects.filter(
        lesson_state=state,
        question=question,
        answer="",
    ).count()


@transaction.atomic
def record_hint_attempt(state: LessonState, question: LessonQuestion, hint_level: int) -> int:
    normalized_hint_level = max(1, min(int(hint_level), 3))
    QuestionAttempt.objects.create(
        lesson_state=state,
        question=question,
        answer="",
        correct=None,
        hint_level=normalized_hint_level,
    )
    state.last_question = question
    state.save(update_fields=["last_question", "updated_at"])
    return state.stars_remaining


@transaction.atomic
def record_answer_attempt(
    state: LessonState,
    question: LessonQuestion,
    answer: str,
    correct: bool,
    hint_count: int,
) -> dict:
    xp_awarded = calculate_xp(correct=correct, hint_level=hint_count)
    earned_star = question_earns_star(correct=correct, hint_usage=hint_count)

    QuestionAttempt.objects.create(
        lesson_state=state,
        question=question,
        answer=answer,
        correct=correct,
        hint_level=hint_count,
    )

    state.xp_earned += xp_awarded
    if earned_star:
        state.stars_remaining = min(3, state.stars_remaining + 1)
    state.last_question = question
    answered_count = get_answered_question_count(state)
    total_questions = state.lesson.questions.count()
    state.status = transition_status(state.status, answered_count, total_questions)
    state.save(update_fields=["xp_earned", "stars_remaining", "last_question", "status", "updated_at"])

    return {
        "xp": xp_awarded,
        "star_earned": earned_star,
        "total_stars": state.stars_remaining,
        "status": state.status,
    }


def get_lesson_state_payload(user, lesson: Lesson) -> dict | None:
    state = LessonState.objects.filter(user=user, lesson=lesson).first()
    if state is None:
        return None

    attempts = (
        QuestionAttempt.objects
        .filter(lesson_state=state)
        .select_related("question")
        .order_by("created_at")
    )

    questions_progress: dict[str, dict] = {}
    for attempt in attempts:
        qkey = attempt.question.question_key
        if qkey not in questions_progress:
            questions_progress[qkey] = {
                "question_id": qkey,
                "answered": False,
                "correct": None,
                "hints_used": 0,
                "answer": "",
            }
        if attempt.answer:
            questions_progress[qkey]["answered"] = True
            questions_progress[qkey]["correct"] = attempt.correct
            questions_progress[qkey]["answer"] = attempt.answer
        else:
            questions_progress[qkey]["hints_used"] = attempt.hint_level

    return {
        "status": state.status,
        "xp_earned": state.xp_earned,
        "stars_remaining": state.stars_remaining,
        "last_question_id": state.last_question.question_key if state.last_question else None,
        "updated_at": state.updated_at.isoformat(),
        "questions": questions_progress,
    }


@transaction.atomic
def reset_lesson_state(user, lesson: Lesson) -> dict:
    state = LessonState.objects.filter(user=user, lesson=lesson).first()
    if state is None:
        return {"status": "not_started", "xp_earned": 0, "total_stars": 0}

    QuestionAttempt.objects.filter(lesson_state=state).delete()
    state.status = LessonState.Status.NOT_STARTED
    state.xp_earned = 0
    state.stars_remaining = 0
    state.last_question = None
    state.save(update_fields=["status", "xp_earned", "stars_remaining", "last_question", "updated_at"])
    return {
        "status": state.status,
        "xp_earned": state.xp_earned,
        "total_stars": state.stars_remaining,
    }


@transaction.atomic
def delete_lesson_state(user, lesson: Lesson) -> bool:
    state = LessonState.objects.filter(user=user, lesson=lesson).first()
    if state is None:
        return False
    QuestionAttempt.objects.filter(lesson_state=state).delete()
    state.delete()
    return True


def reset_lesson_store() -> None:
    QuestionAttempt.objects.all().delete()
    LessonState.objects.all().delete()
    LessonQuestion.objects.all().delete()
    Lesson.objects.all().delete()
