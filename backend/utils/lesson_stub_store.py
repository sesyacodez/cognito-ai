"""
In-memory store for generated lessons to ensure consistency during development.
"""

# Dict mapping lesson_id (UUID4 string) -> lesson_data (dict)
_lessons = {}


def save_lesson(lesson_id: str, lesson_data: dict):
    """Save a generated lesson to the in-memory store."""
    _lessons[lesson_id] = lesson_data


def get_lesson(lesson_id: str) -> dict | None:
    """Retrieve a lesson from the store by ID."""
    return _lessons.get(lesson_id)


def reset_lesson_store():
    """Clear all stored lessons (useful for tests)."""
    global _lessons
    _lessons = {}
