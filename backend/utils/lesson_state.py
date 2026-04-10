"""
Business logic for lesson state transitions, XP calculation, and star management.
Includes safety checks that prevent invalid state transitions.
"""


VALID_TRANSITIONS = {
    "not_started": {"in_progress", "completed"},
    "in_progress": {"in_progress", "completed"},
    "completed": {"completed"},
}


class InvalidTransitionError(Exception):
    """Raised when a lesson state transition is not allowed."""


def validate_transition(current_status: str, target_status: str) -> None:
    """
    Validates that transitioning from current_status to target_status is allowed.
    Raises InvalidTransitionError if the transition is invalid.
    """
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise InvalidTransitionError(
            f"Cannot transition from '{current_status}' to '{target_status}'. "
            f"Allowed transitions from '{current_status}': {allowed or 'none'}."
        )


def safe_transition_status(
    current_status: str, answered_count: int, total_questions: int
) -> str:
    """
    Determines the next status with safety validation.
    If the computed transition is invalid, returns current_status unchanged.
    """
    target = transition_status(current_status, answered_count, total_questions)
    try:
        validate_transition(current_status, target)
        return target
    except InvalidTransitionError:
        return current_status


def calculate_xp(correct: bool, hint_level: int = 0) -> int:
    """
    Calculate XP awarded for a question attempt.
    Base XP is 100. Each hint reduces XP by 25.
    If multiple hints are used (hint_level > 3), XP is 10.
    If answer is incorrect, XP is 0.
    """
    if not correct:
        return 0

    if hint_level == 0:
        return 100
    elif hint_level == 1:
        return 75
    elif hint_level == 2:
        return 50
    elif hint_level == 3:
        return 25
    else:
        return 10


def question_earns_star(correct: bool, hint_usage: int) -> bool:
    """
    Returns True if this question earns its star.
    A star is only awarded when the answer is correct AND no hints were used.
    """
    return correct and hint_usage == 0


def transition_status(current_status: str, answered_count: int, total_questions: int) -> str:
    """
    Determines the next status of a lesson.
    Statuses: not_started, in_progress, completed
    """
    if answered_count == 0:
        return "not_started"
    elif answered_count < total_questions:
        return "in_progress"
    else:
        return "completed"


def evaluate_answer_local(student_answer: str, answer_key: str) -> bool:
    """
    Basic local evaluation fallback (substring match).
    In production, the Socratic_Tutor skill (AI) handles this.
    """
    student_clean = student_answer.strip().lower()
    key_clean = answer_key.strip().lower()

    if not student_clean:
        return False

    if key_clean in student_clean or student_clean in key_clean:
        return True

    if len(student_clean) > 10 and any(word in student_clean for word in key_clean.split()):
        return True

    return False
