"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { getSession } from "@/lib/auth";

interface Roadmap {
  id: string;
  topic: string;
  modules: Array<{
    order: number;
    title: string;
    description: string;
  }>;
  createdAt?: string;
}

export default function InsightHub() {
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newTopic, setNewTopic] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetchRoadmaps();
  }, []);

  async function fetchRoadmaps() {
    setIsLoading(true);
    setError("");
    try {
      const session = getSession();
      const headers = session ? { Authorization: `Bearer ${session.token}` } : {};

      const res = await fetch("/api/roadmaps", {
        headers: { ...headers, "Content-Type": "application/json" },
      });

      if (!res.ok) {
        throw new Error("Failed to fetch roadmaps");
      }

      const data = await res.json();
      setRoadmaps(data || []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load roadmaps"
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateRoadmap(e: React.FormEvent) {
    e.preventDefault();
    if (!newTopic.trim()) return;

    setIsCreating(true);
    setError("");
    try {
      const session = getSession();
      const headers = session ? { Authorization: `Bearer ${session.token}` } : {};

      const res = await fetch("/api/roadmaps", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ topic: newTopic }),
      });

      if (!res.ok) {
        throw new Error("Failed to create roadmap");
      }

      const newRoadmap = await res.json();
      setRoadmaps((prev) => [newRoadmap, ...prev]);
      setNewTopic("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create roadmap"
      );
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#0b0f1e]">
        <Header />

        <main className="max-w-6xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-white mb-8">Insight Hub</h1>

          {/* Create Roadmap Form */}
          <div className="mb-12">
            <form
              onSubmit={handleCreateRoadmap}
              className="bg-[#0f1224] rounded-lg p-6 border border-gray-700"
            >
              <h2 className="text-xl font-semibold text-white mb-4">
                Create New Learning Path
              </h2>
              {error && (
                <div className="mb-4 p-3 bg-red-950 border border-red-700 rounded text-red-200 text-sm">
                  {error}
                </div>
              )}
              <div className="flex gap-3">
                <input
                  type="text"
                  value={newTopic}
                  onChange={(e) => setNewTopic(e.target.value)}
                  disabled={isCreating}
                  placeholder="What would you like to learn?"
                  className="flex-1 px-4 py-2 bg-transparent border border-white text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60 placeholder-gray-400"
                />
                <button
                  type="submit"
                  disabled={isCreating || !newTopic.trim()}
                  className="px-6 py-2 bg-white text-black rounded hover:bg-gray-200 transition disabled:opacity-60 disabled:cursor-not-allowed font-medium"
                >
                  {isCreating ? "Creating..." : "Create"}
                </button>
              </div>
            </form>
          </div>

          {/* Roadmaps Grid */}
          {isLoading ? (
            <div className="text-center py-12">
              <div className="text-gray-300">Loading your learning paths...</div>
            </div>
          ) : roadmaps.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400">
                No learning paths yet. Create one to get started!
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {roadmaps.map((roadmap) => (
                <div
                  key={roadmap.id}
                  className="bg-[#0f1224] rounded-lg p-6 border border-gray-700 hover:border-blue-500 transition cursor-pointer"
                >
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {roadmap.topic}
                  </h3>
                  <p className="text-sm text-gray-400 mb-4">
                    {roadmap.modules?.length || 0} modules
                  </p>
                  <div className="space-y-2">
                    {roadmap.modules?.slice(0, 3).map((module) => (
                      <div key={module.order} className="text-xs text-gray-300">
                        <span className="text-blue-400">Module {module.order}:</span>{" "}
                        {module.title}
                      </div>
                    ))}
                    {roadmap.modules?.length > 3 && (
                      <div className="text-xs text-gray-500">
                        +{roadmap.modules.length - 3} more modules
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  );
}
