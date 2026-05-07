"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import {
  Curriculum,
  CurriculumCourse,
  expandCourse,
  fetchCurriculum,
} from "@/lib/curriculums";

export default function CurriculumPage() {
  const params = useParams();
  const router = useRouter();
  const curriculumId = params.id as string;

  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandingCourseId, setExpandingCourseId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchCurriculum(curriculumId);
        if (!cancelled) setCurriculum(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load curriculum");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }
    if (curriculumId) load();
    return () => {
      cancelled = true;
    };
  }, [curriculumId]);

  async function handleOpenCourse(course: CurriculumCourse) {
    if (!curriculum) return;

    let roadmapId = course.roadmap_id;
    if (!roadmapId) {
      setExpandingCourseId(course.id);
      setError("");
      try {
        const result = await expandCourse(curriculum.curriculum_id, course.id);
        roadmapId = result.roadmap.roadmap_id;
        const refreshed = await fetchCurriculum(curriculum.curriculum_id);
        setCurriculum(refreshed);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to open course");
        return;
      } finally {
        setExpandingCourseId(null);
      }
    }

    if (!roadmapId) return;
    const qs = new URLSearchParams({
      topic: course.title,
      mode: curriculum.mode || "learn",
    });
    router.push(`/workspace/${roadmapId}-0?${qs.toString()}`);
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#0b0f1e] text-white font-sans px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => router.push("/insight-hub")}
            className="text-xs text-gray-400 hover:text-white mb-4 transition flex items-center gap-1"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
              <path d="M19 12H5M5 12l6-6m-6 6l6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            Back to Insight Hub
          </button>

          {isLoading && <p className="text-sm text-gray-400">Loading curriculum...</p>}
          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-sm text-red-200">
              {error}
            </div>
          )}

          {curriculum && (
            <>
              <header className="mb-8">
                <span className="inline-block text-[10px] uppercase tracking-wider text-purple-300 bg-purple-500/15 px-2 py-1 rounded-md mb-3">
                  Curriculum
                </span>
                <h1 className="text-2xl font-bold text-white">{curriculum.topic}</h1>
                <p className="text-sm text-gray-400 mt-2">
                  {curriculum.completed_courses}/{curriculum.course_count} courses completed
                  {" · "}
                  {curriculum.completed_modules}/{curriculum.module_count} modules done
                </p>
                <div className="mt-3 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                    style={{ width: `${curriculum.progress}%` }}
                  />
                </div>
              </header>

              <ol className="space-y-3">
                {curriculum.courses.map((course, i) => (
                  <CourseRow
                    key={course.id}
                    course={course}
                    index={i}
                    isExpanding={expandingCourseId === course.id}
                    onOpen={() => handleOpenCourse(course)}
                  />
                ))}
              </ol>
            </>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}

function CourseRow({
  course,
  index,
  isExpanding,
  onOpen,
}: {
  course: CurriculumCourse;
  index: number;
  isExpanding: boolean;
  onOpen: () => void;
}) {
  const statusLabel = (() => {
    if (!course.expanded) return "Locked";
    if (course.status === "completed") return "Completed";
    if (course.status === "in_progress") return "In progress";
    return "Ready";
  })();

  const statusClass = (() => {
    if (!course.expanded) return "bg-gray-700/40 text-gray-300";
    if (course.status === "completed") return "bg-green-500/15 text-green-300";
    if (course.status === "in_progress") return "bg-blue-500/15 text-blue-300";
    return "bg-purple-500/15 text-purple-300";
  })();

  const cta = !course.expanded
    ? isExpanding
      ? "Generating..."
      : "Generate this course"
    : "Open course";

  return (
    <li className="bg-[#111830] border border-gray-700/40 rounded-2xl p-4 flex items-start gap-4">
      <span className="w-9 h-9 rounded-full bg-[#0d1220] border border-gray-700/40 text-gray-400 text-sm font-bold flex items-center justify-center flex-shrink-0">
        {index + 1}
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="text-base font-semibold text-white truncate">
              {course.title}
            </h3>
            <p className="text-xs text-gray-400 mt-1 line-clamp-2">{course.outcome}</p>
          </div>
          <span className={`text-[10px] uppercase tracking-wide px-2 py-1 rounded-md ${statusClass} flex-shrink-0`}>
            {statusLabel}
          </span>
        </div>

        {course.expanded && course.module_count !== undefined && (
          <p className="text-[11px] text-gray-500 mt-2">
            {course.completed_modules ?? 0}/{course.module_count} modules done
          </p>
        )}

        <button
          onClick={onOpen}
          disabled={isExpanding}
          className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-xs font-medium rounded-xl transition"
        >
          {cta}
        </button>
      </div>
    </li>
  );
}
