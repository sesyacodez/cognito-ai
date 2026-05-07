"use client";

import React, { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/AuthContext";
import { useRouter } from "next/navigation";
import { fetchDashboard, DashboardData, DashboardActivity, DashboardRoadmap } from "@/lib/dashboard";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const dashboardData = await fetchDashboard();
        setData(dashboardData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard data");
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  /** Helper for relative time */
  function timeAgo(dateStr: string) {
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

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-[#0b0f1e] font-sans">
        {/* SIDEBAR */}
        <aside
          className={`${
            sidebarOpen ? "w-64" : "w-0 overflow-hidden"
          } flex-shrink-0 border-r border-gray-700/50 bg-[#080c19] transition-all duration-300 flex flex-col`}
        >
          {/* sidebar header */}
          <div className="flex items-center justify-between px-4 pt-5 pb-3">
            <span className="text-sm font-bold text-white tracking-wide">Features</span>
          </div>

          {/* navigation list */}
          <div className="flex-1 overflow-y-auto px-2 pb-4 scrollbar-thin">
            <button
              onClick={() => router.push("/insight-hub")}
              className="w-full text-left px-3 py-2 rounded-lg text-xs text-gray-300 hover:bg-[#0f1224] hover:text-white transition flex items-center gap-2 group mb-2"
              aria-label="Navigate to Insight Hub"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="flex-shrink-0 text-gray-500 group-hover:text-blue-400 transition" aria-hidden="true">
                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                <path d="M16 16l4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span>Insight Hub</span>
            </button>
            <button
              onClick={() => router.push("/dashboard")}
              className="w-full text-left px-3 py-2 rounded-lg text-xs bg-[#0f1224] text-white flex items-center gap-2 group mb-2 border border-blue-500/30"
              aria-label="Navigate to Dashboard"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="flex-shrink-0 text-blue-400" aria-hidden="true">
                <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span>Dashboard</span>
            </button>
          </div>
        </aside>

        {/* MAIN */}
        <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
          {/* top bar */}
          <header className="flex items-center justify-between px-6 py-3 border-b border-gray-700/30 shrink-0">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen((o: boolean) => !o)}
                className="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-white hover:bg-gray-700/30 transition focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
              
              {/* STREAK COUNTER IN HEADER */}
              {data && (
                <div className="flex items-center gap-2 px-3 py-1 bg-orange-500/10 border border-orange-500/20 rounded-full" aria-label={`Current streak: ${data.current_streak} days`}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 2C12 2 8 8 8 12C8 16 12 20 12 20s4-4 4-8c0-4-4-10-4-10z"
                      stroke="#f97316"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <span className="text-xs font-bold text-orange-400">{data.current_streak} Day Streak</span>
                </div>
              )}
            </div>

            {/* user avatar */}
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold hover:ring-2 ring-blue-500 transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#0b0f1e] focus:ring-blue-500"
                aria-expanded={showDropdown}
                aria-haspopup="true"
                aria-label="User menu"
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
                    className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-800 transition focus:outline-none focus:bg-gray-800"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </header>

          {/* dashboard content */}
          <main className="flex-1 overflow-y-auto px-6 py-8 scrollbar-thin">
            <div className="max-w-5xl mx-auto">
              <h1 className="text-2xl font-bold text-white mb-6">Learning Dashboard</h1>
              
              {isLoading ? (
                <div className="text-center py-10">
                  <div className="w-10 h-10 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-gray-400 text-sm">Loading your progress...</p>
                </div>
              ) : error ? (
                <div className="p-4 bg-red-900/20 border border-red-500/30 rounded-xl text-red-400 text-sm">
                  {error}
                </div>
              ) : data ? (
                <>
                  {/* METRICS GRID */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    
                    <div className="bg-[#111830] border border-gray-700/50 rounded-2xl p-5 hover:border-cyan-500/30 transition shadow-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-full bg-cyan-500/10 flex items-center justify-center">
                          <span className="text-cyan-400 text-lg font-bold">XP</span>
                        </div>
                        <h2 className="text-sm font-semibold text-gray-400">Total XP</h2>
                      </div>
                      <div className="text-3xl font-bold text-white">{data.total_xp.toLocaleString()}</div>
                    </div>

                    <div className="bg-[#111830] border border-gray-700/50 rounded-2xl p-5 hover:border-yellow-500/30 transition shadow-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-full bg-yellow-500/10 flex items-center justify-center">
                           <svg width="18" height="18" viewBox="0 0 24 24" fill="#facc15">
                             <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="#facc15" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                           </svg>
                        </div>
                        <h2 className="text-sm font-semibold text-gray-400">Total Stars</h2>
                      </div>
                      <div className="text-3xl font-bold text-white">{data.total_stars}</div>
                    </div>

                    <div className="bg-[#111830] border border-gray-700/50 rounded-2xl p-5 hover:border-emerald-500/30 transition shadow-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center">
                           <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                             <path d="M20 6L9 17l-5-5" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                           </svg>
                        </div>
                        <h2 className="text-sm font-semibold text-gray-400">Lessons Finished</h2>
                      </div>
                      <div className="text-3xl font-bold text-white">{data.lessons_completed}</div>
                    </div>

                    <div className="bg-[#111830] border border-gray-700/50 rounded-2xl p-5 hover:border-orange-500/30 transition shadow-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-full bg-orange-500/10 flex items-center justify-center">
                           <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                             <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                           </svg>
                        </div>
                        <h2 className="text-sm font-semibold text-gray-400">Longest Streak</h2>
                      </div>
                      <div className="text-3xl font-bold text-white">{data.longest_streak}</div>
                    </div>

                  </div>

                  {/* ROADMAPS SECTION */}
                  {data.roadmaps && data.roadmaps.length > 0 && (
                    <div className="mb-8">
                      <h2 className="text-lg font-bold text-white mb-4">Your Learning Paths</h2>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        {data.roadmaps.map((rm: DashboardRoadmap) => {
                          const progress = rm.module_count > 0 ? Math.round((rm.completed_modules / rm.module_count) * 100) : 0;
                          return (
                            <button
                              key={rm.id}
                              onClick={() => router.push("/insight-hub")}
                              className="text-left bg-[#111830] border border-gray-700/50 rounded-2xl p-5 hover:border-purple-500/40 transition shadow-lg group"
                            >
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <div className="w-8 h-8 rounded-full bg-purple-500/10 flex items-center justify-center">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                      <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                  </div>
                                  <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${rm.mode === 'solve' ? 'bg-amber-500/10 text-amber-400' : 'bg-blue-500/10 text-blue-400'}`}>
                                    {rm.mode}
                                  </span>
                                </div>
                                {progress === 100 && (
                                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                                    <path d="M20 6L9 17l-5-5" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                  </svg>
                                )}
                              </div>
                              <p className="text-sm font-semibold text-white mb-1 group-hover:text-purple-300 transition truncate">{rm.topic}</p>
                              <p className="text-xs text-gray-500 mb-3">{rm.completed_modules}/{rm.module_count} modules</p>
                              <div className="w-full h-1.5 bg-gray-700/50 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-purple-500 rounded-full transition-all duration-700"
                                  style={{ width: `${progress}%` }}
                                />
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* BOTTOM SECTION */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* RECENT ACTIVITY */}
                    <div className="lg:col-span-2 bg-[#111830] border border-gray-700/50 rounded-2xl p-6 shadow-lg">
                      <h2 className="text-lg font-bold text-white mb-4">Recent Activity</h2>
                      {data.recent_activity.length === 0 ? (
                        <div className="text-center py-8">
                          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" className="mx-auto mb-3 text-gray-600">
                            <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                          </svg>
                          <p className="text-sm text-gray-500">No activity yet.</p>
                          <p className="text-xs text-gray-600 mt-1">Start a learning path from Insight Hub to earn XP!</p>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          {data.recent_activity.map((act: DashboardActivity, i: number) => (
                            <button
                              key={i}
                              onClick={() => {
                                const qs = new URLSearchParams({ topic: act.lesson_title || act.lesson_id, mode: "learn" });
                                router.push(`/workspace/${act.lesson_id}?${qs.toString()}`);
                              }}
                              className="w-full flex items-center justify-between p-4 bg-[#0d1222] rounded-xl border border-gray-700/30 hover:border-cyan-500/30 transition cursor-pointer group text-left"
                            >
                              <div className="flex items-center gap-4">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${act.status === 'completed' ? 'bg-emerald-500/10' : 'bg-blue-500/10'}`}>
                                  {act.status === 'completed' ? (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                                      <path d="M20 6L9 17l-5-5" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                  ) : (
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                                      <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                    </svg>
                                  )}
                                </div>
                                <div>
                                  <p className="text-sm font-medium text-white group-hover:text-cyan-300 transition">{act.lesson_title || act.lesson_id}</p>
                                  <p className="text-xs text-gray-500">{timeAgo(act.updated_at)} • {act.status === 'completed' ? 'Completed' : 'In Progress'}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-3">
                                <div className="text-right">
                                  <div className="text-sm font-bold text-cyan-400">+{act.xp_earned} XP</div>
                                  <div className="flex items-center justify-end gap-1 mt-1">
                                    {[...Array(act.stars_earned)].map((_, j) => (
                                      <svg key={j} width="10" height="10" viewBox="0 0 24 24" fill="#facc15">
                                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="#facc15" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />
                                      </svg>
                                    ))}
                                  </div>
                                </div>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-gray-600 group-hover:text-cyan-400 transition">
                                  <path d="M9 18l6-6-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                              </div>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* OVERVIEW / PROGRESS SUMMARY */}
                    <div className="bg-[#111830] border border-gray-700/50 rounded-2xl p-6 shadow-lg">
                       <h2 className="text-lg font-bold text-white mb-4">Progress Summary</h2>
                       
                       <div className="space-y-6">
                         <div>
                           <div className="flex justify-between items-end mb-2">
                             <span className="text-sm text-gray-400 font-medium">XP Goal (10,000 XP)</span>
                             <span className="text-xs text-cyan-400 font-bold">{Math.min(100, (data.total_xp / 10000) * 100).toFixed(1)}%</span>
                           </div>
                           <div className="w-full h-2 bg-gray-700/50 rounded-full overflow-hidden">
                             <div className="h-full bg-cyan-500 rounded-full transition-all duration-1000" style={{ width: `${Math.min(100, (data.total_xp / 10000) * 100)}%` }} />
                           </div>
                         </div>

                         <div className="pt-2 border-t border-gray-700/30">
                           <div className="flex justify-between items-center mb-3">
                             <span className="text-sm text-gray-400 font-medium">Lessons Active</span>
                             <span className="text-xs text-blue-400 font-bold">{data.lessons_in_progress}</span>
                           </div>
                           <div className="flex justify-between items-center mb-3">
                             <span className="text-sm text-gray-400 font-medium">Lessons Completed</span>
                             <span className="text-xs text-emerald-400 font-bold">{data.lessons_completed}</span>
                           </div>
                           <div className="flex justify-between items-center">
                             <span className="text-sm text-gray-400 font-medium">Learning Paths</span>
                             <span className="text-xs text-purple-400 font-bold">{data.roadmaps?.length ?? 0}</span>
                           </div>
                         </div>

                         {data.roadmaps?.length === 0 && data.lessons_completed === 0 && (
                           <div className="pt-4 border-t border-gray-700/30">
                             <button
                               onClick={() => router.push("/insight-hub")}
                               className="w-full py-2.5 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 rounded-xl text-sm font-medium text-blue-400 transition"
                             >
                               Start Learning
                             </button>
                           </div>
                         )}
                       </div>
                    </div>
                  </div>
                </>
              ) : null}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
