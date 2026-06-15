import React from 'react';
import Editor from '@monaco-editor/react';
import { Play, Settings } from 'lucide-react';

interface CodeEditorProps {
  code: string;
  language: string;
  onChangeCode: (code: string) => void;
  onChangeLanguage: (lang: string) => void;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  language,
  onChangeCode,
  onChangeLanguage,
}) => {
  // Map standard friendly language names to monaco identifiers
  const getMonacoLanguage = (lang: string) => {
    switch (lang) {
      case 'C++':
        return 'cpp';
      case 'Python':
        return 'python';
      case 'Java':
        return 'java';
      case 'Go':
        return 'go';
      default:
        return 'cpp';
    }
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      onChangeCode(value);
    }
  };

  return (
    <div className="glass rounded-xl overflow-hidden h-full flex flex-col">
      {/* Editor Header / Toolbars */}
      <div className="bg-dark-950 px-4 py-2 border-b border-white/10 flex justify-between items-center text-xs">
        <div className="flex items-center gap-3">
          <span className="text-dark-400 font-mono flex items-center gap-1.5">
            <Settings className="w-3.5 h-3.5" />
            Environment
          </span>
          <select
            value={language}
            onChange={(e) => onChangeLanguage(e.target.value)}
            className="bg-dark-900 border border-white/10 text-white rounded px-2 py-1 outline-none font-semibold cursor-pointer"
          >
            <option value="C++">C++ (GCC)</option>
            <option value="Python">Python (3.12)</option>
            <option value="Java">Java (JDK 21)</option>
            <option value="Go">Go (1.22)</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] text-dark-500 font-mono uppercase">
            Auto-save enabled
          </span>
        </div>
      </div>

      {/* Editor Body */}
      <div className="flex-1 bg-[#1e1e1e]">
        <Editor
          height="100%"
          language={getMonacoLanguage(language)}
          value={code}
          onChange={handleEditorChange}
          theme="vs-dark"
          options={{
            fontSize: 13,
            fontFamily: 'JetBrains Mono, Menlo, Monaco, Courier New, monospace',
            minimap: { enabled: false },
            lineNumbers: 'on',
            scrollbar: {
              vertical: 'visible',
              horizontal: 'visible',
              verticalScrollbarSize: 8,
              horizontalScrollbarSize: 8,
            },
            automaticLayout: true,
            padding: { top: 10, bottom: 10 },
            roundedSelection: true,
            cursorBlinking: 'smooth',
            smoothScrolling: true,
            renderLineHighlight: 'all',
          }}
        />
      </div>
    </div>
  );
};
