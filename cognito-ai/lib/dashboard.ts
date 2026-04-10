import { getAuthHeader } from "./auth";

export interface DashboardActivity {
  lesson_id: string;
  lesson_title: string;
  status: string;
  xp_earned: number;
  stars_earned: number;
  updated_at: string;
}

export interface DashboardRoadmap {
  id: string;
  topic: string;
  mode: string;
  module_count: number;
  completed_modules: number;
  created_at: string;
}

export interface DashboardData {
  total_xp: number;
  total_stars: number;
  lessons_completed: number;
  lessons_in_progress: number;
  current_streak: number;
  longest_streak: number;
  recent_activity: DashboardActivity[];
  roadmaps: DashboardRoadmap[];
  user_name: string;
}

export async function fetchDashboard(): Promise<DashboardData> {
  const res = await fetch("/api/dashboard", {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
  });
  
  if (!res.ok) {
    throw new Error(`Failed to fetch dashboard: ${res.status}`);
  }
  
  return res.json();
}
