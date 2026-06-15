'use client';

import React, { useState, useEffect, useRef, use } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { Navbar } from '@/components/layout/Navbar';
import { ProblemPanel } from '@/components/problem/ProblemPanel';
import { CodeEditor } from '@/components/editor/CodeEditor';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { ReasoningTimeline } from '@/components/chat/ReasoningTimeline';
import { ChatInput } from '@/components/chat/ChatInput';
import { Loader2, ArrowLeft, Lightbulb, Compass, Code2, Play, CheckCircle } from 'lucide-react';
import Link from 'next/link';

interface SessionPageProps {
  params: Promise<{ id: string }>;
}

export default function SessionPage({ params }: SessionPageProps) {
  const { id } = use(params);
  const router = useRouter();
  
  const {
    user,
    token,
    authLoading,
    activeSession,
    messages,
    activeSessionLoading,
    streamingMessageContent,
    activeAgent,
    reasoningFrame,
    loadSession,
    sendMessageStream,
    submitCodeForReview,
    updateHintLevel,
  } = useStore();

  const [activeTab, setActiveTab] = useState<'editor' | 'timeline'>('editor');
  const [code, setCode] = useState('// Write your solution here\n#include <iostream>\n\nusing namespace std;\n\nint main() {\n    return 0;\n}');
  const [lang, setLang] = useState('C++');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Authenticate user & load session
  useEffect(() => {
    if (!token && !authLoading) {
      router.push('/login');
    }
  }, [token, authLoading, router]);

  useEffect(() => {
    if (token && id) {
      loadSession(id);
    }
  }, [token, id, loadSession]);

  // Scroll to bottom of chat whenever messages or stream content changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingMessageContent]);

  if (authLoading || activeSessionLoading && !activeSession || !user) {
    return (
      <div className="min-h-screen bg-dark-950 flex flex-col justify-center items-center text-dark-400">
        <Loader2 className="w-8 h-8 animate-spin text-brand-500 mb-2" />
        <p className="text-sm font-mono">Loading coaching workspace...</p>
      </div>
    );
  }

  if (!activeSession) {
    return (
      <div className="min-h-screen bg-dark-950 flex flex-col justify-center items-center text-dark-400 p-4">
        <p className="text-sm font-medium mb-4">Coaching session not found.</p>
        <Link href="/dashboard" className="flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-xl text-xs font-bold transition-all">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const handleSendMessage = async (msg: string, attachedCode?: string, attachedLang?: string) => {
    await sendMessageStream(msg, attachedCode, attachedLang);
  };

  const handleReviewCode = async (submittedCode: string, submittedLang: string) => {
    await submitCodeForReview(submittedCode, submittedLang);
  };

  const handleHintIncrement = async () => {
    const currentLvl = activeSession.hint_level;
    if (currentLvl < 5) {
      await updateHintLevel(currentLvl + 1);
    }
  };

  const handleHintDecrement = async () => {
    const currentLvl = activeSession.hint_level;
    if (currentLvl > 0) {
      await updateHintLevel(currentLvl - 1);
    }
  };

  return (
    <div className="h-screen bg-dark-950 flex flex-col overflow-hidden">
      <Navbar />

      {/* Sub-toolbar */}
      <div className="bg-dark-950/80 px-6 py-2.5 border-b border-white/5 flex justify-between items-center z-10">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-xs text-dark-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Dashboard
          </Link>
          <span className="text-dark-600">|</span>
          <span className="text-xs text-brand-300 font-semibold font-mono uppercase">
            Mode: {activeSession.session_mode}
          </span>
        </div>

        {/* Adaptive Hint Progression Controls */}
        {activeSession.session_mode === 'learning' && (
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-dark-400 font-semibold font-mono uppercase mr-1">
              Hint Level: {activeSession.hint_level}/5
            </span>
            <button
              onClick={handleHintDecrement}
              disabled={activeSession.hint_level === 0}
              className="px-2 py-1 bg-white/5 border border-white/10 hover:bg-white/10 text-dark-200 text-xs font-bold rounded-lg disabled:opacity-50 transition-colors"
            >
              -
            </button>
            <button
              onClick={handleHintIncrement}
              disabled={activeSession.hint_level === 5}
              className="px-2.5 py-1 bg-brand-500/10 border border-brand-500/20 hover:bg-brand-500/20 text-brand-300 text-xs font-bold rounded-lg disabled:opacity-50 transition-colors flex items-center gap-1"
            >
              <Lightbulb className="w-3.5 h-3.5" />
              Ask Hint
            </button>
          </div>
        )}
      </div>

      {/* Three Panel Workspace */}
      <div className="flex-1 flex overflow-hidden p-4 gap-4">
        {/* Left Panel: Problem statement description (30%) */}
        <div className="w-[30%] flex flex-col overflow-hidden">
          <ProblemPanel
            problemStatement={activeSession.problem_statement}
            analysis={activeSession.problem_analysis}
          />
        </div>

        {/* Center Panel: Socratic Chat Interface (45%) */}
        <div className="w-[45%] glass rounded-xl flex flex-col overflow-hidden relative">
          {/* Chat Messages Log */}
          <div className="flex-1 overflow-y-auto px-5 py-2 scrollbar-thin space-y-1">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            
            {/* Live SSE Streaming response text placeholder */}
            {streamingMessageContent && (
              <div className="flex w-full gap-3 py-4 border-b border-white/5 justify-start">
                <div className="w-8 h-8 rounded-lg bg-brand-600/10 border border-brand-500/20 flex items-center justify-center flex-shrink-0 glow-active">
                  <Loader2 className="w-4 h-4 text-brand-400 animate-spin" />
                </div>
                <div className="space-y-1.5 max-w-[85%] text-left">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-2 py-0.5 rounded border text-[10px] font-semibold tracking-wide font-mono bg-brand-500/10 border-brand-500/20 text-brand-300">
                      ICPC Coach is typing...
                    </span>
                  </div>
                  <div className="rounded-xl p-4 text-sm leading-relaxed bg-dark-900/40 border border-white/5 text-dark-100 rounded-tl-none italic whitespace-pre-wrap">
                    {streamingMessageContent}
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Active Node Socratic Loading indicator */}
          {activeSessionLoading && !streamingMessageContent && (
            <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-brand-600/10 border border-brand-500/20 text-[10px] text-brand-400 font-semibold font-mono animate-pulse">
              <Loader2 className="w-3 h-3 animate-spin" />
              Node: {activeAgent}
            </div>
          )}

          {/* Message input */}
          <ChatInput
            onSendMessage={handleSendMessage}
            onReviewCode={handleReviewCode}
            isLoading={activeSessionLoading}
            activeLanguage={lang}
            activeCode={code}
          />
        </div>

        {/* Right Panel: Code Workspace & Tabbed Timeline (25%) */}
        <div className="w-[25%] flex flex-col overflow-hidden gap-3">
          {/* Tab Selector */}
          <div className="flex bg-dark-950 p-1 border border-white/10 rounded-xl justify-between items-center text-xs">
            <button
              onClick={() => setActiveTab('editor')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg font-semibold tracking-tight transition-all ${
                activeTab === 'editor' 
                  ? 'bg-brand-600 text-white shadow-sm' 
                  : 'text-dark-400 hover:text-white'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              Editor Workspace
            </button>
            <button
              onClick={() => setActiveTab('timeline')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg font-semibold tracking-tight transition-all ${
                activeTab === 'timeline' 
                  ? 'bg-brand-600 text-white shadow-sm' 
                  : 'text-dark-400 hover:text-white'
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              Reasoning Timeline
            </button>
          </div>

          {/* Tab content panel */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'editor' ? (
              <CodeEditor
                code={code}
                language={lang}
                onChangeCode={setCode}
                onChangeLanguage={setLang}
              />
            ) : (
              <ReasoningTimeline
                frame={reasoningFrame}
                activeAgent={activeAgent}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
