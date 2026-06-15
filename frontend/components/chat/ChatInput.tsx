import React, { useState, useRef, useEffect } from 'react';
import { Send, Code2, Terminal } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string, code?: string, language?: string) => Promise<void>;
  onReviewCode: (code: string, language: string) => Promise<void>;
  isLoading: boolean;
  activeLanguage?: string;
  activeCode?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onReviewCode,
  isLoading,
  activeLanguage = 'C++',
  activeCode = '',
}) => {
  const [message, setMessage] = useState('');
  const [includeCode, setIncludeCode] = useState(false);
  const [lang, setLang] = useState(activeLanguage);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Sync active language/code changes from parent panels
  useEffect(() => {
    setLang(activeLanguage);
  }, [activeLanguage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() && !includeCode) return;

    const codeToSend = includeCode ? activeCode : undefined;
    const langToSend = includeCode ? lang : undefined;

    setMessage('');
    setIncludeCode(false);
    
    await onSendMessage(message, codeToSend, langToSend);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleReviewCodeClick = async () => {
    if (!activeCode.trim()) return;
    await onReviewCode(activeCode, lang);
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-white/10 bg-dark-950 p-4 space-y-3">
      {/* Code Inclusion Banner / Actions */}
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIncludeCode(!includeCode)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-colors ${
              includeCode 
                ? 'bg-brand-500/10 border border-brand-500/30 text-brand-300' 
                : 'bg-white/5 border border-white/10 text-dark-300 hover:bg-white/10'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            {includeCode ? 'Attaching Editor Code' : 'Attach Editor Code'}
          </button>

          {includeCode && (
            <select
              value={lang}
              onChange={(e) => setLang(e.target.value)}
              className="bg-dark-900 border border-white/10 text-dark-200 rounded px-1.5 py-1 text-xs outline-none"
            >
              <option value="C++">C++</option>
              <option value="Python">Python</option>
              <option value="Java">Java</option>
              <option value="Go">Go</option>
            </select>
          )}
        </div>

        {activeCode.trim() && (
          <button
            type="button"
            onClick={handleReviewCodeClick}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 hover:bg-rose-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Terminal className="w-3.5 h-3.5" />
            Submit Code for Review
          </button>
        )}
      </div>

      {/* Main Text Input Area */}
      <div className="flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={includeCode ? "Add instructions or ask a question about your code..." : "Ask your Socratic coach a question or explain your approach..."}
          rows={1}
          disabled={isLoading}
          className="flex-1 min-h-[40px] max-h-[160px] bg-dark-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-dark-500 outline-none focus:border-brand-500 transition-colors resize-none scrollbar-none disabled:opacity-50"
          style={{ height: 'auto' }}
        />
        <button
          type="submit"
          disabled={isLoading || (!message.trim() && !includeCode)}
          className="h-[40px] w-[40px] rounded-xl bg-brand-600 text-white flex items-center justify-center hover:bg-brand-500 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </form>
  );
};
