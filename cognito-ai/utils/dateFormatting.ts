import { Journey } from "@/types/journey";

export function timeAgo(dateStr?: string): string {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hour${hrs > 1 ? "s" : ""} ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "Yesterday";
  return `${days} days ago`;
}

export function groupJourneysByDate(journeys: Journey[]) {
  const today: Journey[] = [];
  const yesterday: Journey[] = [];
  const previous: Journey[] = [];
  const now = new Date();

  journeys.forEach((j) => {
    if (!j.createdAt) {
      previous.push(j);
      return;
    }
    const d = new Date(j.createdAt);
    const diffDays = Math.floor((now.getTime() - d.getTime()) / 86400000);
    if (diffDays < 1) today.push(j);
    else if (diffDays < 2) yesterday.push(j);
    else previous.push(j);
  });
  
  return { today, yesterday, previous };
}
