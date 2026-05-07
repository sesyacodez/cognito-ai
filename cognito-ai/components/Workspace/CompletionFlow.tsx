"use client";

import React from "react";

type Props = {
  xpEarned: number;
  starsEarned: number;
  onClose?: () => void;
};

export default function CompletionFlow({ xpEarned, starsEarned, onClose }: Props) {
  // Mock accuracy and weakest topic data — replace with real data from hook if available
  const accuracy = 84; // percent
  const weakest = "Chain rule application";
  const combo = 3; // combo multiplier

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-white mb-3">Урок завершено</h2>

      <div className="grid grid-cols-1 gap-4">
        <div className="rounded-lg bg-[#071026] p-4 flex items-center justify-between">
          <div>
            <div className="text-sm text-white/70">Нагороди</div>
            <div className="mt-1 text-xl font-semibold text-white">{xpEarned} XP • {starsEarned} ★</div>
          </div>
          <div className="text-right">
            <div className="text-sm text-white/70">Combo</div>
            <div className="mt-1 text-lg font-bold text-emerald-400">x{combo}</div>
          </div>
        </div>

        <div className="rounded-lg bg-[#071026] p-4">
          <div className="text-sm text-white/70">Точність</div>
          <div className="mt-2 flex items-center gap-4">
            <div className="h-3 w-full bg-white/6 rounded-full overflow-hidden">
              <div className="h-3 bg-gradient-to-r from-emerald-400 to-emerald-600" style={{ width: `${accuracy}%` }} />
            </div>
            <div className="text-sm font-medium text-white">{accuracy}%</div>
          </div>
        </div>

        <div className="rounded-lg bg-[#071026] p-4">
          <div className="text-sm text-white/70">Слабкі місця / Рекомендації</div>
          <div className="mt-2 text-sm text-white/60">Рекомендуємо повторити: <strong className="text-white">{weakest}</strong>. Зосередьтесь на практичних прикладах і застосуванні крок за кроком.</div>
        </div>

        <div className="flex items-center gap-3">
          <button onClick={() => { console.log('Share progress'); alert('Shared (mock)'); }} className="flex-1 rounded-md bg-white px-4 py-2 font-semibold text-[#060816]">Share Progress</button>
          <button onClick={onClose} className="rounded-md border border-white/8 px-4 py-2 text-white">Back</button>
        </div>
      </div>
    </div>
  );
}
