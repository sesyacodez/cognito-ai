/**
 * Lessons API client — integrates with GET /api/lessons/{id},
 * POST /api/lessons/{id}/answer, POST /api/lessons/{id}/hint.
 */

import { getAuthHeader } from "./auth";

/* ── Types ─────────────────────────────────────── */

export interface LessonQuestion {
  id: string;
  prompt: string;
  difficulty: "easy" | "medium" | "hard";
}

export interface Lesson {
  lesson_id: string;
  mode: string;
  micro_theory: string;
  questions: LessonQuestion[];
}

export interface AnswerResult {
  correct: boolean;
  next_prompt: string;
  progress: {
    xp: number;
    stars_remaining: number;
    status: "not_started" | "in_progress" | "completed";
  };
}

export interface HintResult {
  hint: string;
  stars_remaining: number;
}

/* ── API calls ─────────────────────────────────── */

export async function fetchLesson(
  lessonId: string,
  moduleTopic: string,
  mode: string = "learn"
): Promise<Lesson> {
  const params = new URLSearchParams({ module_topic: moduleTopic, mode });
  const res = await fetch(`/api/lessons/${lessonId}?${params}`, {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch lesson: ${res.status}`);
  }
  return res.json();
}

export async function submitAnswer(
  lessonId: string,
  questionId: string,
  answer: string
): Promise<AnswerResult> {
  const res = await fetch(`/api/lessons/${lessonId}/answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({ question_id: questionId, answer }),
  });
  if (!res.ok) {
    throw new Error(`Failed to submit answer: ${res.status}`);
  }
  return res.json();
}

export async function requestHint(
  lessonId: string,
  questionId: string,
  hintLevel: number
): Promise<HintResult> {
  const res = await fetch(`/api/lessons/${lessonId}/hint`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({ question_id: questionId, hint_level: hintLevel }),
  });
  if (!res.ok) {
    throw new Error(`Failed to get hint: ${res.status}`);
  }
  return res.json();
}
