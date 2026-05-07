import { useState, useEffect, useRef, useCallback } from "react";
import {
  fetchLesson,
  submitAnswer,
  requestHint,
  resetLesson,
  Lesson,
  AnswerResult,
  HintResult,
} from "@/lib/lessons";
import { QuestionState } from "@/types/workspace";
import { initFreshStates, restoreProgressState } from "@/utils/workspaceHelpers";
import { fetchDashboard, DashboardData } from "@/lib/dashboard";

export function useLessonWorkspace(lessonId: string, moduleTopic: string, mode: string) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questionStates, setQuestionStates] = useState<Record<string, QuestionState>>({});
  const [totalXp, setTotalXp] = useState(0);
  const [totalStars, setTotalStars] = useState(0);
  const [lessonStatus, setLessonStatus] = useState<string>("not_started");
  const [showTheory, setShowTheory] = useState(true);
  const [showConfetti, setShowConfetti] = useState(false);
  const [showResumeDialog, setShowResumeDialog] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  // Socratic tutor panel state
  const [isTutorOpen, setIsTutorOpen] = useState(false);
  const [currentStreak, setCurrentStreak] = useState<number>(0);
  const [lessonsCompleted, setLessonsCompleted] = useState<number>(0);
  const pendingLessonRef = useRef<Lesson | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchLesson(lessonId, moduleTopic, mode);
        if (cancelled) return;
        setLesson(data);

        const hasProgress =
          data.progress &&
          data.progress.status !== "not_started" &&
          Object.keys(data.progress.questions).length > 0;

        if (hasProgress) {
          pendingLessonRef.current = data;
          setShowResumeDialog(true);
          setQuestionStates(initFreshStates(data));
        } else {
          setQuestionStates(initFreshStates(data));
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to load lesson");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [lessonId, moduleTopic, mode]);

  // fetch dashboard-derived values once per lesson load so hook is single source of truth
  useEffect(() => {
    let mounted = true;
    async function loadDashboard() {
      try {
        const data: DashboardData = await fetchDashboard();
        if (!mounted) return;
        setCurrentStreak(data.current_streak ?? 0);
        setLessonsCompleted(data.lessons_completed ?? 0);
      } catch {
        // ignore; non-critical
      }
    }
    loadDashboard();
    return () => {
      mounted = false;
    };
  }, [lessonId]);

  const updateQState = useCallback(
    (qId: string, updates: Partial<QuestionState>) => {
      setQuestionStates((prev) => ({
        ...prev,
        [qId]: { ...prev[qId], ...updates },
      }));
    },
    []
  );

  async function handleContinueLesson() {
    const data = pendingLessonRef.current || lesson;
    if (data?.progress) {
      const { states, firstUnansweredIdx } = restoreProgressState(data, data.progress);
      setQuestionStates(states);
      setTotalXp(data.progress.xp_earned);
      setTotalStars(data.progress.stars_remaining);
      setLessonStatus(data.progress.status);
      if (firstUnansweredIdx >= 0) {
        setCurrentQuestionIndex(firstUnansweredIdx);
        setShowTheory(false);
      }
    }
    setShowResumeDialog(false);
  }

  async function handleStartOver() {
    setIsResetting(true);
    try {
      await resetLesson(lessonId);
      const data = pendingLessonRef.current || lesson;
      if (data) {
        setQuestionStates(initFreshStates(data));
        setTotalXp(0);
        setLessonStatus("not_started");
        setCurrentQuestionIndex(0);
        setShowTheory(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset lesson");
    } finally {
      setIsResetting(false);
      setShowResumeDialog(false);
    }
  }

  async function handleSubmitAnswer(qId: string, answer: string) {
    updateQState(qId, {
      isSubmitting: true,
      optimisticStatus: "checking",
    });

    try {
      const result: AnswerResult = await submitAnswer(lessonId, qId, answer);

      updateQState(qId, {
        submitted: true,
        correct: result.correct,
        nextPrompt: result.next_prompt,
        xp: result.progress.xp,
        starEarned: result.progress.star_earned,
        isSubmitting: false,
        optimisticStatus: result.correct ? "correct" : "incorrect",
      });

      setTotalXp((prev) => prev + result.progress.xp);
      setTotalStars(result.progress.total_stars);
      setLessonStatus(result.progress.status);

      if (result.progress.status === "completed") {
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 3000);
        // refresh dashboard counts when a lesson completes
        (async () => {
          try {
            const d: DashboardData = await fetchDashboard();
            setCurrentStreak(d.current_streak ?? 0);
            setLessonsCompleted(d.lessons_completed ?? 0);
          } catch {
            // ignore
          }
        })();
      }
    } catch (err) {
      updateQState(qId, {
        isSubmitting: false,
        optimisticStatus: "idle",
      });
      setError(err instanceof Error ? err.message : "Failed to submit answer");
    }
  }

  async function handleRequestHint(qId: string) {
    const currentState = questionStates[qId];
    if (!currentState || currentState.hintLevel >= 3) return;

    const nextHintLevel = currentState.hintLevel + 1;

    updateQState(qId, {
      isLoadingHint: true,
      starEarned: false,
    });

    try {
      const result: HintResult = await requestHint(lessonId, qId, nextHintLevel);

      updateQState(qId, {
        hints: [...currentState.hints, result.hint],
        hintLevel: nextHintLevel,
        starEarned: false,
        isLoadingHint: false,
      });
    } catch (err) {
      updateQState(qId, {
        isLoadingHint: false,
      });
      setError(err instanceof Error ? err.message : "Failed to get hint");
    }
  }

  function goToQuestion(index: number) {
    setCurrentQuestionIndex(index);
    setShowTheory(false);
  }

  function goNext() {
    const totalQuestions = lesson?.questions.length ?? 0;
    if (currentQuestionIndex < totalQuestions - 1) {
      goToQuestion(currentQuestionIndex + 1);
    }
  }

  function toggleTutor() {
    setIsTutorOpen((s) => !s);
  }

  return {
    lesson,
    isLoading,
    error,
    currentQuestionIndex,
    questionStates,
    totalXp,
    totalStars,
  currentStreak,
  lessonsCompleted,
    lessonStatus,
    showTheory,
    setShowTheory,
    showConfetti,
    showResumeDialog,
    isResetting,
    handleContinueLesson,
    handleStartOver,
    handleSubmitAnswer,
    handleRequestHint,
    goToQuestion,
    goNext,
    updateQState,
  isTutorOpen,
  toggleTutor,
  };
}
