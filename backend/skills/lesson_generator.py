"""
Lesson_Generator skill — generates micro-theory (<=120 words) and 3 difficulty-graded questions.
"""

from utils.validators import normalize_lesson_output, ValidationError

# ── Skill spec (sent to OpenRouter as a tool definition) ─────────────────────

SPEC = {
    "type": "function",
    "function": {
        "name": "lesson_generator",
        "description": (
            "Generates educational micro-theory and three graduated questions (easy, medium, hard). "
            "In 'learn' mode, the theory explains a module concept clearly and concisely (<= 120 words). "
            "In 'solve' mode, frame theory as a problem/task brief; questions as guided implementation tasks. "
            "Always return ONLY valid JSON matching the parameters schema, no markdown fences."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "module_topic": {
                    "type": "string",
                    "description": "The sub-topic or task this lesson should cover.",
                },
                "target_difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "The baseline difficulty of the lesson.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["learn", "solve"],
                    "description": "Whether the user wants to learn a topic or solve a problem.",
                },
                "lesson": {
                    "type": "object",
                    "description": "The generated lesson content.",
                    "properties": {
                        "micro_theory": {
                            "type": "string",
                            "description": "Educational content (learn mode) or problem brief (solve mode). Max 120 words.",
                        },
                        "questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "A unique UUID4-style string.",
                                    },
                                    "prompt": {
                                        "type": "string",
                                        "description": "The question or task prompt.",
                                    },
                                    "difficulty": {
                                        "type": "string",
                                        "enum": ["easy", "medium", "hard"],
                                        "description": "Graduated difficulty.",
                                    },
                                    "answer_key": {
                                        "type": "string",
                                        "description": "The correct answer or expected result for evaluation.",
                                    },
                                },
                                "required": ["id", "prompt", "difficulty", "answer_key"],
                            },
                        },
                    },
                    "required": ["micro_theory", "questions"],
                },
            },
            "required": ["module_topic", "mode", "lesson"],
        },
    },
}


# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "learn": (
        "You are the Lesson_Generator skill of a learning agent. "
        "Given a module topic, generate a concise micro-theory (max 120 words) explaining the concept. "
        "The theory must be clear, educational, and avoid fluff. "
        "Then generate exactly 3 graduated questions: one easy, one medium, one hard. "
        "The answer_key should be the definitive correct answer. "
        "Call the lesson_generator tool with your result. Do not output any text outside the tool call."
    ),
    "solve": (
        "You are the Lesson_Generator skill of a learning agent. "
        "Given a module task/problem, generate a lesson brief (max 120 words). "
        "Frame the theory as a project or problem brief. "
        "Then generate exactly 3 graduated implementation tasks as questions: "
        "an easy setup task, a medium core task, and a hard optimization or extension task. "
        "The answer_key should describe the expected result for evaluation. "
        "Call the lesson_generator tool with your result. Do not output any text outside the tool call."
    ),
}


# ── Skill implementation (called by runner after model selects the tool) ──────

def run(params: dict, mode: str = "learn") -> dict:
    """
    Validates and normalizes the model's tool-call arguments.
    Returns a normalized lesson dict or raises ValidationError.
    """
    # The runner might pass it as separate args or nested.
    # The SPEC says it's root + 'lesson'
    data = {"lesson": params.get("lesson", params)}
    return normalize_lesson_output(data, mode=mode)
