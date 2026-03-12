"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function SignUp() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState<{ name?: string; email?: string; password?: string; confirmPassword?: string; general?: string }>({});
  const [loading, setLoading] = useState(false);

  function validate() {
    const e: typeof errors = {};
    if (!name.trim()) e.name = "Name is required.";
    if (!email.trim()) e.email = "Email is required.";
    if (!password) e.password = "Password is required.";
    if (!confirmPassword) {
      e.confirmPassword = "Please confirm your password.";
    } else if (password && password !== confirmPassword) {
      e.confirmPassword = "Passwords do not match.";
    }
    return e;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    setErrors({});
    setLoading(true);
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setErrors({ general: data?.detail ?? "Registration failed. Please try again." });
        return;
      }
      router.push("/");
    } catch {
      setErrors({ general: "Network error. Please try again." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0b0f1e] font-sans">
      {/* card container */}
      <main className="w-full max-w-sm rounded-2xl bg-[#0f1224] bg-opacity-90 p-8 shadow-2xl">
        <h1 className="text-center text-3xl font-bold text-white pb-5">
          COGNITO.AI
        </h1>
        <p className="mt-2 text-center text-sm text-gray-300">
          Create your account<br />
          <span className="text-xs text-gray-400">
            An AI mentor that actually teaches.
          </span>
        </p>

        <div className="mt-6 space-y-3">
          <button
            type="button"
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-white text-black rounded-md hover:bg-gray-100 transition cursor-pointer"
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
            Continue with Google
          </button>

          {/* registration form */}
          <form className="space-y-3 mt-4" onSubmit={handleSubmit} noValidate>
            <div>
              <input
                type="text"
                name="name"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2 bg-transparent border border-white text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.name && <p className="mt-1 text-xs text-red-400">{errors.name}</p>}
            </div>
            <div>
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 bg-transparent border border-white text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.email && <p className="mt-1 text-xs text-red-400">{errors.email}</p>}
            </div>
            <div>
              <input
                type="password"
                name="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 bg-transparent border border-white text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.password && <p className="mt-1 text-xs text-red-400">{errors.password}</p>}
            </div>
            <div>
              <input
                type="password"
                name="confirmPassword"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2 bg-transparent border border-white text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.confirmPassword && <p className="mt-1 text-xs text-red-400">{errors.confirmPassword}</p>}
            </div>
            {errors.general && <p className="text-xs text-red-400 text-center">{errors.general}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-white text-black rounded-md hover:bg-gray-100 transition cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? "Creating…" : "Create Account"}
            </button>
          </form>
        </div>

        <p className="mt-6 text-xs text-center text-gray-400">
          By connecting you agree to our{' '}
          <a href="/terms" className="underline">
            Terms of Service
          </a>{' '}
          and{' '}
          <a href="/privacy" className="underline">
            Privacy Policy
          </a>.
        </p>
        <p className="mt-4 text-xs text-center text-gray-400">
          Already have an account?{' '}
          <a href="/" className="underline">
            Sign in
          </a>
        </p>
      </main>
    </div>
  );
}
