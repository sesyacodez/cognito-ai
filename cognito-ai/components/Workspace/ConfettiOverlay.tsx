"use client";

import React, { useEffect, useState } from "react";

type Piece = {
  id: number;
  left: number; // percent
  delay: number; // s
  duration: number; // s
  size: number; // px
  color: string;
  rotation: number; // deg
};

export default function ConfettiOverlay({ active = true }: { active?: boolean }) {
  const [pieces, setPieces] = useState<Piece[]>([]);

  useEffect(() => {
    if (!active) {
      // defer clearing to avoid synchronous setState within effect
      const id = window.setTimeout(() => setPieces([]), 0);
      return () => window.clearTimeout(id);
    }

    // generate once per activation to avoid impure renders
    const colors = ["#22d3ee", "#a78bfa", "#f97316", "#facc15", "#34d399"];
    const generated: Piece[] = Array.from({ length: 40 }).map((_, i) => ({
      id: i,
      left: Math.random() * 100,
      delay: Math.random() * 1.5,
      duration: 2 + Math.random() * 2,
      size: 6 + Math.random() * 10,
      color: colors[i % colors.length],
      rotation: Math.random() * 360,
    }));

    // defer setting state to avoid synchronous setState inside effect
    const setId = window.setTimeout(() => setPieces(generated), 0);

    // clear after the longest animation finishes + small buffer
    const max = Math.max(...generated.map((p) => p.delay + p.duration)) * 1000 + 500;
    const t = window.setTimeout(() => setPieces([]), max);
    return () => {
      window.clearTimeout(setId);
      window.clearTimeout(t);
    };
  }, [active]);

  if (!active || pieces.length === 0) return null;

  return (
    <div aria-hidden className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      <style>{`
        @keyframes confetti-fall {
          0% { transform: translateY(-10vh) rotate(0deg); opacity: 1; }
          100% { transform: translateY(110vh) rotate(360deg); opacity: 0.85; }
        }
      `}</style>

      {pieces.map((p) => (
        <div
          key={p.id}
          style={{
            position: "absolute",
            top: "-10vh",
            left: `${p.left}%`,
            width: p.size,
            height: p.size * 0.6,
            backgroundColor: p.color,
            transform: `rotate(${p.rotation}deg)`,
            borderRadius: 2,
            opacity: 0.95,
            animation: `confetti-fall ${p.duration}s ease-in ${p.delay}s forwards`,
            willChange: "transform, opacity",
          }}
        />
      ))}
    </div>
  );
}
