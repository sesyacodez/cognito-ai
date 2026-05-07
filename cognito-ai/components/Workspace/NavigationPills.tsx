"use client";

import React from "react";

type Props = {
  total: number;
  currentIndex: number;
  onJump: (i: number) => void;
};

export default function NavigationPills({ total, currentIndex, onJump }: Props) {
  if (total <= 1) return null;
  return (
    <div className="flex items-center gap-2">
      {Array.from({ length: total }).map((_, i) => (
        <button
          key={i}
          aria-label={`Go to question ${i + 1}`}
          onClick={() => onJump(i)}
          className={`w-3 h-3 rounded-full ${i === currentIndex ? "bg-blue-500" : "bg-gray-500/40"}`}
        />
      ))}
    </div>
  );
}
