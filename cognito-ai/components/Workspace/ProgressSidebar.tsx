import React from "react";

type Props = {
  totalXp: number;
  totalStars: number;
  currentStreak: number;
  lessonsCompleted: number;
  goToQuestion?: (i: number) => void;
};

export default function ProgressSidebar({ totalXp, totalStars, currentStreak, lessonsCompleted }: Props) {
  return (
    <aside className="w-64 p-4 bg-[#071025] border-l border-gray-800/30 rounded-l-2xl">
      <div className="space-y-4">
        <div>
          <div className="text-xs text-gray-400">XP</div>
          <div className="text-lg font-bold text-white">{totalXp}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Stars</div>
          <div className="text-lg font-bold text-white">{totalStars}</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Streak</div>
          <div className="text-lg font-bold text-white">{currentStreak}d</div>
        </div>
        <div>
          <div className="text-xs text-gray-400">Lessons Completed</div>
          <div className="text-lg font-bold text-white">{lessonsCompleted}</div>
        </div>
      </div>
    </aside>
  );
}
