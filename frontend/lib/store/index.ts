/* Zustand global store for authentication, sessions, and chat state. */


import { create } from 'zustand';
import { api } from '@/lib/api';

export interface User {
  id: string;
  email: string;
  username: string;
  display_name?: string;
  current_rating: number;
  total_problems_attempted?: number;
  total_problems_solved?: number;
  total_hints_used?: number;
  topic_proficiency?: Record<string, any>;
  weak_topics?: string[];
  strong_topics?: string[];
  common_mistakes?: any[];
}

export interface ReasoningFrame {
  current_understanding?: string;
  key_observation?: string;
  why_it_matters?: string;
  possible_approaches?: string[];
  rejected_approaches?: { approach: string; reason: string }[];
  guiding_question?: string;
  next_learning_objective?: string;
}

export interface ProblemAnalysis {
  title: string;
  summary: string;
  categories: string[];
  difficulty: string;
  estimated_rating: number;
  constraints: Record<string, any>;
  key_observations: string[];
  hidden_observations: string[];
  expected_complexity: string;
  brute_force_complexity: string;
  similar_problems: string[];
}

export interface CoachingSession {
  id: string;
  user_id: string;
  problem_id?: string;
  problem_statement: string;
  status: string;
  session_mode: string;
  hint_level: number;
  max_hint_used: number;
  problem_analysis?: ProblemAnalysis;
  timer_start?: string;
  timer_duration_minutes?: number;
  started_at: string;
  completed_at?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  agent_name?: string;
  message_metadata?: {
    reasoning_frame?: ReasoningFrame;
    [key: string]: any;
  };
  created_at: string;
}

interface AppState {
  // Auth state
  user: User | null;
  token: string | null;
  authLoading: boolean;
  authError: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, displayName?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;

  // Sessions state
  sessions: CoachingSession[];
  activeSession: CoachingSession | null;
  messages: Message[];
  activeAgent: string;
  reasoningFrame: ReasoningFrame | null;
  loadingSessions: boolean;
  activeSessionLoading: boolean;
  streamingMessageContent: string;
  
  createSession: (problemStatement: string, mode?: 'learning' | 'contest', duration?: number) => Promise<CoachingSession>;
  loadSessions: () => Promise<void>;
  loadSession: (id: string) => Promise<void>;
  sendMessageStream: (messageText: string, code?: string, language?: string) => Promise<void>;
  submitCodeForReview: (codeText: string, language?: string) => Promise<void>;
  updateHintLevel: (hintLevel: number) => Promise<void>;
}

export const useStore = create<AppState>((set, get) => ({
  // Auth state
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  authLoading: false,
  authError: null,

  login: async (email, password) => {
    set({ authLoading: true, authError: null });
    try {
      const { access_token } = await api.post<{ access_token: string }>('/auth/login', { email, password });
      localStorage.setItem('token', access_token);
      set({ token: access_token });
      await get().checkAuth();
    } catch (err: any) {
      set({ authError: err.message || 'Login failed', authLoading: false });
      throw err;
    }
  },

  register: async (email, username, password, displayName) => {
    set({ authLoading: true, authError: null });
    try {
      const { access_token } = await api.post<{ access_token: string }>('/auth/register', {
        email,
        username,
        password,
        display_name: displayName,
      });
      localStorage.setItem('token', access_token);
      set({ token: access_token });
      await get().checkAuth();
    } catch (err: any) {
      set({ authError: err.message || 'Registration failed', authLoading: false });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, sessions: [], activeSession: null, messages: [] });
  },

  checkAuth: async () => {
    const { token } = get();
    if (!token) {
      set({ user: null, authLoading: false });
      return;
    }
    set({ authLoading: true });
    try {
      const user = await api.get<User>('/profile/');
      set({ user, authLoading: false });
    } catch (err) {
      localStorage.removeItem('token');
      set({ user: null, token: null, authLoading: false });
    }
  },

  // Sessions state
  sessions: [],
  activeSession: null,
  messages: [],
  activeAgent: 'supervisor',
  reasoningFrame: null,
  loadingSessions: false,
  activeSessionLoading: false,
  streamingMessageContent: '',

  createSession: async (problemStatement, mode = 'learning', duration) => {
    set({ activeSessionLoading: true });
    try {
      const session = await api.post<CoachingSession>('/sessions/', {
        problem_statement: problemStatement,
        session_mode: mode,
        timer_duration_minutes: duration || null,
      });
      set(state => ({
        sessions: [session, ...state.sessions],
        activeSession: session,
        messages: [],
        reasoningFrame: null,
        activeSessionLoading: false,
      }));
      // Auto load details to fetch the generated problem analysis
      await get().loadSession(session.id);
      return session;
    } catch (err) {
      set({ activeSessionLoading: false });
      throw err;
    }
  },

  loadSessions: async () => {
    set({ loadingSessions: true });
    try {
      const { sessions } = await api.get<{ sessions: CoachingSession[]; total: number }>('/sessions/?limit=50');
      set({ sessions, loadingSessions: false });
    } catch (err) {
      set({ loadingSessions: false });
    }
  },

  loadSession: async (id) => {
    set({ activeSessionLoading: true, messages: [], reasoningFrame: null });
    try {
      const session = await api.get<CoachingSession>(`/sessions/${id}`);
      const messagesData = await api.get<{ id: string; session_id: string; role: string; content: string; agent_name?: string; message_metadata?: any; created_at: string }[]>(`/sessions/${id}/messages`);
      
      // Map role properly
      const messages = messagesData.map(m => ({
        ...m,
        role: m.role as 'user' | 'assistant' | 'system'
      }));

      // Extract the last reasoning frame from assistant messages
      let lastReasoning: ReasoningFrame | null = null;
      for (let i = messages.length - 1; i >= 0; i--) {
        if (messages[i].role === 'assistant' && messages[i].message_metadata?.reasoning_frame) {
          lastReasoning = messages[i].message_metadata.reasoning_frame;
          break;
        }
      }

      set({
        activeSession: session,
        messages,
        reasoningFrame: lastReasoning,
        activeSessionLoading: false,
      });
    } catch (err) {
      set({ activeSessionLoading: false });
    }
  },

  sendMessageStream: async (messageText, code, language) => {
    const { activeSession, messages } = get();
    if (!activeSession) return;

    // Append user message immediately
    const tempUserMsg: Message = {
      id: Math.random().toString(),
      session_id: activeSession.id,
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString(),
    };

    set({
      messages: [...messages, tempUserMsg],
      streamingMessageContent: '',
    });

    await api.streamChat(
      activeSession.id,
      messageText,
      code,
      language,
      (event) => {
        if (event.type === 'token') {
          set(state => ({
            streamingMessageContent: state.streamingMessageContent + event.content,
            activeAgent: event.agent || state.activeAgent,
          }));
        } else if (event.type === 'agent_start') {
          set({ activeAgent: event.agent });
        } else if (event.type === 'reasoning_frame') {
          set({ reasoningFrame: event.reasoning_frame });
        } else if (event.type === 'agent_end') {
          set({ activeAgent: 'supervisor' });
        }
      },
      () => {
        // Stream finished
        const { streamingMessageContent, activeAgent, reasoningFrame } = get();
        const tempAssistantMsg: Message = {
          id: Math.random().toString(),
          session_id: activeSession.id,
          role: 'assistant',
          content: streamingMessageContent,
          agent_name: activeAgent,
          message_metadata: { reasoning_frame: reasoningFrame || undefined },
          created_at: new Date().toISOString(),
        };
        set(state => ({
          messages: [...state.messages, tempAssistantMsg],
          streamingMessageContent: '',
        }));
        // Reload session data to get updated hint levels or database messages
        get().loadSession(activeSession.id);
      },
      (err) => {
        console.error('Streaming error:', err);
        set(state => ({
          messages: [
            ...state.messages,
            {
              id: Math.random().toString(),
              session_id: activeSession.id,
              role: 'system',
              content: `Error: ${err.message || 'Stream disconnected'}`,
              created_at: new Date().toISOString(),
            },
          ],
          streamingMessageContent: '',
        }));
      }
    );
  },

  submitCodeForReview: async (codeText, language = 'C++') => {
    const { activeSession, messages } = get();
    if (!activeSession) return;

    const tempUserMsg: Message = {
      id: Math.random().toString(),
      session_id: activeSession.id,
      role: 'user',
      content: `Submitting code for review:\n\`\`\`${language.toLowerCase()}\n${codeText}\n\`\`\``,
      created_at: new Date().toISOString(),
    };

    set({
      messages: [...messages, tempUserMsg],
      activeSessionLoading: true,
    });

    try {
      const reviewResponse = await api.post<any>(`/sessions/${activeSession.id}/submit-code`, {
        message: 'Review my code',
        include_code: codeText,
        language: language,
      });

      const tempAssistantMsg: Message = {
        id: Math.random().toString(),
        session_id: activeSession.id,
        role: 'assistant',
        content: reviewResponse.content,
        agent_name: reviewResponse.agent_name || 'CodeReview',
        message_metadata: { reasoning_frame: reviewResponse.reasoning_frame },
        created_at: new Date().toISOString(),
      };

      set(state => ({
        messages: [...state.messages, tempAssistantMsg],
        reasoningFrame: reviewResponse.reasoning_frame || state.reasoningFrame,
        activeSessionLoading: false,
      }));
    } catch (err: any) {
      set(state => ({
        messages: [
          ...state.messages,
          {
            id: Math.random().toString(),
            session_id: activeSession.id,
            role: 'system',
            content: `Code review failed: ${err.message || 'Internal server error'}`,
            created_at: new Date().toISOString(),
          },
        ],
        activeSessionLoading: false,
      }));
    }
  },

  updateHintLevel: async (hintLevel) => {
    const { activeSession } = get();
    if (!activeSession) return;
    try {
      const updated = await api.patch<CoachingSession>(`/sessions/${activeSession.id}`, { hint_level: hintLevel });
      set({ activeSession: updated });
    } catch (err) {
      console.error('Failed to update hint level:', err);
    }
  }
}));
