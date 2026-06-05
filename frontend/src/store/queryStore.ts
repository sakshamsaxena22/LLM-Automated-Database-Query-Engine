import { create } from 'zustand';

interface QueryResult {
  generated_query: Record<string, unknown>;
  iqr: Record<string, unknown>;
  count: number;
  results: Record<string, unknown>[];
  execution_time_ms: number | null;
  risk_level: string;
  cached: boolean;
}

interface HistoryEntry {
  query: string;
  timestamp: number;
  resultCount: number;
}

interface QueryState {
  currentQuery: string;
  lastResult: QueryResult | null;
  isLoading: boolean;
  error: string | null;
  history: HistoryEntry[];
  setQuery: (q: string) => void;
  setResult: (r: QueryResult) => void;
  setLoading: (l: boolean) => void;
  setError: (e: string | null) => void;
  addToHistory: (q: string, count: number) => void;
  clearHistory: () => void;
}

export const useQueryStore = create<QueryState>()((set) => ({
  currentQuery: '',
  lastResult: null,
  isLoading: false,
  error: null,
  history: [],

  setQuery: (q) => set({ currentQuery: q }),
  setResult: (r) => set({ lastResult: r, isLoading: false, error: null }),
  setLoading: (l) => set({ isLoading: l, error: null }),
  setError: (e) => set({ error: e, isLoading: false }),

  addToHistory: (query, resultCount) =>
    set((s) => ({
      history: [
        { query, timestamp: Date.now(), resultCount },
        ...s.history.filter((h) => h.query !== query),
      ].slice(0, 20),
    })),

  clearHistory: () => set({ history: [] }),
}));
