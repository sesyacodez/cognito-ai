import { Journey, JourneyModule } from "@/types/journey";

export function normalizeJourney(raw: Record<string, unknown>, topic: string, type: "topic" | "problem"): Journey {
  const rawModules = (raw.modules as Array<Record<string, unknown>> | undefined) ?? [];
  return {
    id: (raw.roadmap_id as string) ?? (raw.id as string) ?? `journey-${Date.now()}`,
    topic: (raw.topic as string) ?? topic,
    type,
    modules: rawModules.map((m, i) => ({
      order: (m.order as number) ?? (m.index as number) ?? i,
      index: (m.index as number) ?? i,
      title: (m.title as string) ?? "",
      description: (m.outcome as string) ?? (m.description as string) ?? "",
      lesson_status: (m.lesson_status as JourneyModule["lesson_status"]) ?? "not_started",
      xp_earned: (m.xp_earned as number) ?? 0,
      stars_remaining: (m.stars_remaining as number) ?? 3,
    })),
    createdAt: (raw.created_at as string) ?? (raw.createdAt as string) ?? new Date().toISOString(),
    progress: (raw.progress as number) ?? 0,
  };
}
