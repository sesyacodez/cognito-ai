"""
Progress_Updater skill — computes XP, stars, and lesson state after each answer.

This is a LOCAL (deterministic) skill: it does NOT call OpenRouter.
The runner detects LOCAL = True and calls run() directly.
"""

from utils.validators import normalize_progress_output, ValidationError

LOCAL = True

# ── Skill spec (kept for documentation and potential future LLM routing) ──────

SPEC = {
    "type": "function",
    "function": {
        "name": "progress_updater",
        "description": (
            "Computes updated XP, stars, and lesson status based on answer "
            "correctness, hint usage, and response timing. "
            "Returns a deterministic progress update."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "correctness": {
                    "type": "boolean",
                    "description": "Whether the student's answer was correct.",
                },
                "hint_usage": {
                    "type": "integer",
                    "description": "Number of hints the student used (0-3).",
                },
                "timing_seconds": {
                    "type": "integer",
                    "description": "How long the student took to answer, in seconds.",
                },
                "current_xp": {
                    "type": "integer",
                    "description": "XP accumulated so far in this lesson.",
                },
                "current_status": {
                    "type": "string",
                    "enum": ["not_started", "in_progress", "completed"],
                    "description": "Current lesson status before this answer.",
                },
                "answered_count": {
                    "type": "integer",
                    "description": "Number of questions answered so far (including this one).",
                },
                "total_questions": {
                    "type": "integer",
                    "description": "Total number of questions in the lesson.",
                },
            },
            "required": [
                "correctness", "hint_usage", "timing_seconds",
                "current_xp", "current_status", "answered_count", "total_questions",
            ],
        },
    },
}

SYSTEM_PROMPTS = {
    "learn": "Progress_Updater is a deterministic skill. No LLM prompt needed.",
}


# ── XP / stars / bonus logic ──────────────────────────────────────────────────

BASE_XP = 100
HINT_PENALTY = 25
MIN_XP_WITH_HINTS = 10
SPEED_BONUS_THRESHOLD = 30
SPEED_BONUS_XP = 20

VALID_TRANSITIONS = {
    "not_started": {"in_progress"},
    "in_progress": {"in_progress", "completed"},
    "completed": set(),
}


def _compute_xp(correctness: bool, hint_usage: int, timing_seconds: int) -> int:
    if not correctness:
        return 0
    xp = BASE_XP - (hint_usage * HINT_PENALTY)
    xp = max(xp, MIN_XP_WITH_HINTS) if hint_usage > 0 else xp
    if timing_seconds > 0 and timing_seconds <= SPEED_BONUS_THRESHOLD:
        xp += SPEED_BONUS_XP
    return xp


def _compute_stars(hint_usage: int) -> int:
    return max(0, 3 - hint_usage)


def _next_status(current_status: str, answered_count: int, total_questions: int) -> str:
    if answered_count <= 0:
        return current_status
    if current_status == "completed":
        return "completed"

    target = "completed" if answered_count >= total_questions else "in_progress"

    if target not in VALID_TRANSITIONS.get(current_status, set()):
        if current_status == "not_started" and target == "completed":
            return "completed"
        return current_status

    return target


# ── Skill implementation ──────────────────────────────────────────────────────

def run(params: dict, mode: str = "learn") -> dict:
    """
    Deterministic progress computation. Does NOT call OpenRouter.
    """
    correctness = bool(params.get("correctness", False))
    hint_usage = int(params.get("hint_usage", 0))
    timing_seconds = int(params.get("timing_seconds", 0))
    current_xp = int(params.get("current_xp", 0))
    current_status = str(params.get("current_status", "not_started"))
    answered_count = int(params.get("answered_count", 1))
    total_questions = int(params.get("total_questions", 3))

    xp_earned = _compute_xp(correctness, hint_usage, timing_seconds)
    stars = _compute_stars(hint_usage)
    new_status = _next_status(current_status, answered_count, total_questions)

    result = {
        "xp_earned": xp_earned,
        "total_xp": current_xp + xp_earned,
        "stars_remaining": stars,
        "status": new_status,
        "correctness": correctness,
    }

    return normalize_progress_output(result)
