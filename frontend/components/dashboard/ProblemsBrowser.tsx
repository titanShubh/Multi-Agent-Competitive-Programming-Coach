'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { api } from '@/lib/api';
import {
  Library,
  Loader2,
  Play,
  Tag,
  Signal,
  ExternalLink,
  Search,
  Filter,
  AlertTriangle,
} from 'lucide-react';

interface Problem {
  id: string;
  title: string;
  statement: string;
  constraints?: string;
  input_format?: string;
  output_format?: string;
  sample_io?: { input: string; output: string }[];
  source?: string;
  source_id?: string;
  source_url?: string;
  difficulty?: string;
  estimated_rating?: number;
  categories: string[];
  tags: string[];
  created_at: string;
}

const DIFFICULTY_STYLES: Record<string, string> = {
  Easy: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  Medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  Hard: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
};

const CATEGORY_FILTERS = ['All', 'DP', 'Graphs', 'Greedy', 'Math', 'Trees', 'Strings', 'Binary Search'];

function getDifficultyStyle(difficulty?: string): string {
  if (!difficulty) return 'bg-dark-700/50 text-dark-400 border-white/10';
  return DIFFICULTY_STYLES[difficulty] || 'bg-dark-700/50 text-dark-400 border-white/10';
}

/**
 * Reconstruct the full problem statement text from structured problem data
 * so it can be pasted into the session creation flow.
 */
function buildProblemStatement(problem: Problem): string {
  const parts: string[] = [];

  parts.push(problem.title);
  parts.push('');
  parts.push(problem.statement);

  if (problem.constraints) {
    parts.push('');
    parts.push('Constraints:');
    parts.push(problem.constraints);
  }

  if (problem.input_format) {
    parts.push('');
    parts.push('Input Format:');
    parts.push(problem.input_format);
  }

  if (problem.output_format) {
    parts.push('');
    parts.push('Output Format:');
    parts.push(problem.output_format);
  }

  if (problem.sample_io && problem.sample_io.length > 0) {
    parts.push('');
    problem.sample_io.forEach((sample, idx) => {
      parts.push(`Sample Input ${idx + 1}:`);
      parts.push(sample.input);
      parts.push(`Sample Output ${idx + 1}:`);
      parts.push(sample.output);
      parts.push('');
    });
  }

  return parts.join('\n');
}

export const ProblemsBrowser: React.FC = () => {
  const router = useRouter();
  const { createSession } = useStore();

  const [problems, setProblems] = useState<Problem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');
  const [activeDifficulty, setActiveDifficulty] = useState<string | null>(null);
  const [startingSessionId, setStartingSessionId] = useState<string | null>(null);

  const fetchProblems = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (activeCategory !== 'All') params.set('category', activeCategory);
      if (activeDifficulty) params.set('difficulty', activeDifficulty);
      params.set('limit', '50');

      const queryStr = params.toString();
      const data = await api.get<Problem[]>(`/problems/${queryStr ? `?${queryStr}` : ''}`);
      setProblems(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load problems');
    } finally {
      setLoading(false);
    }
  }, [activeCategory, activeDifficulty]);

  useEffect(() => {
    fetchProblems();
  }, [fetchProblems]);

  const handleStartSession = async (problem: Problem) => {
    setStartingSessionId(problem.id);
    try {
      const statement = buildProblemStatement(problem);
      const session = await createSession(statement, 'learning');
      router.push(`/session/${session.id}`);
    } catch (err: any) {
      console.error('Failed to start session:', err);
      setStartingSessionId(null);
    }
  };

  // Client-side search filter
  const filteredProblems = problems.filter((p) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      p.title.toLowerCase().includes(q) ||
      p.categories.some((c) => c.toLowerCase().includes(q)) ||
      p.tags.some((t) => t.toLowerCase().includes(q)) ||
      (p.source && p.source.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
          <Library className="w-4 h-4 text-brand-400" />
          Problem Bank
        </h2>
        <span className="text-[10px] text-dark-500 font-mono uppercase tracking-wider">
          {filteredProblems.length} problem{filteredProblems.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Filters Bar */}
      <div className="glass rounded-xl p-4 space-y-3">
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-dark-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search problems by title, category, or tag..."
            className="w-full bg-dark-900 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-dark-500 outline-none focus:border-brand-500 transition-colors"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Category Pills */}
          <Filter className="w-3 h-3 text-dark-500 flex-shrink-0" />
          {CATEGORY_FILTERS.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-2.5 py-1 rounded-md text-[10px] font-semibold font-mono uppercase tracking-wider transition-all ${
                activeCategory === cat
                  ? 'bg-brand-500/20 text-brand-300 border border-brand-500/30'
                  : 'bg-dark-900 text-dark-400 border border-white/5 hover:border-white/15 hover:text-dark-300'
              }`}
            >
              {cat}
            </button>
          ))}

          {/* Difficulty Pills */}
          <span className="w-px h-4 bg-white/10 mx-1" />
          {['Easy', 'Medium', 'Hard'].map((diff) => (
            <button
              key={diff}
              onClick={() => setActiveDifficulty(activeDifficulty === diff ? null : diff)}
              className={`px-2.5 py-1 rounded-md text-[10px] font-semibold font-mono uppercase tracking-wider border transition-all ${
                activeDifficulty === diff
                  ? getDifficultyStyle(diff)
                  : 'bg-dark-900 text-dark-400 border-white/5 hover:border-white/15 hover:text-dark-300'
              }`}
            >
              {diff}
            </button>
          ))}
        </div>
      </div>

      {/* Problems Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-dark-500">
          <Loader2 className="w-5 h-5 animate-spin mr-2" />
          <span className="text-xs font-mono">Loading problems...</span>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-16 text-dark-500 space-y-2">
          <AlertTriangle className="w-6 h-6 text-amber-500/60" />
          <p className="text-xs text-dark-400">{error}</p>
          <button
            onClick={fetchProblems}
            className="text-[10px] text-brand-400 hover:text-brand-300 font-semibold uppercase tracking-wider transition-colors"
          >
            Try Again
          </button>
        </div>
      ) : filteredProblems.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-dark-500 space-y-1">
          <Library className="w-6 h-6 text-dark-600 mb-1" />
          <p className="text-xs font-semibold text-dark-400">No problems found</p>
          <p className="text-[10px] text-dark-500 max-w-[240px] text-center">
            {searchQuery || activeCategory !== 'All' || activeDifficulty
              ? 'Try adjusting your search or filters.'
              : 'The problem bank is empty. Problems will appear here once added.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredProblems.map((problem) => (
            <div
              key={problem.id}
              className="glass rounded-xl p-5 space-y-3 border border-white/5 hover:border-brand-500/20 hover:bg-brand-500/[0.02] transition-all group"
            >
              {/* Title Row */}
              <div className="flex items-start justify-between gap-2">
                <h4 className="text-sm font-bold text-white tracking-tight leading-snug line-clamp-2 group-hover:text-brand-200 transition-colors">
                  {problem.title}
                </h4>
                {problem.source_url && (
                  <a
                    href={problem.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-dark-500 hover:text-brand-400 transition-colors flex-shrink-0 mt-0.5"
                    title="Open original problem"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>

              {/* Difficulty Badge + Rating */}
              <div className="flex items-center gap-2">
                {problem.difficulty && (
                  <span
                    className={`px-2 py-0.5 rounded text-[9px] font-semibold tracking-wider font-mono uppercase border ${getDifficultyStyle(
                      problem.difficulty
                    )}`}
                  >
                    {problem.difficulty}
                  </span>
                )}
                {problem.estimated_rating != null && (
                  <span className="flex items-center gap-1 text-[10px] text-dark-400 font-mono">
                    <Signal className="w-3 h-3 text-dark-500" />
                    {problem.estimated_rating}
                  </span>
                )}
                {problem.source && (
                  <span className="text-[10px] text-dark-500 font-mono ml-auto">
                    {problem.source}
                    {problem.source_id ? ` #${problem.source_id}` : ''}
                  </span>
                )}
              </div>

              {/* Category Tags */}
              {problem.categories.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {problem.categories.map((cat) => (
                    <span
                      key={cat}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-brand-500/8 text-brand-400/80 text-[9px] font-mono font-medium uppercase tracking-wider border border-brand-500/10"
                    >
                      <Tag className="w-2.5 h-2.5" />
                      {cat}
                    </span>
                  ))}
                </div>
              )}

              {/* Start Session Button */}
              <button
                onClick={() => handleStartSession(problem)}
                disabled={startingSessionId === problem.id}
                className="w-full mt-1 bg-dark-900 hover:bg-brand-600 text-dark-300 hover:text-white border border-white/10 hover:border-brand-500 font-semibold py-2 rounded-lg transition-all text-xs flex items-center justify-center gap-1.5 active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100 group-hover:border-brand-500/30"
              >
                {startingSessionId === problem.id ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Starting Session...
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    Start Session
                  </>
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
