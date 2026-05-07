export interface JourneyModule {
  order: number;
  index: number;
  title: string;
  description: string;
  lesson_status?: "not_started" | "in_progress" | "completed";
  xp_earned?: number;
  stars_remaining?: number;
}

export interface Journey {
  id: string;
  topic: string;
  type: "topic" | "problem";
  modules: JourneyModule[];
  createdAt?: string;
  progress?: number;
}
