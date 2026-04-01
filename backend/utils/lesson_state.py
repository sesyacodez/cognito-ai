"""
Business logic for lesson state transitions, XP calculation, and star management.
"""

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


def calculate_stars(hint_usage: int) -> int:
    """
    Calculate stars remaining (out of 3).
    Each hint used (hint_level 1, 2, 3) deducts one star.
    """
    return max(0, 3 - hint_usage)


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

    # Empty answers are never correct
    if not student_clean:
        return False

    # Very simple heuristic: if key is in student answer or vice versa
    if key_clean in student_clean or student_clean in key_clean:
        return True

    # If student answer is reasonably long and shares significant words, count it
    if len(student_clean) > 10 and any(word in student_clean for word in key_clean.split()):
        return True

    return False
