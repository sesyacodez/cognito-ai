"use client";

import React from "react";
import { Journey } from "@/types/journey";
import Link from "next/link";

export function SidebarGroup({
  label,
  items,
  searchQuery,
}: {
  label: string;
  items: Journey[];
  searchQuery: string;
}) {
  const filtered = items.filter((j) =>
    (j.topic ?? "").toLowerCase().includes(searchQuery.toLowerCase())
  );
  if (filtered.length === 0) return null;

  return (
    <div className="mb-3">
      <p className="px-2 py-1 text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
        {label}
      </p>
      {filtered.map((journey) => (
        <Link
          key={journey.id}
          href={{
            pathname: `/workspace/${journey.id}`,
            query: { topic: journey.topic, mode: journey.type === "topic" ? "learn" : "solve" }
          }}
          className="w-full text-left px-3 py-2 rounded-lg text-xs text-gray-300 hover:bg-[#0f1224] hover:text-white transition flex items-center gap-2 group focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="flex-shrink-0 text-gray-500 group-hover:text-blue-400 transition">
            <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
            <path d="M7 8h10M7 12h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <span className="truncate">{journey.topic}</span>
        </Link>
      ))}
    </div>
  );
}
