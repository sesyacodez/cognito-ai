import React from "react";
import { QuestionState } from "@/types/workspace";

export function DifficultyBadge({
  difficulty,
}: {
  difficulty: "easy" | "medium" | "hard";
}) {
  const colors = {
    easy: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
    medium: "bg-amber-500/15 text-amber-300 border-amber-500/20",
    hard: "bg-red-500/15 text-red-300 border-red-500/20",
  };
  return (
    <span
      className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${colors[difficulty]}`}
    >
      {difficulty}
    </span>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    not_started: "bg-gray-700/30 text-gray-400 border-gray-600/30",
    in_progress: "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
    completed: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  };
  const labels: Record<string, string> = {
    not_started: "Not Started",
    in_progress: "In Progress",
    completed: "Completed",
  };
  return (
    <span
      className={`text-[10px] font-medium px-2.5 py-1 rounded-full border ${styles[status] || styles.not_started}`}
    >
      {labels[status] || status}
    </span>
  );
}

export function QuestionStatusIcon({ state }: { state: QuestionState | undefined }) {
  if (!state || !state.submitted) {
    return (
      <div className="w-6 h-6 rounded-full border border-gray-600 flex items-center justify-center">
        <div className="w-2 h-2 rounded-full bg-gray-600" />
      </div>
    );
  }
  if (state.correct) {
    return (
      <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
          <path
            d="M20 6L9 17l-5-5"
            stroke="#10b981"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    );
  }
  return (
    <div className="w-6 h-6 rounded-full bg-red-500/20 flex items-center justify-center">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
        <path
          d="M18 6L6 18M6 6l12 12"
          stroke="#ef4444"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}
