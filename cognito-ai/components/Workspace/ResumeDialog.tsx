"use client";

import React from "react";

type Props = {
  open: boolean;
  onContinue: () => void;
  onStartOver: () => void;
  isResetting?: boolean;
};

export default function ResumeDialog({ open, onContinue, onStartOver, isResetting }: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold">Resume lesson</h3>
        <p className="mt-2 text-sm text-gray-600">
          We found progress for this lesson. Would you like to continue where you left off or start
          over?
        </p>
        <div className="mt-4 flex gap-3 justify-end">
          <button
            className="px-4 py-2 rounded bg-gray-200"
            onClick={onStartOver}
            disabled={isResetting}
          >
            {isResetting ? "Resetting..." : "Start over"}
          </button>
          <button className="px-4 py-2 rounded bg-blue-600 text-white" onClick={onContinue}>
            Continue
          </button>
        </div>
      </div>
    </div>
  );
}
