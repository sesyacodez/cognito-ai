/**
 * Lessons API client — integrates with GET /api/lessons/{id},
 * POST /api/lessons/{id}/answer, POST /api/lessons/{id}/hint,
 * POST /api/lessons/{id}/reset, DELETE /api/lessons/{id}/state.
 */

import { getAuthHeader } from "./auth";

/* ── Types ─────────────────────────────────────── */

export interface LessonQuestion {
  id: string;
  prompt: string;
  difficulty: "easy" | "medium" | "hard";
}

export interface QuestionProgress {
  question_id: string;
  answered: boolean;
  correct: boolean | null;
  hints_used: number;
  answer: string;
}

export interface LessonProgress {
  status: "not_started" | "in_progress" | "completed";
  xp_earned: number;
  stars_remaining: number;
  last_question_id: string | null;
  updated_at: string;
  questions: Record<string, QuestionProgress>;
}

export interface Lesson {
  lesson_id: string;
  mode: string;
  micro_theory: string;
  questions: LessonQuestion[];
  progress?: LessonProgress;
}

export interface AnswerResult {
  correct: boolean;
  next_prompt: string;
  progress: {
    xp: number;
    star_earned: boolean;
    total_stars: number;
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

export async function resetLesson(
  lessonId: string
): Promise<{ status: string; xp_earned: number; stars_remaining: number }> {
  const res = await fetch(`/api/lessons/${lessonId}/reset`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to reset lesson: ${res.status}`);
  }
  return res.json();
}

export async function deleteLesson(lessonId: string): Promise<void> {
  const res = await fetch(`/api/lessons/${lessonId}/state`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
  });
  if (!res.ok) {
    throw new Error(`Failed to delete lesson progress: ${res.status}`);
  }
}
