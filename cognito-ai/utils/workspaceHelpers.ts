import { Lesson, LessonProgress } from "@/lib/lessons";
import { QuestionState } from "@/types/workspace";

export function initFreshStates(data: Lesson): Record<string, QuestionState> {
  const states: Record<string, QuestionState> = {};
  data.questions.forEach((q) => {
    states[q.id] = {
      answer: "",
      submitted: false,
      correct: null,
      nextPrompt: "",
      hints: [],
      hintLevel: 0,
      starEarned: false,
      xp: 0,
      isSubmitting: false,
      isLoadingHint: false,
      optimisticStatus: "idle",
    };
  });
  return states;
}

export function restoreProgressState(data: Lesson, progress: LessonProgress) {
  const states: Record<string, QuestionState> = {};
  let firstUnansweredIdx = -1;

  data.questions.forEach((q, idx) => {
    const qp = progress.questions[q.id];
    if (qp && qp.answered) {
      const earned = qp.correct === true && qp.hints_used === 0;
      states[q.id] = {
        answer: qp.answer || "",
        submitted: true,
        correct: qp.correct,
        nextPrompt: "",
        hints: [],
        hintLevel: qp.hints_used,
        starEarned: earned,
        xp: 0,
        isSubmitting: false,
        isLoadingHint: false,
        optimisticStatus: qp.correct ? "correct" : "incorrect",
      };
    } else {
      if (firstUnansweredIdx === -1) firstUnansweredIdx = idx;
      states[q.id] = {
        answer: "",
        submitted: false,
        correct: null,
        nextPrompt: "",
        hints: [],
        hintLevel: qp?.hints_used ?? 0,
        starEarned: false,
        xp: 0,
        isSubmitting: false,
        isLoadingHint: false,
        optimisticStatus: "idle",
      };
    }
  });

  return { states, firstUnansweredIdx };
}
