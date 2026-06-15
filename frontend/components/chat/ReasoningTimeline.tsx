import React from 'react';
import { Lightbulb, CheckCircle, AlertTriangle, Eye, Target, Compass } from 'lucide-react';
import { ReasoningFrame } from '@/lib/store';

interface ReasoningTimelineProps {
  frame: ReasoningFrame | null;
  activeAgent: string;
}

export const ReasoningTimeline: React.FC<ReasoningTimelineProps> = ({ frame, activeAgent }) => {
  if (!frame) {
    return (
      <div className="glass rounded-xl p-6 h-full flex flex-col justify-center items-center text-center text-dark-400">
        <Compass className="w-8 h-8 mb-2 animate-spin text-brand-500" style={{ animationDuration: '6s' }} />
        <p className="text-sm font-medium">Coach is listening...</p>
        <p className="text-xs max-w-xs mt-1 text-dark-500">
          The Socratic reasoning timeline will populate once the conversation progresses.
        </p>
      </div>
    );
  }

  const {
    current_understanding,
    key_observation,
    why_it_matters,
    possible_approaches = [],
    rejected_approaches = [],
    guiding_question,
    next_learning_objective
  } = frame;

  return (
    <div className="glass rounded-xl p-5 overflow-y-auto h-full space-y-5 flex flex-col scrollbar-thin">
      <div className="flex justify-between items-center border-b border-white/10 pb-3">
        <h3 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
          <Compass className="w-4 h-4 text-brand-400" />
          Educational Reasoning
        </h3>
        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-brand-500/10 border border-brand-500/20 text-brand-300">
          Active Node: {activeAgent}
        </span>
      </div>

      <div className="space-y-4 flex-1">
        {/* Current Understanding */}
        {current_understanding && (
          <div className="space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-400 flex items-center gap-1.5">
              <Eye className="w-3.5 h-3.5 text-blue-400" />
              Current Understanding
            </span>
            <p className="text-xs text-dark-200 pl-5 leading-relaxed">{current_understanding}</p>
          </div>
        )}

        {/* Key Observation */}
        {key_observation && (
          <div className="space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-400 flex items-center gap-1.5">
              <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
              Key Observation
            </span>
            <p className="text-xs text-dark-200 pl-5 leading-relaxed font-medium text-amber-200/90">{key_observation}</p>
            {why_it_matters && (
              <p className="text-[11px] text-dark-400 pl-5 leading-relaxed italic">Why it matters: {why_it_matters}</p>
            )}
          </div>
        )}

        {/* Possible Approaches */}
        {possible_approaches.length > 0 && (
          <div className="space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-400 flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              Possible Approaches
            </span>
            <ul className="list-disc pl-9 text-xs text-dark-300 space-y-1 leading-relaxed">
              {possible_approaches.map((app, idx) => (
                <li key={idx}>{app}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Rejected Approaches */}
        {rejected_approaches.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-400 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              Rejected / Naive Approaches
            </span>
            <div className="pl-5 space-y-2">
              {rejected_approaches.map((rej, idx) => (
                <div key={idx} className="bg-rose-500/5 border border-rose-500/10 rounded px-2.5 py-1.5">
                  <p className="text-xs font-medium text-rose-300">{rej.approach}</p>
                  <p className="text-[10px] text-dark-400 mt-0.5 leading-relaxed">{rej.reason}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Learning Objective */}
        {next_learning_objective && (
          <div className="space-y-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-400 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-brand-400" />
              Next Learning Objective
            </span>
            <p className="text-xs text-dark-200 pl-5 leading-relaxed">{next_learning_objective}</p>
          </div>
        )}
      </div>

      {/* Guiding Question */}
      {guiding_question && (
        <div className="border-t border-white/5 pt-3 mt-auto bg-brand-500/5 rounded-lg border border-brand-500/10 p-3">
          <p className="text-[10px] uppercase font-mono tracking-widest text-brand-400 font-semibold mb-1">
            Guiding Question
          </p>
          <p className="text-xs text-white leading-relaxed font-medium italic">
            "{guiding_question}"
          </p>
        </div>
      )}
    </div>
  );
};
