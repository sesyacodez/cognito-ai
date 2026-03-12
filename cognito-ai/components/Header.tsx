"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { useRouter } from "next/navigation";

export function Header() {
  const { user, logout, isAuthenticated } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  return (
    <header className="bg-[#0f1224] border-b border-gray-700">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/insight-hub" className="text-2xl font-bold text-white">
          COGNITO.AI
        </Link>

        <nav className="flex items-center gap-6">
          {isAuthenticated && (
            <>
              <Link
                href="/insight-hub"
                className="text-gray-300 hover:text-white transition"
              >
                Insight Hub
              </Link>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-300">{user?.name}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-white text-black rounded hover:bg-gray-200 transition text-sm"
                >
                  Logout
                </button>
              </div>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
