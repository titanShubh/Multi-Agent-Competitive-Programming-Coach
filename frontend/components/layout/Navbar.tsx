import React from 'react';
import { useStore } from '@/lib/store';
import { LogOut, User, Award, Compass } from 'lucide-react';
import Link from 'next/link';

export const Navbar: React.FC = () => {
  const { user, logout } = useStore();

  return (
    <nav className="glass border-b border-white/10 px-6 py-3.5 flex justify-between items-center z-50 relative">
      <Link href="/dashboard" className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-brand-500/20">
          <Compass className="w-4 h-4 text-white" />
        </div>
        <span className="text-sm font-bold text-white tracking-wider uppercase font-mono">
          ICPC Mentor
        </span>
      </Link>

      {user && (
        <div className="flex items-center gap-4">
          {/* Rating Display */}
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 font-semibold font-mono shadow-sm">
            <Award className="w-3.5 h-3.5" />
            Rating: {user.current_rating}
          </div>

          {/* User profile dropdown trigger */}
          <div className="flex items-center gap-2 border-l border-white/10 pl-4">
            <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-dark-300">
              <User className="w-4 h-4 text-dark-200" />
            </div>
            <div className="hidden sm:block text-left">
              <p className="text-xs font-semibold text-white leading-none">
                {user.display_name || user.username}
              </p>
              <p className="text-[10px] text-dark-500 font-mono mt-0.5 leading-none">
                Student
              </p>
            </div>
          </div>

          <button
            onClick={logout}
            title="Log Out"
            className="p-1.5 rounded-lg border border-white/5 hover:bg-red-500/10 hover:border-red-500/20 text-dark-400 hover:text-red-400 transition-all active:scale-95"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      )}
    </nav>
  );
};
