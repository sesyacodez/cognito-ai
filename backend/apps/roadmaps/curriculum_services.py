from __future__ import annotations

import logging
from typing import Iterable

from django.db import transaction
from django.shortcuts import get_object_or_404

from agent.runner import AgentError, run_skill
from apps.roadmaps.models import Curriculum, CurriculumCourse, Roadmap
from apps.roadmaps.services import (
    _get_module_progress_map,
    create_roadmap_for_user,
    normalize_mode,
    serialize_roadmap,
)
from utils.fixtures import get_adaptive_placeholder_curriculum


logger = logging.getLogger(__name__)


def plan_curriculum(topic: str, mode: str = "learn") -> dict:
    """
    Generate a curriculum plan (2-6 courses) for a broad topic without
    persisting anything. Falls back to a deterministic placeholder if the
    planner skill is unreachable or returns malformed output.
    """
    normalized_topic = str(topic).strip() or "General Learning Path"
    normalized_mode = "learn"

    last_agent_error: AgentError | None = None
    for _ in range(2):
        try:
            plan = run_skill(
                "curriculum_planner",
                mode=normalized_mode,
                topic=normalized_topic,
            )
            courses = plan.get("courses", [])
            if courses:
                return {
                    "topic": plan.get("topic") or normalized_topic,
                    "mode": normalized_mode,
                    "courses": courses,
                    "source": "agent",
                }
        except AgentError as exc:
            last_agent_error = exc

    if last_agent_error is not None:
        logger.warning(
            "Curriculum planner failed for topic '%s'. Falling back to placeholder. Error: %s",
            normalized_topic,
            last_agent_error,
        )

    placeholder = get_adaptive_placeholder_curriculum(normalized_topic, mode=normalized_mode)
    return {
        "topic": placeholder["topic"],
        "mode": normalized_mode,
        "courses": placeholder["courses"],
        "source": "placeholder",
    }


def _normalize_course_inputs(courses: Iterable[dict]) -> list[dict]:
    """
    Accept the user-confirmed course list (from the preview) and normalize it
    to a list of {title, outcome, index} dicts in stable order.
    """
    cleaned: list[dict] = []
    for fallback_index, raw in enumerate(courses):
        title = str(raw.get("title", "")).strip()
        if not title:
            continue
        outcome = str(raw.get("outcome", "")).strip() or "Build the skills covered by this course."
        try:
            index = int(raw.get("index", fallback_index))
        except (TypeError, ValueError):
            index = fallback_index
        cleaned.append({"title": title, "outcome": outcome, "index": max(index, 0)})

    cleaned.sort(key=lambda c: c["index"])
    for new_index, course in enumerate(cleaned):
        course["index"] = new_index
    return cleaned


@transaction.atomic
def create_curriculum_for_user(
    user,
    topic: str,
    mode: str,
    courses: Iterable[dict],
) -> Curriculum:
    """
    Persist a Curriculum and its CurriculumCourse rows. The first course is
    expanded into a Roadmap eagerly so the user can start immediately; the
    rest are deferred until expand_course() is called for them.
    """
    normalized_topic = str(topic).strip() or "General Learning Path"
    normalized_mode = normalize_mode(mode)
    if normalized_mode != "learn":
        normalized_mode = "learn"

    course_inputs = _normalize_course_inputs(courses)
    if not course_inputs:
        raise ValueError("courses must contain at least one valid course")

    curriculum = Curriculum.objects.create(
        user=user,
        topic=normalized_topic,
        mode=normalized_mode,
    )

    course_rows = [
        CurriculumCourse(
            curriculum=curriculum,
            index=course["index"],
            title=course["title"],
            outcome=course["outcome"],
        )
        for course in course_inputs
    ]
    CurriculumCourse.objects.bulk_create(course_rows)

    first_course = (
        CurriculumCourse.objects.filter(curriculum=curriculum).order_by("index").first()
    )
    if first_course is not None:
        expand_course(first_course, user=user)

    return curriculum


def expand_course(course: CurriculumCourse, user=None) -> Roadmap:
    """
    Generate (or look up) the Roadmap for a curriculum course. Idempotent:
    repeated calls return the existing roadmap rather than regenerating it.
    """
    if course.roadmap_id is not None:
        return course.roadmap

    owning_user = user or course.curriculum.user
    topic = course.title
    if course.outcome:
        topic = f"{course.title}: {course.outcome}"

    roadmap = create_roadmap_for_user(
        owning_user,
        topic=topic,
        mode=course.curriculum.mode,
    )
    course.roadmap = roadmap
    course.save(update_fields=["roadmap"])
    return roadmap


def _summarize_course_progress(course: CurriculumCourse, module_progress: dict) -> dict:
    """
    Return per-course rollup numbers based on existing lesson states.
    Courses without an expanded roadmap have zero progress.
    """
    if course.roadmap_id is None:
        return {
            "module_count": 0,
            "completed_modules": 0,
            "in_progress_modules": 0,
            "progress": 0,
        }

    modules = list(course.roadmap.modules.all())
    module_count = len(modules)
    completed = 0
    in_progress = 0
    for module in modules:
        lesson_key = f"{course.roadmap_id}-{module.index}"
        state = module_progress.get(lesson_key)
        if state is None:
            continue
        if state["status"] == "completed":
            completed += 1
        elif state["status"] == "in_progress":
            in_progress += 1

    progress = int(round((completed / module_count) * 100)) if module_count else 0
    return {
        "module_count": module_count,
        "completed_modules": completed,
        "in_progress_modules": in_progress,
        "progress": progress,
    }


def serialize_curriculum(curriculum: Curriculum, module_progress: dict | None = None) -> dict:
    data = curriculum.to_api_dict()
    progress_map = module_progress or {}

    total_modules = 0
    total_completed = 0
    for course, course_data in zip(curriculum.courses.all(), data["courses"]):
        rollup = _summarize_course_progress(course, progress_map)
        course_data.update(rollup)
        if course.roadmap_id is not None:
            course_data["modules"] = serialize_roadmap(course.roadmap, progress_map)[
                "modules"
            ]
        else:
            course_data["modules"] = []
        total_modules += rollup["module_count"]
        total_completed += rollup["completed_modules"]
        if rollup["module_count"] == 0:
            course_data["status"] = course.status
        elif rollup["completed_modules"] == rollup["module_count"]:
            course_data["status"] = CurriculumCourse.Status.COMPLETED
        elif rollup["completed_modules"] > 0 or rollup["in_progress_modules"] > 0:
            course_data["status"] = CurriculumCourse.Status.IN_PROGRESS
        else:
            course_data["status"] = CurriculumCourse.Status.NOT_STARTED

    data["module_count"] = total_modules
    data["completed_modules"] = total_completed
    data["progress"] = (
        int(round((total_completed / total_modules) * 100)) if total_modules else 0
    )
    data["course_count"] = len(data["courses"])
    data["completed_courses"] = sum(
        1 for c in data["courses"] if c["status"] == CurriculumCourse.Status.COMPLETED
    )
    return data


def list_curriculums_for_user(user) -> list[dict]:
    curriculums = (
        Curriculum.objects.filter(user=user)
        .prefetch_related("courses__roadmap__modules")
        .order_by("-created_at")
    )
    progress_map = _get_module_progress_map(user)
    return [serialize_curriculum(c, progress_map) for c in curriculums]


def get_curriculum_for_user(user, curriculum_id) -> Curriculum:
    return get_object_or_404(
        Curriculum.objects.prefetch_related("courses__roadmap__modules"),
        id=curriculum_id,
        user=user,
    )


def get_course_for_user(user, curriculum_id, course_id) -> CurriculumCourse:
    return get_object_or_404(
        CurriculumCourse.objects.select_related("curriculum"),
        id=course_id,
        curriculum_id=curriculum_id,
        curriculum__user=user,
    )


def serialize_curriculum_with_first_roadmap(curriculum: Curriculum, user) -> dict:
    progress_map = _get_module_progress_map(user)
    payload = serialize_curriculum(curriculum, progress_map)
    first_course = curriculum.courses.order_by("index").first()
    if first_course is not None and first_course.roadmap_id is not None:
        payload["first_roadmap"] = serialize_roadmap(first_course.roadmap, progress_map)
        payload["first_course_id"] = str(first_course.id)
    else:
        payload["first_roadmap"] = None
        payload["first_course_id"] = str(first_course.id) if first_course else None
    return payload
