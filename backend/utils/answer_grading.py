"""
Deterministic answer checking against stored answer keys.

Used as the source of truth for `correct` in lesson flows; the Socratic tutor
still supplies pedagogical `next_prompt` / hints when the LLM is available.
"""

from __future__ import annotations

import re


def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def _split_acceptable_keys(answer_key: str) -> list[str]:
    """
    Split on | for multiple acceptable phrasings, e.g. "yes|y|true".
    """
    parts = [p.strip() for p in answer_key.split("|")]
    return [p for p in parts if p]


def is_answer_correct_against_key(student_answer: str, answer_key: str) -> bool:
    """
    Return True if the student's answer matches the key using conservative rules.

    - Empty student answer is always incorrect.
    - Empty key cannot be satisfied (treated as incorrect).
    - Multiple alternatives separated by | are OR-ed.
    - Case-insensitive comparison with collapsed whitespace.
    - Substring match in either direction for short answers.
    - For longer student text, any substantive token from the key (>2 chars) appearing
      in the student answer counts as a weak match (same spirit as legacy evaluate_answer_local).
    """
    student_clean = _normalize_ws(student_answer).lower()
    if not student_clean:
        return False

    key_raw = answer_key.strip()
    if not key_raw:
        return False

    for alt in _split_acceptable_keys(key_raw):
        key_clean = _normalize_ws(alt).lower()
        if not key_clean:
            continue
        if key_clean in student_clean or student_clean in key_clean:
            return True
        if len(student_clean) > 10 and any(
            len(w) > 2 and w in student_clean for w in key_clean.split()
        ):
            return True

    return False
