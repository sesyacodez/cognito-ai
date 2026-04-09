"use client";

import React, { useState, useEffect, useRef } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/AuthContext";
import { getSession } from "@/lib/auth";
import { useRouter } from "next/navigation";

/* ── types ─────────────────────────────────────────── */

interface JourneyModule {
  order: number;
  title: string;
  description: string;
}

interface Journey {
  id: string;
  topic: string;
  type: "topic" | "problem";
  modules: JourneyModule[];
  createdAt?: string;
  progress?: number;
}

/* Normalize the POST /api/roadmaps response into a Journey */
function normalizeJourney(raw: Record<string, unknown>, topic: string, type: "topic" | "problem"): Journey {
  const rawModules = (raw.modules as Array<Record<string, unknown>> | undefined) ?? [];
  return {
    id: (raw.roadmap_id as string) ?? (raw.id as string) ?? `journey-${Date.now()}`,
    topic: (raw.topic as string) ?? topic,
    type,
    modules: rawModules.map((m, i) => ({
      order: (m.index as number) ?? i,
      title: (m.title as string) ?? "",
      description: (m.outcome as string) ?? (m.description as string) ?? "",
    })),
    createdAt: new Date().toISOString(),
    progress: 0,
  };
}

/* ── helpers ────────────────────────────────────────── */

function timeAgo(dateStr?: string) {
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

/* ── component ──────────────────────────────────────── */

export default function InsightHub() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [journeys, setJourneys] = useState<Journey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [activeTab, setActiveTab] = useState<"topic" | "problem">("topic");
  const [searchQuery, setSearchQuery] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [error, setError] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  useEffect(() => {
    fetchJourneys();
  }, []);

  async function fetchJourneys() {
    setIsLoading(true);
    setError("");
    try {
      const session = getSession();
      const headers: HeadersInit = { "Content-Type": "application/json" };
      if (session) headers["Authorization"] = `Bearer ${session.token}`;

      const res = await fetch("/api/roadmaps", { headers });
      if (!res.ok) throw new Error("Failed to fetch journeys");
      const data = await res.json();
      setJourneys(data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load journeys");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateJourney(e: React.FormEvent) {
    e.preventDefault();
    if (!inputValue.trim()) return;

    setIsCreating(true);
    setError("");
    try {
      const session = getSession();
      const headers: HeadersInit = { "Content-Type": "application/json" };
      if (session) headers["Authorization"] = `Bearer ${session.token}`;

      const mode = activeTab === "topic" ? "learn" : "solve";
      const res = await fetch("/api/roadmaps", {
        method: "POST",
        headers,
        body: JSON.stringify({ topic: inputValue, mode }),
      });
      if (!res.ok) throw new Error("Failed to create journey");

      const raw = await res.json();
      const newJourney = normalizeJourney(raw, inputValue, activeTab);
      setJourneys((prev) => [newJourney, ...prev]);
      setInputValue("");
      
      const qs = new URLSearchParams({ topic: newJourney.topic, mode: newJourney.type === "topic" ? "learn" : "solve" });
      router.push(`/workspace/${newJourney.id}?${qs.toString()}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create journey");
    } finally {
      setIsCreating(false);
    }
  }

  /* group journeys by date for sidebar */
  function groupJourneys() {
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

  const groups = groupJourneys();
  const filteredJourneys = journeys.filter((j) =>
    (j.topic ?? "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  /* recent = last 3 for bottom cards */
  const recentJourneys = journeys.slice(0, 3);

  /* placeholder text based on active tab */
  const placeholderText =
    activeTab === "topic"
      ? "What would you like to explore..."
      : "Describe the problem you need to solve...";

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-[#0b0f1e] font-sans">
        {/* ═══════════ SIDEBAR ═══════════ */}
        <aside
          className={`${sidebarOpen ? "w-64" : "w-0 overflow-hidden"
            } flex-shrink-0 border-r border-gray-700/50 bg-[#080c19] transition-all duration-300 flex flex-col`}
        >
          {/* sidebar top nav */}
          <div className="px-2 pt-5 pb-2">
            <button
              onClick={() => router.push("/insight-hub")}
              className="w-full text-left px-3 py-2 rounded-lg text-xs bg-[#0f1224] text-white flex items-center gap-2 group mb-2 border border-blue-500/30 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Navigate to Insight Hub"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="flex-shrink-0 text-blue-400" aria-hidden="true">
                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                <path d="M16 16l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span>Insight Hub</span>
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              className="w-full text-left px-3 py-2 rounded-lg text-xs text-gray-300 hover:bg-[#0f1224] hover:text-white transition flex items-center gap-2 group mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Navigate to Dashboard"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="flex-shrink-0 text-gray-500 group-hover:text-blue-400 transition" aria-hidden="true">
                <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span>Dashboard</span>
            </button>
          </div>

          {/* sidebar header */}
          <div className="flex items-center justify-between px-4 pt-2 pb-3">
            <span className="text-sm font-bold text-white tracking-wide">
              Journeys
            </span>
            <button
              onClick={() => {
                setJourneys((prev) => [
                  {
                    id: `new-${Date.now()}`,
                    topic: "New Journey",
                    type: "topic",
                    modules: [],
                    createdAt: new Date().toISOString(),
                    progress: 0,
                  },
                  ...prev,
                ]);
              }}
              className="w-6 h-6 flex items-center justify-center rounded text-gray-400 hover:text-white hover:bg-gray-700/50 transition focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="New journey"
              title="New journey"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M7 1v12M1 7h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          </div>

          {/* search */}
          <div className="px-3 pb-3">
            <div className="flex items-center gap-2 rounded-lg bg-[#0f1224] border border-gray-700/50 px-3 py-1.5 focus-within:border-blue-500/50 focus-within:ring-1 focus-within:ring-blue-500/50 transition-all">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="text-gray-500 flex-shrink-0">
                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                <path d="M16 16l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <input
                type="text"
                placeholder="Search journeys..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-xs text-gray-300 placeholder-gray-500 outline-none w-full"
              />
            </div>
          </div>

          {/* journey list */}
          <div className="flex-1 overflow-y-auto px-2 pb-4 scrollbar-thin">
            {isLoading ? (
              <div className="text-center py-6 text-gray-500 text-xs">Loading...</div>
            ) : filteredJourneys.length === 0 ? (
              <div className="text-center py-6 text-gray-500 text-xs">No journeys yet</div>
            ) : (
              <>
                {groups.today.length > 0 && (
                  <SidebarGroup label="Today" items={groups.today} searchQuery={searchQuery} />
                )}
                {groups.yesterday.length > 0 && (
                  <SidebarGroup label="Yesterday" items={groups.yesterday} searchQuery={searchQuery} />
                )}
                {groups.previous.length > 0 && (
                  <SidebarGroup label="Previous" items={groups.previous} searchQuery={searchQuery} />
                )}
              </>
            )}
          </div>
        </aside>

        {/* ═══════════ MAIN ═══════════ */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* top bar */}
          <header className="flex items-center justify-between px-6 py-3 border-b border-gray-700/30">
            <button
              onClick={() => setSidebarOpen((o) => !o)}
              aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
              className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-700/30 transition focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>

            {/* user avatar */}
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                aria-haspopup="true"
                aria-expanded={showDropdown}
                aria-label="User menu"
                className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold hover:ring-2 ring-blue-500 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0b0f1e] focus:ring-blue-500"
              >
                {user?.name?.charAt(0)?.toUpperCase() || "U"}
              </button>
              
              {showDropdown && (
                <div className="absolute right-0 mt-2 w-48 bg-[#0f1224] rounded-lg shadow-xl border border-gray-700/50 py-1 z-50">
                  <div className="px-4 py-2 border-b border-gray-700/50">
                    <p className="text-sm font-medium text-white truncate">{user?.name}</p>
                    <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-800 transition"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </header>

          {/* center content */}
          <main className="flex-1 flex flex-col items-center justify-center px-6 pb-8">
            {/* logo */}
            <div className="mb-6 flex flex-col items-center">
              <img
                src="/CognitoAI logo.svg"
                alt="CognitoAI Logo"
                className="w-30 h-30 mb-"
              />
              <h1 className="text-2xl font-bold text-white tracking-wider mb-1">
                COGNITO.AI
              </h1>
              <p className="text-sm text-gray-400 mb-4">
                What would you like to explore?
              </p>
            </div>

            {/* tab toggle */}
            <div className="flex items-center bg-[#0f1224] rounded-full p-1 mb-6 border border-gray-700/40">
              <button
                onClick={() => setActiveTab("topic")}
                className={`px-5 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${activeTab === "topic"
                  ? "bg-[#1a2040] text-white shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#0f1224]"
                  : "text-gray-400 hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#0f1224]"
                  }`}
              >
                Topic
              </button>
              <button
                onClick={() => setActiveTab("problem")}
                className={`px-5 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${activeTab === "problem"
                  ? "bg-[#1a2040] text-white shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#0f1224]"
                  : "text-gray-400 hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#0f1224]"
                  }`}
              >
                Problem
              </button>
            </div>

            {/* input area */}
            <form
              onSubmit={handleCreateJourney}
              className="w-full max-w-xl mb-8"
            >
              <div className="relative bg-[#0f1224] rounded-xl border border-gray-700/50 p-4 focus-within:border-blue-500/50 transition-colors">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={placeholderText}
                  disabled={isCreating}
                  rows={2}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleCreateJourney(e);
                    }
                  }}
                  className="w-full bg-transparent text-sm text-white placeholder-gray-500 outline-none resize-none disabled:opacity-60"
                />
                <div className="flex items-center justify-between mt-2">
                  <div className="flex items-center gap-2">
                    {/* attach icon */}
                    <button
                      type="button"
                      className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-700/30 transition"
                      title="Attach file"
                    >
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                        <path
                          d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </button>
                    {/* image icon */}
                    <button
                      type="button"
                      className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-700/30 transition"
                      title="Add image"
                    >
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                        <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2" />
                        <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
                        <path d="M21 15l-5-5L5 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </button>
                    {/* sparkle icon */}
                    <div className="w-7 h-7 flex items-center justify-center text-gray-500">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                        <path
                          d="M12 2l2.4 7.2L22 12l-7.6 2.8L12 22l-2.4-7.2L2 12l7.6-2.8L12 2z"
                          stroke="currentColor"
                          strokeWidth="1.5"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </div>
                  </div>

                  {/* submit button */}
                  <button
                    type="submit"
                    disabled={isCreating || !inputValue.trim()}
                    className="w-8 h-8 flex items-center justify-center rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white transition focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-[#0f1224]"
                    aria-label="Submit search"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </button>
                </div>
              </div>

              {error && (
                <div className="mt-3 p-3 bg-red-950/50 border border-red-700/50 rounded-lg text-red-200 text-xs">
                  {error}
                </div>
              )}

              <p className="text-center text-xs text-gray-500 mt-3">
                Upload a problem or describe a task to get step-by-step guidance
              </p>
            </form>

            {/* ── recent journeys ── */}
            {recentJourneys.length > 0 && (
              <div className="w-full max-w-3xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold text-white">
                    Recent Journeys
                  </h2>
                  <button className="text-xs text-blue-400 hover:text-blue-300 transition">
                    View all →
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recentJourneys.map((journey) => (
                    <div
                      key={journey.id}
                      onClick={() => {
                        const qs = new URLSearchParams({ topic: journey.topic, mode: journey.type === "topic" ? "learn" : "solve" });
                        router.push(`/workspace/${journey.id}?${qs.toString()}`);
                      }}
                      className="group bg-[#0f1224] rounded-xl border border-gray-700/40 p-5 hover:border-blue-500/40 transition-all duration-200 cursor-pointer hover:shadow-lg hover:shadow-blue-900/10"
                    >
                      {/* card header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-600/15 flex items-center justify-center">
                          {journey.type === "problem" ? (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                              <rect x="3" y="3" width="18" height="18" rx="2" stroke="#60a5fa" strokeWidth="1.5" />
                              <path d="M8 12h8M12 8v8" stroke="#60a5fa" strokeWidth="1.5" strokeLinecap="round" />
                            </svg>
                          ) : (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                              <rect x="3" y="4" width="18" height="16" rx="2" stroke="#60a5fa" strokeWidth="1.5" />
                              <path d="M7 8h10M7 12h6" stroke="#60a5fa" strokeWidth="1.5" strokeLinecap="round" />
                            </svg>
                          )}
                        </div>
                        <span
                          className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${journey.type === "problem"
                            ? "bg-purple-500/15 text-purple-300"
                            : "bg-blue-500/15 text-blue-300"
                            }`}
                        >
                          {journey.type === "problem" ? "Problem" : "Topic"}
                        </span>
                      </div>

                      {/* card body */}
                      <h3 className="text-sm font-semibold text-white mb-1 line-clamp-2 group-hover:text-blue-100 transition">
                        {journey.topic}
                      </h3>
                      <p className="text-xs text-gray-400 mb-4 line-clamp-2">
                        {journey.modules
                          ?.slice(0, 2)
                          .map((m) => m.title)
                          .join(", ") || "No modules yet"}
                      </p>

                      {/* card footer */}
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-gray-500">
                          {timeAgo(journey.createdAt)}
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-blue-500 rounded-full transition-all"
                              style={{
                                width: `${journey.progress ?? Math.floor(Math.random() * 100)}%`,
                              }}
                            />
                          </div>
                          <span className="text-[10px] text-gray-400">
                            {journey.progress ?? Math.floor(Math.random() * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}

/* ── Sidebar Group ──────────────────────────────────── */

function SidebarGroup({
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
        <button
          key={journey.id}
          onClick={() => {
            const qs = new URLSearchParams({ topic: journey.topic, mode: journey.type === "topic" ? "learn" : "solve" });
            window.location.href = `/workspace/${journey.id}?${qs.toString()}`;
          }}
          className="w-full text-left px-3 py-2 rounded-lg text-xs text-gray-300 hover:bg-[#0f1224] hover:text-white transition flex items-center gap-2 group focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="flex-shrink-0 text-gray-500 group-hover:text-blue-400 transition">
            <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" />
            <path d="M7 8h10M7 12h6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <span className="truncate">{journey.topic}</span>
        </button>
      ))}
    </div>
  );
}
