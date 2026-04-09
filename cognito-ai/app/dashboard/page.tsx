"use client";

import React, { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { useAuth } from "@/lib/AuthContext";
import { useRouter } from "next/navigation";
import { fetchDashboard, DashboardData, DashboardActivity } from "@/lib/dashboard";

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

                  {/* BOTTOM SECTION */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* RECENT ACTIVITY */}
                    <div className="lg:col-span-2 bg-[#111830] border border-gray-700/50 rounded-2xl p-6 shadow-lg">
                      <h2 className="text-lg font-bold text-white mb-4">Recent Activity</h2>
                      {data.recent_activity.length === 0 ? (
                        <p className="text-sm text-gray-500">No activity yet. Start learning to earn XP!</p>
                      ) : (
                        <div className="space-y-4">
                          {data.recent_activity.map((act: DashboardActivity, i: number) => (
                            <div key={i} className="flex items-center justify-between p-4 bg-[#0d1222] rounded-xl border border-gray-700/30 hover:border-gray-600/50 transition">
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
                                  <p className="text-sm font-medium text-white">Lesson {act.lesson_id.split('-')[0]}...</p>
                                  <p className="text-xs text-gray-500">{timeAgo(act.updated_at)} • {act.status === 'completed' ? 'Completed' : 'In Progress'}</p>
                                </div>
                              </div>
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
                            </div>
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

                         <div>
                           <div className="flex justify-between items-end mb-2">
                             <span className="text-sm text-gray-400 font-medium">Lessons Active</span>
                             <span className="text-xs text-blue-400 font-bold">{data.lessons_in_progress}</span>
                           </div>
                         </div>
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
