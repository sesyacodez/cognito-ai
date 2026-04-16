from uuid import uuid4


def get_placeholder_roadmap(topic: str) -> dict:
    """
    Returns a static 5-module roadmap in the normalized API contract shape.
    Used as a graceful fallback when the agent runner is unavailable.
    """
    topic_clean = topic.strip() or "General Learning Path"

    return {
        "roadmap_id": f"placeholder-{uuid4().hex[:8]}",
        "mode": "learn",
        "modules": [
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 0,
                "title": f"{topic_clean}: Foundations",
                "outcome": "Learn the basics and fundamental concepts.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 1,
                "title": f"{topic_clean}: Core Concepts",
                "outcome": "Explore the essential principles and theories.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 2,
                "title": f"{topic_clean}: Intermediate Techniques",
                "outcome": "Develop intermediate skills and apply techniques.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 3,
                "title": f"{topic_clean}: Advanced Applications",
                "outcome": "Master advanced applications and real-world use cases.",
            },
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": 4,
                "title": f"{topic_clean}: Capstone Project",
                "outcome": "Complete a capstone project to demonstrate your learning.",
            },
        ],
    }


def get_adaptive_placeholder_roadmap(topic: str, mode: str = "learn") -> dict:
    """
    Returns a deterministic fallback roadmap whose module count adapts to topic complexity.
    This is used when the decomposer skill cannot be reached.
    """
    topic_clean = topic.strip() or "General Learning Path"
    mode_clean = "solve" if str(mode).strip().lower() == "solve" else "learn"

    word_count = len(topic_clean.split())
    if mode_clean == "solve":
        if word_count <= 4:
            module_count = 1
        elif word_count <= 10:
            module_count = 3
        else:
            module_count = 5
        stage_templates = [
            ("Problem Framing", "Clarify the scope, constraints, and desired outcome."),
            ("Implementation Plan", "Break the solution into concrete executable steps."),
            ("Build and Validate", "Implement the solution and verify against requirements."),
            ("Hardening", "Address edge cases, reliability, and maintainability concerns."),
            ("Delivery", "Package and document the final solution for use."),
        ]
    else:
        if word_count <= 3:
            module_count = 3
        elif word_count <= 7:
            module_count = 4
        elif word_count <= 12:
            module_count = 5
        elif word_count <= 18:
            module_count = 6
        else:
            module_count = 7
        stage_templates = [
            ("Foundations", "Learn the basics and fundamental concepts."),
            ("Core Concepts", "Explore the essential principles and theories."),
            ("Guided Practice", "Apply concepts in structured exercises."),
            ("Intermediate Techniques", "Develop intermediate skills and apply techniques."),
            ("Advanced Applications", "Use advanced patterns in realistic scenarios."),
            ("Integration", "Connect concepts into a coherent end-to-end workflow."),
            ("Capstone Project", "Complete a capstone project to demonstrate your learning."),
        ]

    modules = []
    for index in range(module_count):
        stage_title, stage_outcome = stage_templates[index]
        modules.append(
            {
                "id": f"placeholder-{uuid4().hex[:6]}",
                "index": index,
                "title": f"{topic_clean}: {stage_title}",
                "outcome": stage_outcome,
            }
        )

    return {
        "roadmap_id": f"placeholder-{uuid4().hex[:8]}",
        "mode": mode_clean,
        "modules": modules,
    }


def get_placeholder_lesson(module_topic: str, mode: str = "learn") -> dict:
    """
    Returns a static lesson with micro-theory and 3 questions.
    Used as a graceful fallback when the agent runner is unavailable.
    """
    topic_clean = module_topic.strip() or "General Topic"

    return {
        "lesson_id": f"placeholder-lesson-{uuid4().hex[:8]}",
        "mode": mode,
        "micro_theory": (
            f"This is a placeholder micro-theory for '{topic_clean}'. "
            "In a real scenario, this would contain condensed educational content "
            "explaining the core concepts of the module clearly and concisely."
        ),
        "questions": [
            {
                "id": f"q1-{uuid4().hex[:4]}",
                "prompt": f"What is the first fundamental concept of {topic_clean}?",
                "difficulty": "easy",
                "answer_key": "The first fundamental concept.",
            },
            {
                "id": f"q2-{uuid4().hex[:4]}",
                "prompt": f"Explain why {topic_clean} is important in its context.",
                "difficulty": "medium",
                "answer_key": "Because it enables structured learning.",
            },
            {
                "id": f"q3-{uuid4().hex[:4]}",
                "prompt": f"How would you apply {topic_clean} to a complex problem?",
                "difficulty": "hard",
                "answer_key": "By breaking it down into smaller modules.",
            },
        ],
    }


def get_placeholder_evaluation(correct: bool = True) -> dict:
    """Returns a static Socratic evaluation response."""
    return {
        "correct": correct,
        "next_prompt": (
            "Great job! That's correct. Now, can you tell me how this "
            "relates to the previous module?"
            if correct
            else "Not quite. Think about the relationship between the inputs and outputs. "
            "What happens if you change the initial state?"
        ),
        "hint": None if correct else "Try looking at the documentation for the API.",
    }


def get_placeholder_hint(hint_level: int = 1) -> dict:
    """Returns a static hint response."""
    hints = {
        1: "Think about the main objective of the task.",
        2: "Consider using a loop to iterate through the data.",
        3: "The total should be the sum of all elements in the array.",
    }
    return {
        "hint": hints.get(hint_level, hints[1]),
        "stars_remaining": max(0, 4 - hint_level),
    }
