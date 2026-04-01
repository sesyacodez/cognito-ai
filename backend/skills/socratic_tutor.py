"""
Socratic_Tutor skill — evaluates student answers and provides guiding hints.
Never reveals the direct answer. Always asks a follow-up guiding question.
"""

from utils.validators import normalize_evaluation_output, ValidationError

# ── Skill spec (sent to OpenRouter as a tool definition) ─────────────────────

SPEC = {
    "type": "function",
    "function": {
        "name": "socratic_tutor",
        "description": (
            "Evaluates a student's answer and returns a guiding Socratic prompt. "
            "If the answer is correct, acknowledge it and ask a deepening follow-up question. "
            "If the answer is incorrect, point out a mistake without giving the answer "
            "and ask a guiding question to nudge them closer. "
            "If a hint is requested (hint_level > 0), provide a tiered hint. "
            "Always return ONLY valid JSON matching the parameters schema, no markdown fences."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "evaluation": {
                    "type": "object",
                    "description": "The evaluation result.",
                    "properties": {
                        "correct": {
                            "type": "boolean",
                            "description": "True if the student's answer is correct.",
                        },
                        "next_prompt": {
                            "type": "string",
                            "description": "A Socratic guiding question.",
                        },
                        "hint": {
                            "type": "string",
                            "description": "A hint if a hint_level was specified.",
                        },
                    },
                    "required": ["correct", "next_prompt"],
                },
            },
            "required": ["evaluation"],
        },
    },
}


# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "learn": (
        "You are the Socratic_Tutor skill of a learning agent. "
        "Your goal is to guide the student to the answer without ever giving it directly. "
        "Evaluate the student's answer against the question prompt and expected answer. "
        "If correct: Acknowledge, then ask a question that explores a related or advanced concept. "
        "If incorrect: Mention one specific area of confusion and ask a guiding question to help them rethink. "
        "If hint requested (hint_level > 0): Provide a hint proportional to the level (1=gentle nudge, 2=partial reveal, 3=strong hint minus answer). "
        "Call the socratic_tutor tool with your result. Do not output any text outside the tool call."
    )
}


# ── Skill implementation (called by runner after model selects the tool) ──────

def run(params: dict, mode: str = "learn") -> dict:
    """
    Validates and normalizes the evaluation result.
    """
    # SPEC says it's root + 'evaluation'
    data = params.get("evaluation", params)
    return normalize_evaluation_output(data)
