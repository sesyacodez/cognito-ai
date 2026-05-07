"""
Decomposer skill — decomposes a topic or problem into a learning roadmap.

learn mode: 1–7 modules with learning outcomes sized to topic breadth.
solve mode: 1–5 modules with concrete deliverables (1 module if problem is simple).
"""

from utils.validators import normalize_decomposer_output, ValidationError

# ── Skill spec (sent to OpenRouter as a tool definition) ─────────────────────

SPEC = {
    "type": "function",
    "function": {
        "name": "decomposer",
        "description": (
            "Decomposes a topic or problem into a structured learning roadmap. "
            "In 'learn' mode, break the topic into 1–7 sequential modules based on breadth: "
            "use 1 module for a single method, function, syntax feature, or atomic concept; "
            "2–3 for narrow topics; 4–5 for broad topics; 6–7 only for comprehensive domains. "
            "Each module must have a clear learning outcome. "
            "In 'solve' mode, assess problem complexity: if simple (one clear task), "
            "return 1 module framed as a guided project; if complex, return 2–5 modules "
            "as sequential work steps with concrete deliverables. "
            "Always return ONLY valid JSON matching the parameters schema, no markdown fences."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic or problem the user wants to learn or solve.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["learn", "solve"],
                    "description": "Whether the user wants to learn a topic or solve a problem.",
                },
                "roadmap": {
                    "type": "object",
                    "description": "The generated roadmap.",
                    "properties": {
                        "topic": {"type": "string"},
                        "modules": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "A UUID4 string.",
                                    },
                                    "title": {"type": "string"},
                                    "outcome": {
                                        "type": "string",
                                        "description": (
                                            "Learning outcome (learn mode) or "
                                            "concrete deliverable (solve mode)."
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
                    "required": ["topic", "modules"],
                },
            },
            "required": ["topic", "mode", "roadmap"],
        },
    },
}


# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "learn": (
        "You are the Decomposer skill of a learning agent. "
        "Given a topic, choose the fewest sequential learning modules that teach it well. "
        "Use 1 module for one method, function, syntax feature, API call, or atomic concept "
        "(for example, Python str.split). Use 2–3 modules for narrow topics, 4–5 for broad "
        "topics, and 6–7 only for comprehensive domains or full curricula. "
        "Each module must have a UUID4 id, a title, a clear learning outcome, and an order (1-based). "
        "Call the decomposer tool with your result. Do not output any text outside the tool call."
    ),
    "solve": (
        "You are the Decomposer skill of a learning agent. "
        "Given a problem or task, assess its complexity. "
        "If simple (a single clear task), return exactly 1 module framing it as a guided project. "
        "If complex (multiple distinct steps), return 2–5 modules as sequential work steps. "
        "Each module must have a UUID4 id, a title, a concrete deliverable as its outcome, "
        "and an order (1-based). "
        "Call the decomposer tool with your result. Do not output any text outside the tool call."
    ),
}


# ── Skill implementation (called by runner after model selects the tool) ──────

def run(params: dict, mode: str = "learn") -> dict:
    """
    Validates and normalizes the model's tool-call arguments.
    Returns a normalized roadmap dict or raises ValidationError.
    """
    data = {"roadmap": params.get("roadmap", params)}
    return normalize_decomposer_output(data, mode=mode)
