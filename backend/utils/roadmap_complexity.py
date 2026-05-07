from __future__ import annotations

import re


_ATOMIC_TOPIC_TERMS = {
    "attribute",
    "function",
    "keyword",
    "method",
    "operator",
    "property",
    "syntax",
}

_NARROW_PROGRAMMING_TERMS = {
    "append",
    "filter",
    "find",
    "join",
    "len",
    "map",
    "pop",
    "reduce",
    "replace",
    "slice",
    "sort",
    "split",
    "strip",
}

_BROAD_TOPIC_TERMS = {
    "architecture",
    "complete",
    "comprehensive",
    "curriculum",
    "deep dive",
    "end to end",
    "full",
    "fundamentals",
    "master",
    "roadmap",
}


def _topic_words(topic: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", topic.lower())


def estimate_module_count(topic: str, mode: str = "learn") -> int:
    """
    Estimate how many lessons a roadmap needs before model generation.

    The goal is to avoid turning atomic concepts, such as a single Python
    method, into a mini-course while still allowing broad topics to expand.
    """
    topic_clean = topic.strip() or "General Learning Path"
    mode_clean = "solve" if str(mode).strip().lower() == "solve" else "learn"
    words = _topic_words(topic_clean)
    word_count = len(words)
    word_set = set(words)
    lowered = topic_clean.lower()

    if mode_clean == "solve":
        if word_count <= 4:
            return 1
        if word_count <= 10:
            return 3
        return 5

    has_atomic_marker = bool(word_set & _ATOMIC_TOPIC_TERMS)
    has_narrow_programming_term = bool(word_set & _NARROW_PROGRAMMING_TERMS)
    if has_atomic_marker and has_narrow_programming_term:
        return 1
    if re.search(r"\b(str|string|list|dict|array)\s*[.#]?\s*\w+\b", lowered) and has_atomic_marker:
        return 1

    broad_signals = sum(1 for term in _BROAD_TOPIC_TERMS if term in lowered)
    if broad_signals >= 2:
        return 6
    if broad_signals == 1 and word_count >= 4:
        return 5

    if word_count <= 3:
        return 2 if has_narrow_programming_term else 3
    if word_count <= 7:
        return 3 if has_narrow_programming_term else 4
    if word_count <= 12:
        return 5
    if word_count <= 18:
        return 6
    return 7


def trim_modules_to_estimated_count(modules: list[dict], topic: str, mode: str = "learn") -> list[dict]:
    module_count = min(len(modules), estimate_module_count(topic, mode=mode))
    return modules[:module_count]
