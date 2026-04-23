"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";

const featureCards = [
  {
    title: "Adaptive lessons",
    description:
      "Cognito.AI adjusts the next prompt based on how you respond, so the path stays relevant.",
  },
  {
    title: "Guided practice",
    description:
      "Each session keeps you active with feedback, nudges, and Socratic follow-ups.",
  },
  {
    title: "Progress dashboard",
    description:
      "Track streaks, roadmaps, and recent activity from one focused starting point.",
  },
];

const journeySteps = [
  {
    title: "Pick a roadmap",
    description:
      "Choose the goal you want to work on and let the app organize the path ahead.",
  },
  {
    title: "Learn by doing",
    description:
      "Work through prompts and feedback loops that keep the lesson interactive.",
  },
  {
    title: "Return to the dashboard",
    description:
      "Jump back in anytime and continue from the next best step.",
  },
];

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading || isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#060816]">
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/75">
          Loading Cognito.AI...
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#060816] text-white">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(circle at top left, rgba(165, 180, 252, 0.22), transparent 34%), radial-gradient(circle at 85% 20%, rgba(165, 180, 252, 0.18), transparent 28%), linear-gradient(180deg, #08111f 0%, #060816 45%, #05060d 100%)",
        }}
      />
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px)",
          backgroundSize: "72px 72px",
        }}
      />

      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-6 lg:px-10">
        <header className="flex items-center justify-between gap-4 border-b border-white/10 pb-6">
          <div className="flex items-center gap-3">
            <Image
              src="/CognitoAI%20logo.svg"
              alt="Cognito.AI logo"
              width={156}
              height={114}
              priority
              unoptimized
              className="h-12 w-auto drop-shadow-[0_0_18px_rgba(165,180,252,0.28)]"
            />
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-[#c7d2fe]">
                Cognito.AI
              </p>
              <p className="text-xs text-white/55">Adaptive learning mentor</p>
            </div>
          </div>

          <Link
            href="/signin"
            className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-white/85 transition hover:bg-white/10"
          >
            Sign in
          </Link>
        </header>

        <main className="grid flex-1 items-center gap-12 py-10 lg:grid-cols-[1.08fr_0.92fr] lg:py-16">
          <section className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#a5b4fc]/20 bg-[#a5b4fc]/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-[#e0e7ff]">
              Your AI mentor, ready on startup
            </div>

            <div className="space-y-5">
              <h1 className="max-w-2xl text-5xl font-semibold tracking-tight text-white sm:text-6xl lg:text-7xl">
                Learn faster with a mentor that keeps the next step obvious.
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-white/70 sm:text-xl">
                Cognito.AI turns roadmaps, practice, and progress tracking into one
                guided flow. Open the app, choose your path, and keep moving without
                getting lost in menus.
              </p>
            </div>

            <div className="flex flex-wrap gap-4">
              <Link
                href="/signup"
                className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-[#08111f] transition hover:bg-[#e0e7ff]"
              >
                Try out now
              </Link>
              <Link
                href="/signin"
                className="inline-flex items-center justify-center rounded-full border border-white/15 bg-white/5 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10"
              >
                Sign in
              </Link>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {featureCards.map((feature) => (
                <article
                  key={feature.title}
                  className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur"
                >
                  <p className="text-sm font-semibold text-white">{feature.title}</p>
                  <p className="mt-2 text-sm leading-6 text-white/60">
                    {feature.description}
                  </p>
                </article>
              ))}
            </div>
          </section>

          <aside className="space-y-4">
            <div className="rounded-[2rem] border border-white/10 bg-white/5 p-5 shadow-2xl backdrop-blur">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-[#c7d2fe]/80">
                    At a glance
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-white">
                    What Cognito.AI feels like
                  </h2>
                </div>
                <div className="rounded-full border border-[#a5b4fc]/20 bg-[#a5b4fc]/15 px-3 py-1 text-xs font-medium text-[#eef2ff]">
                  Live learning
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {journeySteps.map((step, index) => (
                  <div
                    key={step.title}
                    className="flex gap-4 rounded-2xl border border-white/10 bg-[#0a1020]/80 px-4 py-4"
                  >
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/10 text-sm font-semibold text-[#e0e7ff]">
                      {String(index + 1).padStart(2, "0")}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">{step.title}</p>
                      <p className="mt-1 text-sm leading-6 text-white/65">
                        {step.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[2rem] border border-[#a5b4fc]/20 bg-[#a5b4fc]/10 p-5">
              <p className="text-xs uppercase tracking-[0.3em] text-[#e0e7ff]/80">
                Why it stands out
              </p>
              <p className="mt-3 text-sm leading-6 text-[#eef2ff]/90">
                Cognito.AI keeps the experience focused: a clear roadmap, guided
                practice, and a dashboard that shows progress at a glance.
              </p>
            </div>
          </aside>
        </main>

        <section className="pb-10">
          <div className="rounded-[2rem] border border-white/10 bg-white/5 p-6 backdrop-blur">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
              <div className="max-w-2xl">
                <p className="text-xs uppercase tracking-[0.3em] text-[#c7d2fe]/80">
                  Ready when you are
                </p>
                <h2 className="mt-3 text-2xl font-semibold text-white sm:text-3xl">
                  Start your first guided session in seconds.
                </h2>
                <p className="mt-3 text-sm leading-6 text-white/65">
                  Create an account, try the onboarding flow, and jump into the
                  dashboard whenever you come back.
                </p>
              </div>

              <Link
                href="/signup"
                className="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-[#08111f] transition hover:bg-[#e0e7ff]"
              >
                Try out now
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
