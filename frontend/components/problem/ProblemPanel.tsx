import React from 'react';
import { MessageContent } from '../chat/MessageContent';
import { ProblemAnalysis } from '@/lib/store';
import { Clock, ShieldAlert, Award, Hash } from 'lucide-react';

interface ProblemPanelProps {
  problemStatement: string;
  analysis?: ProblemAnalysis | null;
}

export const ProblemPanel: React.FC<ProblemPanelProps> = ({ problemStatement, analysis }) => {
  return (
    <div className="glass rounded-xl p-5 overflow-y-auto h-full flex flex-col space-y-5 scrollbar-thin">
      {/* Title & Metadata Banner */}
      <div className="border-b border-white/10 pb-4 space-y-2">
        <h2 className="text-lg font-bold text-white tracking-tight">
          {analysis?.title || 'Competitive Programming Problem'}
        </h2>
        
        {analysis && (
          <div className="flex flex-wrap gap-2 items-center">
            {/* Rating badge */}
            <span className="flex items-center gap-1 text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300">
              <Award className="w-3 h-3" />
              Rating: {analysis.estimated_rating || 'Unrated'}
            </span>

            {/* Difficulty badge */}
            <span className="flex items-center gap-1 text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-300">
              {analysis.difficulty || 'Medium'}
            </span>

            {/* Categories */}
            {analysis.categories?.map((cat, idx) => (
              <span key={idx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 border border-white/10 text-dark-300">
                {cat}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Constraints info box */}
      {analysis?.constraints && (
        <div className="bg-dark-900/40 border border-white/5 rounded-xl p-3.5 space-y-2">
          <h4 className="text-[10px] uppercase font-mono tracking-widest text-dark-400 font-semibold flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-brand-400" />
            Execution Constraints
          </h4>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <span className="text-dark-500 block font-mono text-[9px] uppercase">Time Limit</span>
              <span className="text-white font-medium">{analysis.constraints.time_limit || '2.0s'}</span>
            </div>
            <div>
              <span className="text-dark-500 block font-mono text-[9px] uppercase">Memory Limit</span>
              <span className="text-white font-medium">{analysis.constraints.memory_limit || '256MB'}</span>
            </div>
            {analysis.constraints.N && (
              <div className="col-span-2">
                <span className="text-dark-500 block font-mono text-[9px] uppercase">Input Range (N)</span>
                <span className="text-white font-mono font-medium">{analysis.constraints.N}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Problem Statement text body */}
      <div className="flex-1 space-y-4">
        <h4 className="text-[10px] uppercase font-mono tracking-widest text-dark-400 font-semibold flex items-center gap-1.5">
          <Hash className="w-3.5 h-3.5 text-brand-400" />
          Problem Statement
        </h4>
        <div className="text-dark-200">
          <MessageContent content={problemStatement} />
        </div>
      </div>

      {/* Key Observations Tips (if visible in teach mode) */}
      {analysis?.key_observations && analysis.key_observations.length > 0 && (
        <div className="border-t border-white/5 pt-4">
          <h4 className="text-[10px] uppercase font-mono tracking-widest text-dark-400 font-semibold mb-2">
            Discovered Insights
          </h4>
          <ul className="space-y-1.5">
            {analysis.key_observations.map((obs, idx) => (
              <li key={idx} className="flex gap-2 text-xs text-dark-300 items-start">
                <span className="text-brand-400 font-mono">[{idx + 1}]</span>
                <span className="leading-relaxed">{obs}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
