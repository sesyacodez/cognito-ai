"use client";

import React from "react";
import { useLessonWorkspace } from "@/hooks/useLessonWorkspace";
import LoadingState from "./LoadingState";
import ErrorState from "./ErrorState";
import ConfettiOverlay from "./ConfettiOverlay";
import QuestionCard from "./QuestionCard";
import { useWorkspaceShortcuts } from "@/hooks/useWorkspaceShortcuts";
import ProgressSidebar from "./ProgressSidebar";
import SocraticTutorPanel from "./SocraticTutorPanel";
import { fetchDashboard, DashboardData } from "@/lib/dashboard";
import ResumeDialog from "./ResumeDialog";
import NavigationPills from "./NavigationPills";
import CompletionFlow from "./CompletionFlow";

export default function WorkspaceClient({ lessonId }: { lessonId: string }) {
  const {
    lesson,
    isLoading,
    error,
    currentQuestionIndex,
    questionStates,
    totalXp,
  totalStars,
  lessonStatus,
    showConfetti,
    handleSubmitAnswer,
    handleRequestHint,
    updateQState,
  isTutorOpen,
  toggleTutor,
  goToQuestion,
  goNext,
  currentStreak: hookCurrentStreak,
  lessonsCompleted: hookLessonsCompleted,
  showResumeDialog,
  handleContinueLesson,
  handleStartOver,
  isResetting,
  } = useLessonWorkspace(lessonId, "", "learn");
  

  // prefer values from hook; fall back to local state if needed
  const [currentStreak, setCurrentStreak] = React.useState<number>(hookCurrentStreak ?? 0);
  const [lessonsCompleted, setLessonsCompleted] = React.useState<number>(hookLessonsCompleted ?? 0);

  // keep local mirrors in sync with hook-provided values
  React.useEffect(() => setCurrentStreak(hookCurrentStreak ?? 0), [hookCurrentStreak]);
  React.useEffect(() => setLessonsCompleted(hookLessonsCompleted ?? 0), [hookLessonsCompleted]);

  // local optimistic answer state (kept in sync with hook state)
  const [localAnswer, setLocalAnswer] = React.useState<string>("");

  const question = lesson?.questions?.[currentQuestionIndex];
  const qState = question ? questionStates[question.id] : undefined;

  React.useEffect(() => {
    // when question changes, seed local answer from hook state
    setLocalAnswer(qState?.answer || "");
  }, [qState?.answer, question?.id]);

  // keyboard shortcuts integration
  useWorkspaceShortcuts({
    enabled: true,
    submitAnswer: () => {
      if (question) handleSubmitAnswer(question.id, localAnswer);
    },
    goNext: () => {
      goNext();
    },
    toggleHint: () => {
      if (question) handleRequestHint(question.id);
    },
    selectOption: (idx: number) => {
      // if question has an options/choices array, optimistically set the answer
      if (!question) return;
      const opts = (question as any).options ?? (question as any).choices;
      const opt = Array.isArray(opts) ? opts[idx] : undefined;
      if (opt !== undefined) {
        setLocalAnswer(opt);
        updateQState(question.id, { answer: opt });
      }
    },
  });

  if (isLoading) return <LoadingState message="Loading lesson..." />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="relative flex-1 flex gap-6 p-6">
  <SocraticTutorPanel isOpen={isTutorOpen} onClose={toggleTutor} currentQuestionPrompt={question?.prompt} />
      <ConfettiOverlay active={showConfetti} />

      <ResumeDialog
        open={showResumeDialog}
        onContinue={handleContinueLesson}
        onStartOver={handleStartOver}
        isResetting={isResetting}
      />

      <main className="flex-1">
        {question ? (
          <>
            <div className="mb-4 flex items-center justify-between">
              <NavigationPills
                total={lesson?.questions?.length ?? 0}
                currentIndex={currentQuestionIndex}
                onJump={(i) => {
                  // jump navigation will set current question index via goToQuestion; we reuse updateQState as a no-op
                  if (lesson && lesson.questions?.[i]) {
                    updateQState(lesson.questions[i].id, {});
                  }
                }}
              />
            </div>

            <QuestionCard
              question={{ id: question.id, prompt: question.prompt }}
              answer={localAnswer}
              onChange={(v) => {
                setLocalAnswer(v);
                if (question) updateQState(question.id, { answer: v });
              }}
              onSubmit={() => handleSubmitAnswer(question.id, localAnswer)}
              onGetHint={() => handleRequestHint(question.id)}
              onToggleTutor={() => toggleTutor()}
              disabled={false}
            />
          </>
        ) : (
          <div className="p-6 text-gray-400">No question found.</div>
        )}
      </main>
      <aside className="w-64">
        {lessonStatus === "completed" ? (
          <CompletionFlow xpEarned={totalXp} starsEarned={totalStars} onClose={() => {}} />
        ) : (
          <ProgressSidebar totalXp={totalXp} totalStars={totalStars} currentStreak={currentStreak} lessonsCompleted={lessonsCompleted} />
        )}
      </aside>
    </div>
  );
}
