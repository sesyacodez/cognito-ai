"use client";

import React, { useState, useEffect, useRef } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/AuthContext";
import { getSession } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { resetLesson, deleteLesson } from "@/lib/lessons";

/* ── types ─────────────────────────────────────────── */

interface JourneyModule {
  order: number;
  index: number;
  title: string;
  description: string;
  lesson_status?: "not_started" | "in_progress" | "completed";
  xp_earned?: number;
  stars_remaining?: number;
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
  const [expandedJourney, setExpandedJourney] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
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
      const normalized = (data || []).map((raw: Record<string, unknown>) =>
        normalizeJourney(raw, (raw.topic as string) || "", (raw.type as "topic" | "problem") || "topic")
      );
      setJourneys(normalized);
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

            {/* ── journeys with module progress ── */}
            {journeys.length > 0 && (
              <div className="w-full max-w-3xl">
                <h2 className="text-sm font-semibold text-white mb-4">
                  Your Learning Paths
                </h2>

                <div className="space-y-4">
                  {journeys.map((journey) => {
                    const isExpanded = expandedJourney === journey.id;
                    const completedModules = journey.modules.filter(m => m.lesson_status === "completed").length;
                    const progress = journey.modules.length > 0 ? Math.round((completedModules / journey.modules.length) * 100) : 0;
                    const mode = journey.type === "topic" ? "learn" : "solve";

                    return (
                      <div key={journey.id} className="bg-[#0f1224] rounded-xl border border-gray-700/40 overflow-hidden transition-all hover:border-blue-500/30">
                        {/* journey header — click to expand */}
                        <button
                          onClick={() => setExpandedJourney(isExpanded ? null : journey.id)}
                          className="w-full flex items-center justify-between p-5 text-left group"
                        >
                          <div className="flex items-center gap-4 min-w-0">
                            <div className="w-10 h-10 rounded-xl bg-blue-600/15 flex items-center justify-center flex-shrink-0">
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                                <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" stroke="#60a5fa" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                              </svg>
                            </div>
                            <div className="min-w-0">
                              <h3 className="text-sm font-semibold text-white group-hover:text-blue-200 transition truncate">{journey.topic}</h3>
                              <p className="text-xs text-gray-500">{completedModules}/{journey.modules.length} modules • {timeAgo(journey.createdAt)}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 flex-shrink-0">
                            <div className="flex items-center gap-2">
                              <div className="w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-500 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
                              </div>
                              <span className="text-xs text-gray-400 w-8 text-right">{progress}%</span>
                            </div>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className={`text-gray-500 transition-transform ${isExpanded ? "rotate-180" : ""}`}>
                              <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          </div>
                        </button>

                        {/* expanded module list */}
                        {isExpanded && (
                          <div className="px-5 pb-5 space-y-2 border-t border-gray-700/30 pt-4">
                            {journey.modules.map((mod) => {
                              const lessonId = `${journey.id}-${mod.index}`;
                              const isActionLoading = actionLoading === lessonId;
                              const statusColors: Record<string, string> = {
                                completed: "bg-emerald-500/10 border-emerald-500/30",
                                in_progress: "bg-blue-500/10 border-blue-500/30",
                                not_started: "bg-[#0d1220] border-gray-700/30",
                              };
                              const status = mod.lesson_status || "not_started";

                              return (
                                <div key={mod.index} className={`flex items-center gap-3 p-3 rounded-xl border ${statusColors[status]} transition`}>
                                  {/* status icon */}
                                  <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0">
                                    {status === "completed" ? (
                                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                                        <path d="M20 6L9 17l-5-5" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                      </svg>
                                    ) : status === "in_progress" ? (
                                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                                        <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#3b82f6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                                      </svg>
                                    ) : (
                                      <div className="w-5 h-5 rounded-full border-2 border-gray-600" />
                                    )}
                                  </div>

                                  {/* module info */}
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-white truncate">{mod.title}</p>
                                    <p className="text-xs text-gray-500 truncate">{mod.description}</p>
                                  </div>

                                  {/* XP/stars for non-idle modules */}
                                  {status !== "not_started" && (
                                    <div className="flex items-center gap-2 flex-shrink-0 mr-1">
                                      <span className="text-xs font-bold text-cyan-400">{mod.xp_earned} XP</span>
                                      <div className="flex gap-0.5">
                                        {[1, 2, 3].map(s => (
                                          <svg key={s} width="10" height="10" viewBox="0 0 24 24" fill={s <= (mod.stars_remaining ?? 0) ? "#facc15" : "none"}>
                                            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke={s <= (mod.stars_remaining ?? 0) ? "#facc15" : "#4b5563"} strokeWidth="1.5"/>
                                          </svg>
                                        ))}
                                      </div>
                                    </div>
                                  )}

                                  {/* action buttons */}
                                  <div className="flex items-center gap-1 flex-shrink-0">
                                    {status === "not_started" && (
                                      <button
                                        onClick={() => {
                                          const qs = new URLSearchParams({ topic: mod.title, mode });
                                          router.push(`/workspace/${lessonId}?${qs.toString()}`);
                                        }}
                                        className="px-3 py-1.5 text-xs font-medium bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 rounded-lg border border-blue-500/20 transition"
                                      >
                                        Start
                                      </button>
                                    )}
                                    {status === "in_progress" && (
                                      <button
                                        onClick={() => {
                                          const qs = new URLSearchParams({ topic: mod.title, mode });
                                          router.push(`/workspace/${lessonId}?${qs.toString()}`);
                                        }}
                                        className="px-3 py-1.5 text-xs font-medium bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 rounded-lg border border-cyan-500/20 transition"
                                      >
                                        Continue
                                      </button>
                                    )}
                                    {status === "completed" && (
                                      <button
                                        onClick={() => {
                                          const qs = new URLSearchParams({ topic: mod.title, mode });
                                          router.push(`/workspace/${lessonId}?${qs.toString()}`);
                                        }}
                                        className="px-3 py-1.5 text-xs font-medium bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 rounded-lg border border-emerald-500/20 transition"
                                      >
                                        Review
                                      </button>
                                    )}
                                    {status !== "not_started" && (
                                      <>
                                        <button
                                          onClick={async (e) => {
                                            e.stopPropagation();
                                            setActionLoading(lessonId);
                                            try {
                                              await resetLesson(lessonId);
                                              await fetchJourneys();
                                            } catch { /* ignore */ } finally {
                                              setActionLoading(null);
                                            }
                                          }}
                                          disabled={isActionLoading}
                                          title="Reset progress"
                                          className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-500 hover:text-amber-400 hover:bg-amber-500/10 transition disabled:opacity-50"
                                        >
                                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                                            <path d="M1 4v6h6M23 20v-6h-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                            <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                          </svg>
                                        </button>
                                        <button
                                          onClick={async (e) => {
                                            e.stopPropagation();
                                            setActionLoading(lessonId);
                                            try {
                                              await deleteLesson(lessonId);
                                              await fetchJourneys();
                                            } catch { /* ignore */ } finally {
                                              setActionLoading(null);
                                            }
                                          }}
                                          disabled={isActionLoading}
                                          title="Delete progress"
                                          className="w-7 h-7 flex items-center justify-center rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition disabled:opacity-50"
                                        >
                                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                                            <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                          </svg>
                                        </button>
                                      </>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  })}
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
