"use client";

import Link from "next/link";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";

export default function SignIn() {
  const router = useRouter();
  const { login, loginWithGoogle, isLoading, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, router]);

  async function handleEmailLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      await login(email, password);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Login failed. Please try again."
      );
    }
  }

  async function handleGoogleLogin() {
    setError("");
    try {
      await loginWithGoogle();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Google login failed. Please try again."
      );
    }
  }

  if (isLoading || isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#0b0f1e]">
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/75">
          {isAuthenticated ? "Redirecting to dashboard..." : "Loading Cognito.AI..."}
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0b0f1e] font-sans">
      <main className="w-full max-w-sm rounded-2xl bg-[#0f1224] bg-opacity-90 p-8 shadow-2xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">
              Cognito.AI
            </p>
            <h1 className="mt-2 text-3xl font-bold text-white">Welcome back</h1>
          </div>
          <Link href="/" className="text-xs text-gray-400 underline">
            Landing page
          </Link>
        </div>

        <p className="mt-2 text-sm text-gray-300">
          Sign in to continue your learning path.
        </p>

        <div className="mt-6 space-y-3">
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={isLoading}
            className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-md bg-white px-4 py-2 text-black transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 488 512"
              className="h-5 w-5"
            >
              <path
                fill="#4285F4"
                d="M488 261.8c0-17.4-1.6-34.1-4.6-50.4H249v95.5h134.8c-5.8 31.2-23.5 57.7-50
                75.5v62.7h80.9c47.3-43.6 74.3-107.7 74.3-183.3z"
              />
              <path
                fill="#34A853"
                d="M249 512c67.2 0 123.7-22.4 164.9-60.7l-80.9-62.7c-22.6 15.2-51.4
                24.2-84 24.2-64.6 0-119.4-43.6-139.1-102.2H28.9v64.3C70.1 467.4 154.5 512 249
                512z"
              />
              <path
                fill="#FBBC05"
                d="M109.9 307.7c-4.8-14.4-7.6-29.6-7.6-45.3s2.8-30.9
                7.6-45.3V152h-81C7.1 195.9 0 230.4 0 262.4s7.1 66.5 28.9
                110L109.9 307.7z"
              />
              <path
                fill="#EA4335"
                d="M249 100.8c35.6 0 67.7 12.3 93 36.3l69.7-69.7C364.7
                29.2 308.2 0 249 0 154.5 0 70.1 44.6 28.9
                111l81 64.3c19.7-58.6 74.5-102.2 139.1-102.2z"
              />
            </svg>
            {isLoading ? "Signing in..." : "Continue with Google"}
          </button>

          <form className="mt-4 space-y-3" onSubmit={handleEmailLogin}>
            {error && (
              <div className="rounded border border-red-700 bg-red-950 p-2 text-xs text-red-200">
                {error}
              </div>
            )}
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
              required
              className="w-full rounded-md border border-white px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
              required
              className="w-full rounded-md border border-white px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-md bg-white px-4 py-2 text-black transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>
        </div>

        <p className="mt-6 text-center text-xs text-gray-400">
          By connecting you agree to our{" "}
          <a href="/terms" className="underline">
            Terms of Service
          </a>{" "}
          and{" "}
          <a href="/privacy" className="underline">
            Privacy Policy
          </a>
          .
        </p>
        <p className="mt-4 text-center text-xs text-gray-400">
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="underline">
            Try out now
          </Link>
        </p>
      </main>
    </div>
  );
}