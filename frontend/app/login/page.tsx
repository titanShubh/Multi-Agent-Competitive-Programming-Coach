'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useStore } from '@/lib/store';
import { Compass, Mail, Lock, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showWakeupNotice, setShowWakeupNotice] = useState(false);
  
  const { login, user, authLoading, authError } = useStore();
  const router = useRouter();

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      router.push('/dashboard');
    }
  }, [user, router]);

  // Sync store errors
  useEffect(() => {
    if (authError) {
      setError(authError);
    }
  }, [authError]);

  // Alert timer for Render cold starts
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (authLoading) {
      timer = setTimeout(() => {
        setShowWakeupNotice(true);
      }, 3000);
    } else {
      setShowWakeupNotice(false);
    }
    return () => clearTimeout(timer);
  }, [authLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }
    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex flex-col justify-center items-center px-4 relative overflow-hidden select-none">
      {/* Background decoration */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-brand-600/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-md w-full glass rounded-2xl p-8 space-y-6 z-10 relative">
        {/* Brand Logo */}
        <div className="flex flex-col items-center space-y-2 text-center">
          <Link href="/" className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Compass className="w-5 h-5 text-white" />
          </Link>
          <h2 className="text-xl font-bold tracking-tight text-white mt-2">Welcome Back</h2>
          <p className="text-xs text-dark-400">Enter your credentials to access your coaching workspace</p>
        </div>

        {/* Error message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-3 text-xs text-red-400 text-center font-medium">
            {error}
          </div>
        )}

        {/* Wakeup warning for Render cold starts */}
        {showWakeupNotice && (
          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 text-xs text-amber-300 text-center font-medium animate-pulse">
            Waking up server on Render free tier (takes ~45 seconds on first load)...
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[10px] uppercase font-semibold font-mono text-dark-400 tracking-wider">
              Email Address
            </label>
            <div className="relative">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                disabled={authLoading}
                className="w-full bg-dark-900 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-dark-500 outline-none focus:border-brand-500 transition-colors disabled:opacity-50"
              />
              <Mail className="w-4 h-4 text-dark-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] uppercase font-semibold font-mono text-dark-400 tracking-wider">
              Password
            </label>
            <div className="relative">
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                disabled={authLoading}
                className="w-full bg-dark-900 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-dark-500 outline-none focus:border-brand-500 transition-colors disabled:opacity-50"
              />
              <Lock className="w-4 h-4 text-dark-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <button
              type="submit"
              disabled={authLoading}
              className="w-full bg-brand-600 hover:bg-brand-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-brand-500/15 flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 disabled:active:scale-100"
            >
              {authLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing In...
                </>
              ) : (
                'Sign In'
              )}
            </button>

            <button
              type="button"
              disabled={authLoading}
              onClick={async () => {
                setEmail('demo@coach.com');
                setPassword('demopass123');
                setError(null);
                try {
                  await login('demo@coach.com', 'demopass123');
                  router.push('/dashboard');
                } catch (err: any) {
                  setError(err.message || 'Demo login failed');
                }
              }}
              className="w-full bg-white/5 border border-white/10 hover:bg-white/10 text-white font-semibold py-2.5 rounded-xl transition-all flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 disabled:active:scale-100"
            >
              Try Guest Demo
            </button>
          </div>
        </form>

        <div className="text-center text-xs text-dark-400 pt-2 border-t border-white/5">
          Don't have an account?{' '}
          <Link href="/register" className="text-brand-400 hover:underline font-semibold">
            Register here
          </Link>
        </div>
      </div>
    </div>
  );
}
