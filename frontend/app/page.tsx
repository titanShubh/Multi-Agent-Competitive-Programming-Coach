'use client';

import React from 'react';
import Link from 'next/link';
import { Compass, BookOpen, Terminal, Sparkles, HelpCircle, Code2, Users, ArrowRight } from 'lucide-react';

export default function LandingPage() {
  const features = [
    {
      title: 'Problem Analyzer',
      desc: 'Parses problems, extracts constraints, identifies categories, and identifies key observations.',
      icon: BookOpen,
      color: 'text-blue-400',
    },
    {
      title: 'Socratic Coach',
      desc: 'Core guide that asks questions, provides hints, and leads you through the reasoning timeline.',
      icon: Compass,
      color: 'text-brand-400',
    },
    {
      title: 'Code Reviewer',
      desc: 'Pinpoints bugs and logical errors line-by-line without writing the fixed code for you.',
      icon: Code2,
      color: 'text-rose-400',
    },
    {
      title: 'Algorithm Expert',
      desc: 'Breaks down algorithms conceptually using analogies and interactive complexity comparisons.',
      icon: Sparkles,
      color: 'text-emerald-400',
    },
  ];

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col justify-between relative overflow-hidden select-none">
      {/* Decorative background glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-brand-600/10 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/10 blur-[120px] rounded-full" />

      {/* Header */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex justify-between items-center z-10 relative">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <span className="text-sm font-bold tracking-wider uppercase font-mono text-white">
            ICPC Coach
          </span>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-semibold text-dark-300 hover:text-white transition-colors">
            Log In
          </Link>
          <Link
            href="/register"
            className="text-xs font-bold uppercase tracking-wider font-mono bg-brand-600 hover:bg-brand-500 text-white px-4 py-2 rounded-xl transition-all shadow-lg shadow-brand-500/15 hover:shadow-brand-500/25 active:scale-95"
          >
            Sign Up
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto w-full px-6 flex-1 flex flex-col justify-center py-12 z-10 relative">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Hero Content */}
          <div className="lg:col-span-7 space-y-6 text-left">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 text-xs text-brand-300 font-semibold font-mono">
              <Sparkles className="w-3.5 h-3.5" />
              Multi-Agent Socratic Mentor
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight text-white">
              Don't just get answers.<br />
              Learn how to <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-400 to-indigo-400">solve them.</span>
            </h1>

            <p className="text-base text-dark-300 leading-relaxed max-w-xl">
              Behave like a senior ICPC coach. Upload problem statements, write your attempted solutions, and progress through hints, edge cases, and code reviews without leaking solutions too early.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 pt-2">
              <Link
                href="/register"
                className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-bold px-7 py-3.5 rounded-xl transition-all shadow-lg shadow-brand-500/20 active:scale-95"
              >
                Start Coaching
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 bg-white/5 border border-white/10 hover:bg-white/10 text-white font-bold px-7 py-3.5 rounded-xl transition-all active:scale-95"
              >
                Go to Dashboard
              </Link>
            </div>
          </div>

          {/* Feature Cards Grid */}
          <div className="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div key={idx} className="glass rounded-xl p-5 space-y-3 hover:border-white/15 transition-all">
                  <div className={`w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center ${feat.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-sm font-bold text-white tracking-tight">{feat.title}</h3>
                  <p className="text-xs text-dark-400 leading-relaxed">{feat.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-dark-950/50 py-6 text-center text-xs text-dark-500 z-10 relative">
        <p>© 2026 ICPC Socratic Coach. Powered by DeepMind Advanced Agentic Coding.</p>
      </footer>
    </div>
  );
}
