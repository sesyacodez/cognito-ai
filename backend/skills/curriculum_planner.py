"""
Curriculum Planner skill - splits a broad topic into 2-6 focused courses.

Each course must be coherent enough that the existing decomposer can later
expand it into a roadmap of 1-7 modules. The planner does not generate
modules itself; it only proposes course-level structure for the user to
confirm.
"""

from utils.validators import normalize_curriculum_planner_output, ValidationError


SPEC = {
    "type": "function",
    "function": {
        "name": "curriculum_planner",
        "description": (
            "Splits a broad learning topic into 2-6 focused, sequenced courses. "
            "Each course is a sub-topic broad enough to deserve its own roadmap "
            "but narrow enough that a learner can complete it as one journey. "
            "Always return ONLY valid JSON matching the parameters schema, no markdown fences."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The broad topic the user wants to learn.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["learn"],
                    "description": "Curriculum planning is only supported in learn mode.",
                },
                "curriculum": {
                    "type": "object",
                    "description": "The proposed curriculum split.",
                    "properties": {
                        "topic": {"type": "string"},
                        "courses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "A UUID4 string.",
                                    },
                                    "title": {
                                        "type": "string",
                                        "description": "Course title (a focused sub-topic).",
                                    },
                                    "outcome": {
                                        "type": "string",
                                        "description": (
                                            "One-sentence learning outcome the learner "
                                            "should be able to demonstrate after this course."
                                        ),
                                    },
                                    "order": {
                                        "type": "integer",
                                        "description": "Sequential from 1.",
                                    },
                                },
                                "required": ["id", "title", "outcome", "order"],
                            },
                        },
                    },
                    "required": ["topic", "courses"],
                },
            },
            "required": ["topic", "mode", "curriculum"],
        },
    },
}


SYSTEM_PROMPTS = {
    "learn": (
        "You are the Curriculum Planner skill of a learning agent. "
        "Given a broad topic, split it into 2-6 sequenced courses. Each course "
        "should be a focused sub-topic that makes sense as its own roadmap of "
        "1-7 modules later. Order the courses from foundational to advanced and "
        "applied. Each course must have a UUID4 id, a clear title, a single-sentence "
        "learning outcome, and an order (1-based). "
        "Call the curriculum_planner tool with your result. Do not output any text "
        "outside the tool call."
    ),
}


def run(params: dict, mode: str = "learn") -> dict:
    """
    Validates and normalizes the model's tool-call arguments.
    Returns a normalized curriculum-plan dict or raises ValidationError.
    """
    data = {"curriculum": params.get("curriculum", params)}
    return normalize_curriculum_planner_output(data, mode=mode)
