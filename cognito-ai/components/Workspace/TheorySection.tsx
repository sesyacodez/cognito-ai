import React from "react";

interface TheorySectionProps {
  showTheory: boolean;
  setShowTheory: (show: boolean) => void;
  microTheory: string;
}

export function TheorySection({ showTheory, setShowTheory, microTheory }: TheorySectionProps) {
  return (
    <div className="px-6 py-3">
      <button
        onClick={() => setShowTheory(!showTheory)}
        className="flex items-center gap-2 text-sm font-medium text-gray-300 hover:text-white transition group focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded-lg p-1 -m-1"
        aria-expanded={showTheory}
        aria-controls="micro-theory-content"
      >
        <div className="w-6 h-6 rounded bg-cyan-500/10 flex items-center justify-center group-hover:bg-cyan-500/20 transition">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5A2.5 2.5 0 004 17V4a1 1 0 011-1h15v13H6.5A2.5 2.5 0 004 19.5z"
              stroke="#22d3ee"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        Micro Theory
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          className={`transition-transform ${showTheory ? "rotate-180" : ""}`}
        >
          <path
            d="M6 9l6 6 6-6"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {showTheory && (
        <div className="mt-3 p-4 bg-[#111830] rounded-xl border border-gray-700/30 text-sm text-gray-300 leading-relaxed animate-fadeIn">
          {microTheory}
        </div>
      )}
    </div>
  );
}
