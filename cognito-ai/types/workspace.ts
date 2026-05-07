export interface QuestionState {
  answer: string;
  submitted: boolean;
  correct: boolean | null;
  nextPrompt: string;
  hints: string[];
  hintLevel: number;
  starEarned: boolean;
  xp: number;
  isSubmitting: boolean;
  isLoadingHint: boolean;
  optimisticStatus: "idle" | "checking" | "correct" | "incorrect";
}
