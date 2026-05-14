"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/AuthContext";

/* ── data ─────────────────────────────────────────── */

const navLinks = [
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
];

const features = [
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l5.447 2.724A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" stroke="#a5b4fc" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    title: "Adaptive roadmaps",
    description:
      "Enter a topic and get a structured path with a variable number of modules sized to the breadth of what you want to learn—not a one-size-fits-all outline.",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#a5b4fc" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    title: "Socratic lesson workspace",
    description:
      "Each module pairs concise theory with three difficulty tiers and tiered hints so you practice actively instead of copying finished answers from a chatbot.",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M4 6h16M4 12h16M4 18h16" stroke="#a5b4fc" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
    title: "Insight Hub",
    description:
      "Your personal library for roadmaps and lessons: search new topics, see progress, and resume exactly where you stopped.",
  },
  {
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <path d="M12 2l2.4 7.2L22 12l-7.6 2.8L12 22l-2.4-7.2L2 12l7.6-2.8L12 2z" stroke="#a5b4fc" strokeWidth="1.5" strokeLinejoin="round" />
      </svg>
    ),
    title: "Progress that persists",
    description:
      "XP, stars, and lesson state are saved so your dashboard reflects real work—sign in with Google or email and pick up on any device.",
  },
];

const steps = [
  {
    number: "01",
    title: "Choose a topic",
    description:
      "From the Insight Hub, start a roadmap for the subject you are studying—especially dense first-year university material.",
  },
  {
    number: "02",
    title: "Work the modules",
    description:
      "Open a module to read short theory, answer easy–hard questions, and use hints when you are stuck—guided by the tutor, not handed solutions.",
  },
  {
    number: "03",
    title: "Save and return",
    description:
      "Your XP, stars, and lesson state stay in your account so you can close the tab and continue later from the dashboard.",
  },
];

/* ── component ──────────────────────────────────────── */

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (isLoading || isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#060816]">
        <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/75">
          Loading Cognito.ai...
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#060816] text-white">
      {/* ── background ── */}
      <div
        className="pointer-events-none fixed inset-0"
        style={{
          backgroundImage:
            "radial-gradient(circle at 50% 0%, rgba(165, 180, 252, 0.12), transparent 50%), radial-gradient(circle at 80% 50%, rgba(99, 102, 241, 0.08), transparent 40%)",
        }}
      />
      <div
        className="pointer-events-none fixed inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }}
      />

      {/* ── announcement banner ── */}
      <div className="relative z-30 flex items-center justify-center bg-gradient-to-r from-[#a5b4fc]/20 via-[#818cf8]/15 to-[#a5b4fc]/20 px-4 py-2.5 text-center text-sm backdrop-blur-sm border-b border-[#a5b4fc]/10">
        <span className="text-[#c7d2fe]">
          Start your first Socratic lesson session today&nbsp;
          <Link href="/signup" className="font-semibold text-white underline underline-offset-2 hover:text-[#e0e7ff] transition">
            Try it free →
          </Link>
        </span>
      </div>

      {/* ── header ── */}
      <header
        className={`sticky top-0 z-20 transition-all duration-300 ${
          scrolled
            ? "bg-[#060816]/80 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20"
            : "bg-transparent"
        }`}
      >
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 lg:px-10">
          {/* logo */}
          <div className="flex items-center gap-3">
            <Image
              src="/CognitoAI%20logo.svg"
              alt="Cognito.ai logo"
              width={156}
              height={114}
              priority
              unoptimized
              className="h-10 w-auto drop-shadow-[0_0_14px_rgba(165,180,252,0.25)]"
            />
            <span className="text-base font-bold tracking-[0.15em] text-white">
              Cognito.ai
            </span>
          </div>

          {/* desktop nav */}
          <nav className="hidden items-center gap-8 md:flex">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm text-white/60 transition hover:text-white"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* actions */}
          <div className="hidden items-center gap-3 md:flex">
            <Link
              href="/signin"
              className="text-sm font-medium text-white/70 transition hover:text-white"
            >
              Sign in
            </Link>
            <Link
              href="/signup"
              className="inline-flex items-center gap-1.5 rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-[#060816] transition hover:bg-[#e0e7ff] hover:shadow-lg hover:shadow-indigo-500/10"
            >
              Get started
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </Link>
          </div>

          {/* mobile menu toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="flex items-center justify-center w-10 h-10 rounded-lg text-white/70 hover:bg-white/5 transition md:hidden"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            )}
          </button>
        </div>

        {/* mobile menu */}
        {mobileMenuOpen && (
          <div className="border-t border-white/5 bg-[#060816]/95 backdrop-blur-xl px-6 pb-6 pt-4 md:hidden">
            <nav className="flex flex-col gap-4">
              {navLinks.map((link) => (
                <a
                  key={link.label}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="text-sm text-white/70 transition hover:text-white"
                >
                  {link.label}
                </a>
              ))}
              <hr className="border-white/10" />
              <Link href="/signin" className="text-sm text-white/70 hover:text-white transition">
                Sign in
              </Link>
              <Link
                href="/signup"
                className="inline-flex items-center justify-center gap-1.5 rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-[#060816] transition hover:bg-[#e0e7ff]"
              >
                Get started →
              </Link>
            </nav>
          </div>
        )}
      </header>

      {/* ── hero ── */}
      <section className="relative z-10 mx-auto max-w-6xl px-6 pt-20 pb-16 text-center lg:px-10 lg:pt-28 lg:pb-24">
        {/* tag */}
        <div className="landing-fade-in inline-flex items-center gap-2 rounded-full border border-[#a5b4fc]/20 bg-[#a5b4fc]/8 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-[#c7d2fe] mb-8">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-[#a5b4fc]" />
          Adaptive · Socratic · Built for students
        </div>

        <h1 className="landing-fade-in mx-auto max-w-3xl text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl" style={{ animationDelay: "0.1s" }}>
          Learn deeply without{" "}
          <span className="bg-gradient-to-r from-[#a5b4fc] to-[#818cf8] bg-clip-text text-transparent">
            AI dependency
          </span>
        </h1>

        <p className="landing-fade-in mx-auto mt-6 max-w-2xl text-lg leading-8 text-white/60 sm:text-xl" style={{ animationDelay: "0.2s" }}>
          Cognito.ai is an adaptive learning platform for university-level topics: structured roadmaps,
          interactive lessons with tiered questions and hints, and saved progress—so you build concepts instead of
          collecting instant answers.
        </p>

        <div className="landing-fade-in mt-10 flex flex-wrap items-center justify-center gap-4" style={{ animationDelay: "0.3s" }}>
          <Link
            href="/signup"
            className="group inline-flex items-center gap-2 rounded-full bg-white px-7 py-3.5 text-sm font-semibold text-[#060816] transition hover:bg-[#e0e7ff] hover:shadow-xl hover:shadow-indigo-500/15"
          >
            See it in action
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="transition-transform group-hover:translate-x-0.5">
              <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </Link>
          <Link
            href="/signin"
            className="inline-flex items-center justify-center rounded-full border border-white/12 bg-white/5 px-7 py-3.5 text-sm font-semibold text-white transition hover:bg-white/10"
          >
            Sign in
          </Link>
        </div>

        {/* hero preview — mirrors lesson workspace (theory + question + hint), not a free-form answer bot */}
        <div className="landing-fade-in landing-float relative mx-auto mt-16 max-w-2xl" style={{ animationDelay: "0.5s" }}>
          <div className="absolute -inset-4 rounded-3xl bg-gradient-to-b from-[#a5b4fc]/10 to-transparent blur-2xl" />
          <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#0b0f1e]/80 shadow-2xl shadow-black/40">
            <div className="px-5 py-4 border-b border-white/5 flex items-center justify-between gap-3">
              <div className="flex gap-1.5">
                <span className="h-3 w-3 rounded-full bg-white/10" />
                <span className="h-3 w-3 rounded-full bg-white/10" />
                <span className="h-3 w-3 rounded-full bg-white/10" />
              </div>
              <span className="text-xs text-white/50 font-medium tracking-wide uppercase truncate">
                Lesson · Loss and gradients
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-amber-300/90 shrink-0">Medium</span>
            </div>

            <div className="px-5 py-5 space-y-4 text-left">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#a5b4fc]/80 mb-2">Theory</p>
                <p className="text-sm text-white/70 leading-relaxed">
                  Training adjusts weights using the gradient of the loss with respect to parameters—small steps in the direction that reduces error.
                </p>
              </div>

              <div className="rounded-xl border border-white/8 bg-[#0a0e1c]/90 p-4">
                <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-white/40 mb-2">Question</p>
                <p className="text-sm text-white/85 mb-3">
                  In one sentence, what does backpropagation compute for each weight?
                </p>
                <div className="rounded-lg border border-dashed border-white/15 bg-[#060816]/60 px-3 py-2.5 text-xs text-white/35">
                  Type your answer…
                </div>
              </div>

              <div className="rounded-xl border border-[#a5b4fc]/20 bg-[#a5b4fc]/6 p-4">
                <div className="flex items-center justify-between gap-2 mb-2">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#c7d2fe]">Hint</p>
                  <span className="text-[10px] text-white/35">Tier 1</span>
                </div>
                <p className="text-xs text-white/65 leading-relaxed">
                  Think about which derivative links a small change in a weight to a small change in the loss—what quantity captures that relationship?
                </p>
              </div>
            </div>

            <div className="px-5 py-3 border-t border-white/5 flex items-center justify-between gap-3 text-xs text-white/40">
              <span>Submit answer · Request deeper hint</span>
              <span className="text-emerald-400/80 font-medium">+XP on correct</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── features ── */}
      <section id="features" className="relative z-10 mx-auto max-w-6xl px-6 py-20 lg:px-10">
        <div className="text-center mb-14">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#a5b4fc]/70 mb-3">Features</p>
          <h2 className="text-3xl font-bold text-white sm:text-4xl">What Cognito.ai actually does</h2>
          <p className="mx-auto mt-4 max-w-xl text-base text-white/50">
            Adaptive roadmaps, lesson nodes with theory and tiered questions, Socratic hints instead of answer dumps—and XP, stars, and lesson state that persist to your account.
          </p>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="group rounded-2xl border border-white/8 bg-white/[0.03] p-6 transition hover:border-[#a5b4fc]/20 hover:bg-white/[0.05] hover:shadow-lg hover:shadow-indigo-500/5"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-[#a5b4fc]/10 transition group-hover:bg-[#a5b4fc]/15">
                {f.icon}
              </div>
              <h3 className="text-sm font-semibold text-white mb-2">{f.title}</h3>
              <p className="text-sm leading-6 text-white/50">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── how it works ── */}
      <section id="how-it-works" className="relative z-10 mx-auto max-w-6xl px-6 py-20 lg:px-10">
        <div className="text-center mb-14">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#a5b4fc]/70 mb-3">How it works</p>
          <h2 className="text-3xl font-bold text-white sm:text-4xl">Start learning in three steps</h2>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {steps.map((step) => (
            <div key={step.number} className="relative">
              <div className="flex items-start gap-5">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-[#a5b4fc]/15 to-[#818cf8]/10 text-lg font-bold text-[#a5b4fc] border border-[#a5b4fc]/10">
                  {step.number}
                </div>
                <div>
                  <h3 className="text-base font-semibold text-white mb-2">{step.title}</h3>
                  <p className="text-sm leading-6 text-white/50">{step.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="relative z-10 mx-auto max-w-6xl px-6 py-20 lg:px-10">
        <div className="rounded-[2rem] border border-[#a5b4fc]/15 bg-gradient-to-br from-[#a5b4fc]/8 to-[#0f1224]/50 p-10 text-center backdrop-blur sm:p-14">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#c7d2fe]/70 mb-4">Ready when you are</p>
          <h2 className="text-2xl font-bold text-white sm:text-3xl lg:text-4xl mb-4">
            Start your first guided session in seconds.
          </h2>
          <p className="mx-auto max-w-lg text-base text-white/50 mb-8">
            Sign up with Google or email, open the Insight Hub, generate a roadmap for a topic, and work lessons at your own pace—your dashboard keeps the thread.
          </p>
          <Link
            href="/signup"
            className="group inline-flex items-center gap-2 rounded-full bg-white px-7 py-3.5 text-sm font-semibold text-[#060816] transition hover:bg-[#e0e7ff] hover:shadow-xl hover:shadow-indigo-500/15"
          >
            Get started for free
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="transition-transform group-hover:translate-x-0.5">
              <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </Link>
        </div>
      </section>

      {/* ── footer ── */}
      <footer className="relative z-10 border-t border-white/5 py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 sm:flex-row lg:px-10">
          <div className="flex items-center gap-2">
            <Image
              src="/CognitoAI%20logo.svg"
              alt="Cognito.ai"
              width={80}
              height={60}
              unoptimized
              className="h-6 w-auto opacity-60"
            />
            <span className="text-xs text-white/40">Cognito.ai</span>
          </div>
          <p className="text-xs text-white/30">
            © {new Date().getFullYear()} Cognito.ai. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="/terms" className="text-xs text-white/40 hover:text-white/60 transition">Terms</a>
            <a href="/privacy" className="text-xs text-white/40 hover:text-white/60 transition">Privacy</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
