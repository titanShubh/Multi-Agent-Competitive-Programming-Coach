'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { Navbar } from '@/components/layout/Navbar';
import { StatsCards } from '@/components/dashboard/StatsCards';
import { TopicRadar } from '@/components/dashboard/TopicRadar';
import { ProgressChart } from '@/components/dashboard/ProgressChart';
import { PlusCircle, Loader2, Play, BookOpen, Clock, Settings } from 'lucide-react';
import Link from 'next/link';
import { ProblemsBrowser } from '@/components/dashboard/ProblemsBrowser';

export default function DashboardPage() {
  const router = useRouter();
  const {
    user,
    token,
    authLoading,
    sessions,
    loadingSessions,
    activeSessionLoading,
    loadSessions,
    createSession,
  } = useStore();

  const [problemText, setProblemText] = useState('');
  const [sessionMode, setSessionMode] = useState<'learning' | 'contest'>('learning');
  const [timerDuration, setTimerDuration] = useState<number | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  // Authenticate user & load sessions
  useEffect(() => {
    if (!token && !authLoading) {
      router.push('/login');
    }
  }, [token, authLoading, router]);

  useEffect(() => {
    if (token) {
      loadSessions();
    }
  }, [token, loadSessions]);

  const handleStartSession = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!problemText.trim() || problemText.length < 10) {
      setError('Problem statement must be at least 10 characters long.');
      return;
    }
    try {
      const session = await createSession(problemText, sessionMode, timerDuration);
      router.push(`/session/${session.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start coaching session');
    }
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-dark-950 flex flex-col justify-center items-center text-dark-400">
        <Loader2 className="w-8 h-8 animate-spin text-brand-500 mb-2" />
        <p className="text-sm font-mono">Loading profile...</p>
      </div>
    );
  }

  // Aggregate stats from the user learning profile
  const totalAttempted = user.total_problems_attempted || sessions.length;
  // If user profile has solved count, use it. Otherwise count sessions which are not active
  const totalSolved = user.total_problems_solved || sessions.filter(s => s.status === 'completed').length;
  const totalHints = user.total_hints_used || 0;

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col">
      <Navbar />

      <main className="max-w-7xl mx-auto w-full px-6 py-8 flex-1 space-y-8 z-10 relative">
        {/* Welcome Banner */}
        <div className="space-y-1 text-left">
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Coaching Dashboard
          </h1>
          <p className="text-sm text-dark-400">
            Welcome back, <span className="text-brand-300 font-semibold">{user.display_name || user.username}</span>. Paste a competitive programming problem below to begin your Socratic session.
          </p>
        </div>

        {/* Stats Cards Grid */}
        <StatsCards
          attempted={totalAttempted}
          solved={totalSolved}
          hintsUsed={totalHints}
          rating={user.current_rating}
        />

        {/* Workspace Actions: New Session + History */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Paste Problem Statement Form */}
          <div className="lg:col-span-7 space-y-6">
            <div className="glass rounded-xl p-5 space-y-4">
              <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2 border-b border-white/10 pb-3">
                <PlusCircle className="w-4 h-4 text-brand-400" />
                Initialize Coaching Session
              </h3>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 text-xs text-red-400 text-center font-medium">
                  {error}
                </div>
              )}

              <form onSubmit={handleStartSession} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-semibold font-mono text-dark-400 tracking-wider">
                    Problem Statement (include sample inputs/outputs)
                  </label>
                  <textarea
                    value={problemText}
                    onChange={(e) => setProblemText(e.target.value)}
                    placeholder="Paste the full competitive programming problem statement here..."
                    disabled={activeSessionLoading}
                    rows={8}
                    className="w-full bg-dark-900 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-dark-500 outline-none focus:border-brand-500 transition-colors resize-none disabled:opacity-50"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Mode Selector */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-semibold font-mono text-dark-400 tracking-wider flex items-center gap-1">
                      <Settings className="w-3 h-3 text-brand-400" />
                      Session Mode
                    </label>
                    <select
                      value={sessionMode}
                      onChange={(e) => setSessionMode(e.target.value as any)}
                      disabled={activeSessionLoading}
                      className="w-full bg-dark-900 border border-white/10 text-white rounded-xl px-3 py-2.5 text-sm outline-none focus:border-brand-500 cursor-pointer disabled:opacity-50"
                    >
                      <option value="learning">Learning Mode (Socratic hints)</option>
                      <option value="contest">Contest Mode (No hints, only clarification)</option>
                    </select>
                  </div>

                  {/* Timer input */}
                  <div className="space-y-1">
                    <label className="text-[10px] uppercase font-semibold font-mono text-dark-400 tracking-wider flex items-center gap-1">
                      <Clock className="w-3 h-3 text-brand-400" />
                      Duration Timer (optional)
                    </label>
                    <input
                      type="number"
                      value={timerDuration || ''}
                      onChange={(e) => setTimerDuration(e.target.value ? parseInt(e.target.value) : undefined)}
                      placeholder="Minutes (e.g. 45)"
                      min={1}
                      max={180}
                      disabled={activeSessionLoading}
                      className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-sm text-white placeholder-dark-500 outline-none focus:border-brand-500 transition-colors disabled:opacity-50"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={activeSessionLoading || !problemText.trim()}
                  className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-brand-500/15 flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 disabled:active:scale-100"
                >
                  {activeSessionLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Analyzing Problem & Starting Graph...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-white" />
                      Start Socratic Session
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Session History List */}
          <div className="lg:col-span-5 space-y-6">
            <div className="glass rounded-xl p-5 space-y-4 h-[440px] flex flex-col">
              <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2 border-b border-white/10 pb-3">
                <BookOpen className="w-4 h-4 text-brand-400" />
                Recent Sessions
              </h3>

              <div className="flex-1 overflow-y-auto space-y-2 pr-1 scrollbar-thin">
                {loadingSessions ? (
                  <div className="h-full flex items-center justify-center text-dark-500 text-xs">
                    <Loader2 className="w-5 h-5 animate-spin mr-1.5" />
                    Fetching sessions...
                  </div>
                ) : sessions.length > 0 ? (
                  sessions.map((sess) => (
                    <Link
                      key={sess.id}
                      href={`/session/${sess.id}`}
                      className="block p-3 rounded-xl bg-white/5 border border-white/10 hover:border-brand-500/30 hover:bg-brand-500/[0.02] transition-all text-left"
                    >
                      <div className="flex items-center justify-between text-xs mb-1.5">
                        <span className="font-bold text-white tracking-tight truncate max-w-[70%]">
                          {sess.problem_analysis?.title || 'CP Session'}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[9px] font-semibold tracking-wider font-mono uppercase ${
                          sess.status === 'completed' 
                            ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' 
                            : 'bg-brand-500/10 border border-brand-500/20 text-brand-300'
                        }`}>
                          {sess.status}
                        </span>
                      </div>
                      <p className="text-[11px] text-dark-400 line-clamp-2 leading-relaxed">
                        {sess.problem_analysis?.summary || sess.problem_statement}
                      </p>
                      <div className="flex gap-3 text-[9px] text-dark-500 font-mono mt-2 pt-1.5 border-t border-white/5 uppercase">
                        <span>Mode: {sess.session_mode}</span>
                        <span>Hints: {sess.hint_level}</span>
                        <span>Date: {new Date(sess.started_at).toLocaleDateString()}</span>
                      </div>
                    </Link>
                  ))
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center text-dark-500 space-y-1">
                    <p className="text-xs font-semibold">No active sessions</p>
                    <p className="text-[10px] max-w-[180px]">
                      Paste a problem on the left to start learning.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Charts & Analytics Visuals */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <TopicRadar proficiency={user.topic_proficiency || {}} />
          <ProgressChart rating={user.current_rating} />
        </div>

        {/* Problems Browser */}
        <ProblemsBrowser />
      </main>
    </div>
  );
}
