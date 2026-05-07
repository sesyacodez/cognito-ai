"use client";

import React, { useEffect, useState } from "react";

type Props = {
  question: {
    id: string;
    prompt: string;
    placeholder?: string;
    hint?: string;
    explanation?: string;
  };
  answer: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  onGetHint?: () => void;
  disabled?: boolean;
  // from WorkspaceClient
  showHint?: boolean;
  isCorrect?: boolean | null; // true = correct, false = incorrect, null = not graded yet
  onToggleTutor?: () => void;
};

export default function QuestionCard({
  question,
  answer,
  onChange,
  onSubmit,
  onGetHint,
  disabled,
  showHint = false,
  isCorrect = null,
  onToggleTutor,
}: Props) {
  const [localShowHint, setLocalShowHint] = useState<boolean>(!!showHint);
  const [shaking, setShaking] = useState(false);

  // keep local showHint in sync with prop
  useEffect(() => {
    setLocalShowHint(!!showHint);
  }, [showHint]);

  // trigger shake animation when answer is marked incorrect
  useEffect(() => {
    if (isCorrect === false) {
      setShaking(true);
      const t = setTimeout(() => setShaking(false), 650);
      return () => clearTimeout(t);
    }
    return;
  }, [isCorrect]);

  const handleGetHint = () => {
    // prefer parent handler; otherwise toggle locally
    if (onGetHint) {
      onGetHint();
    } else {
      setLocalShowHint((s) => !s);
    }
  };

  const rootBorderClass = isCorrect === true ? "border-green-400 bg-green-900/10" : isCorrect === false ? "border-red-500 bg-red-900/10" : "border-gray-700/30";

  return (
    <div className={`rounded-2xl p-6 border ${rootBorderClass} ${shaking ? "shake" : ""} bg-[#0d1222]`}>
      <h3 className="text-sm font-semibold text-white mb-3">Question</h3>

      <p className="text-sm text-gray-300 mb-4">{question.prompt}</p>

      <textarea
        value={answer}
        onChange={(e) => onChange(e.target.value)}
        placeholder={question.placeholder || "Write your answer here..."}
        className="w-full min-h-[120px] p-3 bg-[#0b0f1e] border border-gray-800 rounded-lg text-white focus-visible:outline-blue-400"
        aria-label="Answer input"
        disabled={disabled}
      />

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={onSubmit}
          disabled={disabled}
          className="px-4 py-2 bg-cyan-600 text-white rounded-lg disabled:opacity-50"
          aria-disabled={disabled}
        >
          Submit
        </button>

        <button
          onClick={() => onToggleTutor && onToggleTutor()}
          className="px-3 py-2 bg-indigo-600 text-white rounded-lg flex items-center gap-2"
          title="Socratic help"
        >
          <span className="text-lg">💡</span>
          <span className="text-sm">Не розумію, поясни</span>
        </button>

        {question.hint || onGetHint ? (
          <button
            onClick={handleGetHint}
            disabled={disabled}
            className="px-3 py-2 bg-gray-800 text-gray-200 rounded-lg"
            aria-pressed={localShowHint}
            aria-controls={`hint-${question.id}`}
          >
            {localShowHint ? "Hide hint" : "Hint"}
          </button>
        ) : null}
      </div>

      {/* hint & explanation area */}
      <div className="mt-4" aria-live="polite">
        {localShowHint && question.hint ? (
          <div id={`hint-${question.id}`} className="p-3 rounded-md bg-gray-800/60 text-gray-200">
            <strong className="text-sm text-white">Hint:</strong>
            <p className="mt-1 text-sm">{question.hint}</p>
          </div>
        ) : null}

        {isCorrect === false && question.explanation ? (
          <div className="mt-3 p-3 rounded-md bg-red-900/20 text-red-200">
            <strong className="text-sm text-red-100">Explanation:</strong>
            <p className="mt-1 text-sm">{question.explanation}</p>
          </div>
        ) : null}

        {isCorrect === true ? (
          <div className="mt-3 p-3 rounded-md bg-green-900/20 text-green-200">
            <strong className="text-sm text-green-100">Nice work — that looks correct.</strong>
          </div>
        ) : null}
      </div>

      <style jsx>{`
        @keyframes shakeX {
          0% { transform: translateX(0); }
          15% { transform: translateX(-8px); }
          30% { transform: translateX(8px); }
          45% { transform: translateX(-6px); }
          60% { transform: translateX(6px); }
          75% { transform: translateX(-2px); }
          100% { transform: translateX(0); }
        }
        .shake {
          animation: shakeX 650ms ease-in-out;
        }
      `}</style>
    </div>
  );
}
