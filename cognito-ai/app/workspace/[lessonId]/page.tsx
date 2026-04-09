"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import {
  fetchLesson,
  submitAnswer,
  requestHint,
  Lesson,
  LessonQuestion,
  AnswerResult,
  HintResult,
} from "@/lib/lessons";

/* ══════════════════════════════════════════════════
   Types
   ══════════════════════════════════════════════════ */

interface QuestionState {
  answer: string;
  submitted: boolean;
  correct: boolean | null;
  nextPrompt: string;
  hints: string[];
  hintLevel: number;
  starsRemaining: number;
  xp: number;
  isSubmitting: boolean;
  isLoadingHint: boolean;
  optimisticStatus: "idle" | "checking" | "correct" | "incorrect";
}

/* ══════════════════════════════════════════════════
   Main Component
   ══════════════════════════════════════════════════ */

export default function LearningWorkspace() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();

  const lessonId = params.lessonId as string;
  const moduleTopic = searchParams.get("topic") || "General Topic";
  const mode = searchParams.get("mode") || "learn";

  /* ── state ── */
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questionStates, setQuestionStates] = useState<
    Record<string, QuestionState>
  >({});
  const [totalXp, setTotalXp] = useState(0);
  const [lessonStatus, setLessonStatus] = useState<string>("not_started");
  const [showTheory, setShowTheory] = useState(true);
  const [showConfetti, setShowConfetti] = useState(false);
  const answerInputRef = useRef<HTMLTextAreaElement>(null);

  /* ── fetch lesson on mount ── */
  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchLesson(lessonId, moduleTopic, mode);
        if (cancelled) return;
        setLesson(data);

        // Initialize question states
        const states: Record<string, QuestionState> = {};
        data.questions.forEach((q) => {
          states[q.id] = {
            answer: "",
            submitted: false,
            correct: null,
            nextPrompt: "",
            hints: [],
            hintLevel: 0,
            starsRemaining: 3,
            xp: 0,
            isSubmitting: false,
            isLoadingHint: false,
            optimisticStatus: "idle",
          };
        });
        setQuestionStates(states);
      } catch (err) {
        if (cancelled) return;
        setError(
          err instanceof Error ? err.message : "Failed to load lesson"
        );
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [lessonId, moduleTopic, mode]);

  /* ── helpers ── */
  const currentQuestion: LessonQuestion | null =
    lesson?.questions[currentQuestionIndex] ?? null;
  const currentState: QuestionState | null = currentQuestion
    ? questionStates[currentQuestion.id] ?? null
    : null;
  const completedCount = Object.values(questionStates).filter(
    (s) => s.submitted
  ).length;
  const totalQuestions = lesson?.questions.length ?? 0;
  const progressPercent =
    totalQuestions > 0 ? (completedCount / totalQuestions) * 100 : 0;

  /* update a single question's state */
  const updateQState = useCallback(
    (qId: string, updates: Partial<QuestionState>) => {
      setQuestionStates((prev) => ({
        ...prev,
        [qId]: { ...prev[qId], ...updates },
      }));
    },
    []
  );

  /* ── submit answer with optimistic UI ── */
  async function handleSubmitAnswer() {
    if (!currentQuestion || !currentState) return;
    const answer = currentState.answer.trim();
    if (!answer) return;

    const qId = currentQuestion.id;

    // ① Optimistic: immediately show "checking" state
    updateQState(qId, {
      isSubmitting: true,
      optimisticStatus: "checking",
    });

    try {
      const result: AnswerResult = await submitAnswer(lessonId, qId, answer);

      // ② Update with real result
      updateQState(qId, {
        submitted: true,
        correct: result.correct,
        nextPrompt: result.next_prompt,
        xp: result.progress.xp,
        starsRemaining: result.progress.stars_remaining,
        isSubmitting: false,
        optimisticStatus: result.correct ? "correct" : "incorrect",
      });

      setTotalXp((prev) => prev + result.progress.xp);
      setLessonStatus(result.progress.status);

      // If completed, show confetti
      if (result.progress.status === "completed") {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 3000);
      }
    } catch (err) {
      // ③ Rollback optimistic state
      updateQState(qId, {
        isSubmitting: false,
        optimisticStatus: "idle",
      });
      setError(
        err instanceof Error ? err.message : "Failed to submit answer"
      );
    }
  }

  /* ── request hint with optimistic UI ── */
  async function handleRequestHint() {
    if (!currentQuestion || !currentState) return;
    if (currentState.hintLevel >= 3) return;

    const qId = currentQuestion.id;
    const nextHintLevel = currentState.hintLevel + 1;

    // ① Optimistic: show loading state and decrement stars
    updateQState(qId, {
      isLoadingHint: true,
      starsRemaining: Math.max(0, 3 - nextHintLevel),
    });

    try {
      const result: HintResult = await requestHint(
        lessonId,
        qId,
        nextHintLevel
      );

      // ② Update with real result
      updateQState(qId, {
        hints: [...currentState.hints, result.hint],
        hintLevel: nextHintLevel,
        starsRemaining: result.stars_remaining,
        isLoadingHint: false,
      });
    } catch (err) {
      // ③ Rollback
      updateQState(qId, {
        isLoadingHint: false,
        starsRemaining: Math.max(0, 3 - currentState.hintLevel),
      });
      setError(
        err instanceof Error ? err.message : "Failed to get hint"
      );
    }
  }

  /* ── navigate questions ── */
  function goToQuestion(index: number) {
    setCurrentQuestionIndex(index);
    setShowTheory(false);
    setTimeout(() => answerInputRef.current?.focus(), 100);
  }

  function goNext() {
    if (currentQuestionIndex < totalQuestions - 1) {
      goToQuestion(currentQuestionIndex + 1);
    }
  }

  /* ── render ── */

  /* Loading state */
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0b0f1e]">
        <div className="flex flex-col items-center gap-4">
          <div className="relative w-12 h-12">
            <div className="absolute inset-0 rounded-full border-2 border-gray-700" />
            <div className="absolute inset-0 rounded-full border-2 border-t-cyan-500 animate-spin" />
          </div>
          <p className="text-sm text-gray-400 animate-pulse">
            Loading lesson...
          </p>
        </div>
      </div>
    );
  }

  /* Error state */
  if (error && !lesson) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0b0f1e]">
        <div className="max-w-md text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="#ef4444"
                strokeWidth="1.5"
              />
              <path
                d="M12 8v4m0 4h.01"
                stroke="#ef4444"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-white mb-2">
            Failed to load lesson
          </h2>
          <p className="text-sm text-gray-400 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm rounded-lg transition"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!lesson) return null;

  return (
    <div className="flex min-h-screen h-screen bg-[#0b0f1e] font-sans overflow-hidden">
      {/* ═══ Confetti overlay ═══ */}
      {showConfetti && <ConfettiOverlay />}

      {/* ═══ LEFT PANEL: Theory + Question ═══ */}
      <div className="flex flex-col w-[55%] border-r border-gray-700/30">
        {/* Top bar */}
        <header className="flex items-center justify-between px-5 py-3 border-b border-gray-700/30 flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-700/30 transition focus:outline-none focus:ring-2 focus:ring-cyan-500"
              aria-label="Go back"
              title="Go back"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path
                  d="M19 12H5m0 0l7 7m-7-7l7-7"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
            <img
              src="/CognitoAI logo.svg"
              alt="CognitoAI"
              className="w-6 h-6"
              style={{ filter: "brightness(0) invert(1)" }}
            />
            <span className="text-sm font-bold text-white tracking-wider">
              COGNITO.AI
            </span>
            <span className="text-xs text-gray-500 ml-2">
              Learning Workspace
            </span>
          </div>

          {/* Progress + XP */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">XP</span>
              <span className="text-sm font-bold text-cyan-400">{totalXp}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-24 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-700 ease-out"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
              <span className="text-xs text-gray-400">
                {completedCount}/{totalQuestions}
              </span>
            </div>
          </div>
        </header>

        {/* Content area */}
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          {/* Module title */}
          <div className="px-6 pt-6 pb-2">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] uppercase tracking-wider text-cyan-400 font-semibold">
                {mode === "solve" ? "Problem" : "Topic"}
              </span>
              <span className="text-[10px] text-gray-600">•</span>
              <span className="text-[10px] text-gray-500">
                {lesson.lesson_id}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white">{moduleTopic}</h1>
          </div>

          {/* Theory section */}
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
                {lesson.micro_theory}
              </div>
            )}
          </div>

          {/* Question navigation pills */}
          <div className="px-6 py-3">
            <div className="flex items-center gap-2 flex-wrap">
              {lesson.questions.map((q: any, i: number) => {
                const qs = questionStates[q.id];
                const isActive = i === currentQuestionIndex;
                const isDone = qs?.submitted;
                const isCorrect = qs?.correct;

                let pillColor =
                  "bg-[#141a30] border-gray-700/40 text-gray-400";
                if (isActive)
                  pillColor =
                    "bg-cyan-500/15 border-cyan-500/40 text-cyan-300 ring-1 ring-cyan-500/20";
                if (isDone && isCorrect)
                  pillColor =
                    "bg-emerald-500/15 border-emerald-500/40 text-emerald-300";
                if (isDone && !isCorrect)
                  pillColor =
                    "bg-red-500/15 border-red-500/40 text-red-300";

                return (
                  <button
                    key={q.id}
                    onClick={() => goToQuestion(i)}
                    className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-[#0b0f1e] ${pillColor}`}
                    aria-label={`Go to Question ${i + 1}`}
                    aria-current={isActive ? "step" : undefined}
                  >
                    Q{i + 1}
                    {isDone && isCorrect && " ✓"}
                    {isDone && !isCorrect && " ✗"}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Current question */}
          {currentQuestion && currentState && (
            <div className="px-6 py-3">
              <QuestionCard
                question={currentQuestion}
                state={currentState}
                index={currentQuestionIndex}
                onAnswerChange={(val) =>
                  updateQState(currentQuestion.id, { answer: val })
                }
                onSubmit={handleSubmitAnswer}
                onHint={handleRequestHint}
                onNext={goNext}
                isLast={currentQuestionIndex >= totalQuestions - 1}
                inputRef={answerInputRef}
              />
            </div>
          )}
        </div>
      </div>

      {/* ═══ RIGHT PANEL: Progress & Feedback ═══ */}
      <div className="flex-1 flex flex-col bg-[#0d1220] min-w-0">
        {/* Panel header */}
        <header className="flex items-center justify-between px-5 py-3 border-b border-gray-700/30 flex-shrink-0">
          <div className="flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                stroke="#22d3ee"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span className="text-sm font-medium text-white">
              Progress & Feedback
            </span>
          </div>
          <StatusBadge status={lessonStatus} />
        </header>

        {/* Progress content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 scrollbar-thin">
          {/* Stars display */}
          {currentState && (
            <div className="bg-[#111830] rounded-xl border border-gray-700/30 p-5">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Current Question Stars
              </h3>
              <div className="flex items-center gap-1">
                {[1, 2, 3].map((star) => (
                  <svg
                    key={star}
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill={
                      star <= currentState.starsRemaining
                        ? "#facc15"
                        : "none"
                    }
                  >
                    <path
                      d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                      stroke={
                        star <= currentState.starsRemaining
                          ? "#facc15"
                          : "#4b5563"
                      }
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                ))}
                <span className="ml-2 text-sm text-gray-400">
                  {currentState.starsRemaining}/3 remaining
                </span>
              </div>
              <p className="mt-2 text-[11px] text-gray-500">
                Each hint used deducts one star. No hints = max XP!
              </p>
            </div>
          )}

          {/* XP summary */}
          <div className="bg-[#111830] rounded-xl border border-gray-700/30 p-5">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              XP Earned
            </h3>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-cyan-400">
                {totalXp}
              </span>
              <span className="text-sm text-gray-500">points</span>
            </div>
            <div className="mt-3 w-full h-2 bg-gray-700/50 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full transition-all duration-700 ease-out"
                style={{ width: `${Math.min((totalXp / 300) * 100, 100)}%` }}
              />
            </div>
            <p className="mt-1 text-[11px] text-gray-500">
              Max: 300 XP (100 per question, no hints)
            </p>
          </div>

          {/* Hints received */}
          {currentState && currentState.hints.length > 0 && (
            <div className="bg-[#111830] rounded-xl border border-gray-700/30 p-5">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Hints Used
              </h3>
              <div className="space-y-2">
                {currentState.hints.map((hint, i) => (
                  <div
                    key={i}
                    className="flex gap-2 p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg"
                  >
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      className="flex-shrink-0 mt-0.5"
                    >
                      <path
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 01-4 0v-.531a3.374 3.374 0 00-.988-2.386l-.548-.547z"
                        stroke="#f59e0b"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <p className="text-sm text-amber-200/80">{hint}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI feedback */}
          {currentState && currentState.nextPrompt && (
            <div className="bg-[#111830] rounded-xl border border-gray-700/30 p-5">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                AI Feedback
              </h3>
              <div
                className={`p-4 rounded-lg border ${
                  currentState.correct
                    ? "bg-emerald-500/5 border-emerald-500/20"
                    : "bg-red-500/5 border-red-500/20"
                }`}
              >
                <div className="flex items-start gap-2">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                      currentState.correct
                        ? "bg-emerald-500/20"
                        : "bg-red-500/20"
                    }`}
                  >
                    {currentState.correct ? (
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                      >
                        <path
                          d="M20 6L9 17l-5-5"
                          stroke="#10b981"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    ) : (
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                      >
                        <path
                          d="M18 6L6 18M6 6l12 12"
                          stroke="#ef4444"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    )}
                  </div>
                  <p
                    className={`text-sm leading-relaxed ${
                      currentState.correct
                        ? "text-emerald-200/80"
                        : "text-red-200/80"
                    }`}
                  >
                    {currentState.nextPrompt}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Question overview */}
          <div className="bg-[#111830] rounded-xl border border-gray-700/30 p-5">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
              Question Overview
            </h3>
            <div className="space-y-2">
              {lesson.questions.map((q: any, i: number) => {
                const qs = questionStates[q.id];
                return (
                  <button
                    key={q.id}
                    onClick={() => goToQuestion(i)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg transition text-left ${
                      i === currentQuestionIndex
                        ? "bg-cyan-500/10 border border-cyan-500/30"
                        : "bg-[#0d1220] border border-gray-700/20 hover:border-gray-600/40"
                    }`}
                  >
                    <QuestionStatusIcon state={qs} />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-300 truncate">
                        Question {i + 1}
                      </p>
                      <p className="text-[11px] text-gray-500 truncate">
                        {q.prompt}
                      </p>
                    </div>
                    <DifficultyBadge difficulty={q.difficulty} />
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Lesson complete button */}
        {lessonStatus === "completed" && (
          <div className="px-5 pb-5 pt-2 flex-shrink-0">
            <button
              onClick={() => router.push("/insight-hub")}
              className="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-xl transition-all text-sm shadow-lg shadow-cyan-500/20 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-[#0d1220]"
            >
              🎉 Lesson Complete! Return to Hub
            </button>
          </div>
        )}
      </div>

      {/* Global error toast */}
      {error && lesson && <ErrorToast message={error} onClose={() => setError("")} />}

      {/* Animations */}
      <style jsx global>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.2); }
          50% { box-shadow: 0 0 0 8px rgba(34, 211, 238, 0); }
        }
        .animate-pulse-glow {
          animation: pulse-glow 2s ease-in-out infinite;
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-4px); }
          75% { transform: translateX(4px); }
        }
        .animate-shake {
          animation: shake 0.4s ease-out;
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-slideUp {
          animation: slideUp 0.4s ease-out;
        }
        .scrollbar-thin::-webkit-scrollbar {
          width: 6px;
        }
        .scrollbar-thin::-webkit-scrollbar-track {
          background: transparent;
        }
        .scrollbar-thin::-webkit-scrollbar-thumb {
          background: rgba(100, 116, 139, 0.3);
          border-radius: 3px;
        }
        .scrollbar-thin::-webkit-scrollbar-thumb:hover {
          background: rgba(100, 116, 139, 0.5);
        }
      `}</style>
    </div>
  );
}

/* ══════════════════════════════════════════════════
   Sub-Components
   ══════════════════════════════════════════════════ */

function QuestionCard({
  question,
  state,
  index,
  onAnswerChange,
  onSubmit,
  onHint,
  onNext,
  isLast,
  inputRef,
}: {
  question: LessonQuestion;
  state: QuestionState;
  index: number;
  onAnswerChange: (val: string) => void;
  onSubmit: () => void;
  onHint: () => void;
  onNext: () => void;
  isLast: boolean;
  inputRef: React.RefObject<HTMLTextAreaElement | null>;
}) {
  return (
    <div
      className={`bg-[#111830] rounded-xl border p-5 transition-all animate-slideUp ${
        state.optimisticStatus === "correct"
          ? "border-emerald-500/40"
          : state.optimisticStatus === "incorrect"
            ? "border-red-500/40 animate-shake"
            : "border-gray-700/30"
      }`}
    >
      {/* Question header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-cyan-400">
            Question {index + 1}
          </span>
          <DifficultyBadge difficulty={question.difficulty} />
        </div>
        {state.submitted && (
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              state.correct
                ? "bg-emerald-500/15 text-emerald-300"
                : "bg-red-500/15 text-red-300"
            }`}
          >
            {state.correct ? "Correct ✓" : "Incorrect ✗"}
          </span>
        )}
      </div>

      {/* Prompt */}
      <p className="text-sm text-gray-200 leading-relaxed mb-4">
        {question.prompt}
      </p>

      {/* Answer input */}
      <div
        className={`relative rounded-lg border transition-colors ${
          state.submitted
            ? state.correct
              ? "border-emerald-500/30 bg-emerald-500/5"
              : "border-red-500/30 bg-red-500/5"
            : "border-gray-700/40 bg-[#0d1220] focus-within:border-cyan-500/40"
        }`}
      >
        <textarea
          ref={inputRef}
          value={state.answer}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => onAnswerChange(e.target.value)}
          onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
            if (e.key === "Enter" && !e.shiftKey && !state.submitted) {
              e.preventDefault();
              onSubmit();
            }
          }}
          placeholder="Type your answer here..."
          disabled={state.submitted || state.isSubmitting}
          rows={3}
          aria-label="Your answer"
          className="w-full bg-transparent text-sm text-white placeholder-gray-600 outline-none resize-none p-3 disabled:opacity-60 focus:ring-0"
        />

        {/* Checking indicator */}
        {state.optimisticStatus === "checking" && (
          <div className="absolute top-3 right-3 flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs text-cyan-400">Checking...</span>
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-between mt-4">
        <div className="flex items-center gap-2">
          {/* Hint button */}
          {!state.submitted && (
            <button
              onClick={onHint}
              disabled={state.hintLevel >= 3 || state.isLoadingHint}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/20 hover:bg-amber-500/20 transition disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-[#111830]"
              aria-label={`Request hint ${state.hintLevel + 1}`}
            >
              {state.isLoadingHint ? (
                <div className="w-3 h-3 border border-amber-400 border-t-transparent rounded-full animate-spin" />
              ) : (
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 01-4 0v-.531a3.374 3.374 0 00-.988-2.386l-.548-.547z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
              Hint ({state.hintLevel}/3)
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Submit */}
          {!state.submitted && (
            <button
              onClick={onSubmit}
              disabled={
                !state.answer.trim() || state.isSubmitting
              }
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium bg-cyan-600 hover:bg-cyan-500 text-white transition disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-[#111830]"
            >
              {state.isSubmitting ? (
                <>
                  <div className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  Submit
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M5 12h14M12 5l7 7-7 7"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </>
              )}
            </button>
          )}

          {/* Next question */}
          {state.submitted && !isLast && (
            <button
              onClick={onNext}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium bg-cyan-600 hover:bg-cyan-500 text-white transition animate-pulse-glow focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-[#111830]"
            >
              Next Question
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path
                  d="M5 12h14M12 5l7 7-7 7"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function DifficultyBadge({
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

function StatusBadge({ status }: { status: string }) {
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

function QuestionStatusIcon({ state }: { state: QuestionState | undefined }) {
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

function ErrorToast({
  message,
  onClose,
}: {
  message: string;
  onClose: () => void;
}) {
  useEffect(() => {
    const t = setTimeout(onClose, 5000);
    return () => clearTimeout(t);
  }, [message, onClose]);

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-slideUp">
      <div className="flex items-center gap-3 px-4 py-3 bg-red-950/90 border border-red-700/50 rounded-xl shadow-2xl backdrop-blur-sm">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="#ef4444" strokeWidth="1.5" />
          <path
            d="M12 8v4m0 4h.01"
            stroke="#ef4444"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
        <span className="text-sm text-red-200">{message}</span>
        <button
          onClick={onClose}
          className="text-red-400 hover:text-red-300 transition"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M18 6L6 18M6 6l12 12"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

function ConfettiOverlay() {
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {Array.from({ length: 40 }).map((_, i) => {
        const left = Math.random() * 100;
        const delay = Math.random() * 2;
        const duration = 2 + Math.random() * 2;
        const colors = [
          "#22d3ee",
          "#3b82f6",
          "#10b981",
          "#facc15",
          "#f472b6",
          "#a78bfa",
        ];
        const color = colors[i % colors.length];
        const size = 6 + Math.random() * 8;
        return (
          <div
            key={i}
            className="absolute rounded-sm"
            style={{
              left: `${left}%`,
              top: "-10px",
              width: `${size}px`,
              height: `${size}px`,
              backgroundColor: color,
              animation: `confetti-fall ${duration}s ease-in ${delay}s forwards`,
              transform: `rotate(${Math.random() * 360}deg)`,
            }}
          />
        );
      })}
      <style jsx>{`
        @keyframes confetti-fall {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}
