import React from 'react';
import { MessageContent } from './MessageContent';
import { Message } from '@/lib/store';
import { User, ShieldAlert, Cpu } from 'lucide-react';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  
  // Custom display name and colors for agents
  const getAgentInfo = (name?: string) => {
    switch (name) {
      case 'ProblemAnalyzer':
        return { label: 'Problem Analyzer', color: 'bg-blue-500/10 border-blue-500/20 text-blue-400' };
      case 'TeachingAgent':
        return { label: 'ICPC Socratic Coach', color: 'bg-brand-500/10 border-brand-500/20 text-brand-300' };
      case 'AlgorithmExpert':
        return { label: 'Algorithm Expert', color: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' };
      case 'ComplexityAnalyzer':
        return { label: 'Complexity Expert', color: 'bg-purple-500/10 border-purple-500/20 text-purple-400' };
      case 'TestCaseGenerator':
        return { label: 'Test Case Generator', color: 'bg-amber-500/10 border-amber-500/20 text-amber-400' };
      case 'CodeReview':
        return { label: 'Code Reviewer', color: 'bg-rose-500/10 border-rose-500/20 text-rose-400' };
      case 'LearningMemory':
        return { label: 'Memory update', color: 'bg-slate-500/10 border-slate-500/20 text-slate-400' };
      default:
        return { label: 'Coach', color: 'bg-brand-500/10 border-brand-500/20 text-brand-300' };
    }
  };

  if (isSystem) {
    return (
      <div className="flex items-center gap-2 justify-center py-2 px-4 rounded-lg bg-red-950/20 border border-red-900/30 text-xs text-red-400 max-w-xl mx-auto my-2">
        <ShieldAlert className="w-4 h-4 flex-shrink-0" />
        <span className="font-mono">{message.content}</span>
      </div>
    );
  }

  const agent = !isUser ? getAgentInfo(message.agent_name) : null;

  return (
    <div className={`flex w-full gap-3 py-4 border-b border-white/5 animate-fade-in ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-lg bg-brand-600/10 border border-brand-500/20 flex items-center justify-center flex-shrink-0">
          <Cpu className="w-4 h-4 text-brand-400" />
        </div>
      )}

      <div className={`space-y-1.5 max-w-[85%] ${isUser ? 'text-right' : 'text-left'}`}>
        <div className="flex items-center gap-2 text-xs">
          {!isUser && agent && (
            <span className={`px-2 py-0.5 rounded border text-[10px] font-semibold tracking-wide font-mono ${agent.color}`}>
              {agent.label}
            </span>
          )}
          {isUser && (
            <span className="text-dark-400 font-medium font-mono text-[10px]">STUDENT</span>
          )}
          <span className="text-dark-500 text-[9px] font-mono">
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <div className={`rounded-xl p-4 text-sm leading-relaxed ${
          isUser 
            ? 'bg-brand-600/10 border border-brand-500/20 text-white rounded-tr-none' 
            : 'bg-dark-900/40 border border-white/5 text-dark-100 rounded-tl-none'
        }`}>
          <MessageContent content={message.content} />
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-dark-300" />
        </div>
      )}
    </div>
  );
};
