/**
 * Curriculum API client - handles broad-topic preview, confirmation,
 * fetching curricula, and expanding courses on demand.
 */

import { readHttpErrorMessage } from "./apiErrors";
import { getAuthHeader } from "./auth";

/* ── Types ─────────────────────────────────────── */

export interface RoadmapModuleSummary {
  id: string;
  title: string;
  index: number;
  order: number;
  outcome: string;
  description: string;
  lesson_status?: "not_started" | "in_progress" | "completed";
  xp_earned?: number;
  stars_remaining?: number;
}

export interface RoadmapPayload {
  roadmap_id: string;
  id: string;
  topic: string;
  mode: string;
  type: "topic" | "problem";
  created_at: string;
  createdAt: string;
  progress: number;
  modules: RoadmapModuleSummary[];
}

export interface CurriculumCoursePlan {
  id: string;
  index: number;
  title: string;
  outcome: string;
}

export interface CurriculumCourse extends CurriculumCoursePlan {
  order: number;
  description: string;
  status: "not_started" | "in_progress" | "completed";
  expanded: boolean;
  roadmap_id: string | null;
  module_count?: number;
  completed_modules?: number;
  in_progress_modules?: number;
  progress?: number;
}

export interface CurriculumPlan {
  topic: string;
  mode: string;
  courses: CurriculumCoursePlan[];
  source?: "agent" | "placeholder";
}

export interface Curriculum {
  curriculum_id: string;
  id: string;
  topic: string;
  mode: string;
  kind: "curriculum";
  created_at: string;
  createdAt: string;
  courses: CurriculumCourse[];
  module_count: number;
  completed_modules: number;
  progress: number;
  course_count: number;
  completed_courses: number;
  first_course_id?: string | null;
  first_roadmap?: RoadmapPayload | null;
}

export type CreateJourneyResponse =
  | { kind: "roadmap"; roadmap: RoadmapPayload }
  | { kind: "curriculum_preview"; plan: CurriculumPlan };

export interface ExpandCourseResponse {
  course_id: string;
  curriculum_id: string;
  roadmap: RoadmapPayload;
}

/* ── API calls ─────────────────────────────────── */

export async function createJourney(
  topic: string,
  mode: "learn" | "solve",
  options: { forceRoadmap?: boolean } = {}
): Promise<CreateJourneyResponse> {
  const res = await fetch("/api/roadmaps", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({
      topic,
      mode,
      force_roadmap: options.forceRoadmap === true,
    }),
  });

  if (!res.ok) {
    throw new Error(await readHttpErrorMessage(res, "Failed to create journey"));
  }

  return res.json();
}

export async function confirmCurriculum(
  topic: string,
  mode: "learn" | "solve",
  courses: CurriculumCoursePlan[]
): Promise<Curriculum> {
  const res = await fetch("/api/curriculums", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({
      topic,
      mode,
      courses: courses.map((c) => ({
        title: c.title,
        outcome: c.outcome,
        index: c.index,
      })),
    }),
  });

  if (!res.ok) {
    throw new Error(await readHttpErrorMessage(res, "Failed to create curriculum"));
  }

  return res.json();
}

export async function fetchCurriculum(curriculumId: string): Promise<Curriculum> {
  const res = await fetch(`/api/curriculums/${curriculumId}`, {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
  });

  if (!res.ok) {
    throw new Error(await readHttpErrorMessage(res, "Failed to fetch curriculum"));
  }

  return res.json();
}

export async function listCurriculums(): Promise<Curriculum[]> {
  const res = await fetch("/api/curriculums", {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
  });

  if (!res.ok) {
    throw new Error(await readHttpErrorMessage(res, "Failed to list curriculums"));
  }

  return res.json();
}

export async function expandCourse(
  curriculumId: string,
  courseId: string
): Promise<ExpandCourseResponse> {
  const res = await fetch(
    `/api/curriculums/${curriculumId}/courses/${courseId}/expand`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
    }
  );

  if (!res.ok) {
    throw new Error(await readHttpErrorMessage(res, "Failed to expand course"));
  }

  return res.json();
}
