"""Compatibility wrappers for the database-backed lesson storage layer."""

from __future__ import annotations

from copy import deepcopy


_LESSON_CACHE: dict[str, dict] = {}


def _should_fallback_to_memory(exc: Exception) -> bool:
    return exc.__class__.__name__ == "DatabaseOperationForbidden"


def save_lesson(lesson_id: str, lesson_data: dict):
    """Persist a lesson payload and its questions."""
    from apps.lessons.services import upsert_lesson_payload

    title = str(lesson_data.get("title") or lesson_data.get("module_topic") or lesson_id)
    module_topic = str(lesson_data.get("module_topic") or lesson_data.get("title") or lesson_id)
    mode = str(lesson_data.get("mode", "learn"))

    try:
        lesson = upsert_lesson_payload(
            lesson_key=lesson_id,
            lesson_payload=lesson_data,
            title=title,
            module_topic=module_topic,
            mode=mode,
        )
    except Exception as exc:
        if not _should_fallback_to_memory(exc):
            raise
        _LESSON_CACHE[lesson_id] = deepcopy(lesson_data)
        return lesson_data

    _LESSON_CACHE[lesson_id] = deepcopy(lesson_data)
    return lesson


def get_lesson(lesson_id: str) -> dict | None:
    """Retrieve a persisted lesson payload by ID, including answer keys."""
    from apps.lessons.services import get_lesson_payload

    try:
        lesson = get_lesson_payload(lesson_id)
    except Exception as exc:
        if not _should_fallback_to_memory(exc):
            raise
        lesson = None

    if lesson is not None:
        _LESSON_CACHE[lesson_id] = deepcopy(lesson)
        return lesson

    cached = _LESSON_CACHE.get(lesson_id)
    if cached is None:
        return None
    return deepcopy(cached)


def reset_lesson_store():
    """Clear all stored lessons (useful for tests)."""
    from apps.lessons.services import reset_lesson_store as reset_lessons

    try:
        reset_lessons()
    except Exception as exc:
        if not _should_fallback_to_memory(exc):
            raise

    _LESSON_CACHE.clear()
