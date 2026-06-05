import { useState } from 'react';
import { motion } from 'framer-motion';
import { useQueryStore } from '@/store/queryStore';
import apiClient from '@/api/client';
import {
  Brain,
  Send,
  Clock,
  Loader2,
  AlertTriangle,
  Database,
  Zap,
  Hash,
  ChevronDown,
  ChevronUp,
  Sparkles,
  History,
  Trash2,
} from 'lucide-react';

const EXAMPLE_QUERIES = [
  'Show all transactions above $1000',
  'Find users who signed up in the last 7 days',
  'What is the average transaction amount by type?',
  'List the top 10 customers by total spending',
  'Show failed transactions from yesterday',
  'Count transactions grouped by status',
];

export function QueryConsolePage() {
  const {
    currentQuery,
    lastResult,
    isLoading,
    error,
    history,
    setQuery,
    setResult,
    setLoading,
    setError,
    addToHistory,
    clearHistory,
  } = useQueryStore();

  const [collection, setCollection] = useState('transactions');
  const [showQuery, setShowQuery] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const handleSubmit = async () => {
    if (!currentQuery.trim() || isLoading) return;
    setLoading(true);
    try {
      const { data } = await apiClient.post('/ai/query', {
        query: currentQuery,
        collection,
      });
      setResult(data);
      addToHistory(currentQuery, data.count);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Query failed');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            AI Query Console
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Ask anything about your data in natural language
          </p>
        </div>
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
        >
          <History className="h-4 w-4" />
          History ({history.length})
        </button>
      </div>

      {/* Example chips */}
      <div className="flex flex-wrap gap-2">
        {EXAMPLE_QUERIES.map((q) => (
          <button
            key={q}
            onClick={() => setQuery(q)}
            className="rounded-full border border-border bg-card/60 px-3 py-1.5 text-xs text-muted-foreground transition-all hover:border-primary/50 hover:text-primary hover:bg-primary/5"
          >
            <Sparkles className="mr-1 inline h-3 w-3" />
            {q}
          </button>
        ))}
      </div>

      {/* Query input */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <label className="text-sm font-medium text-foreground">Collection:</label>
          <select
            value={collection}
            onChange={(e) => setCollection(e.target.value)}
            className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:outline-none"
          >
            <option value="transactions">transactions</option>
            <option value="users">users</option>
            <option value="orders">orders</option>
            <option value="products">products</option>
          </select>
        </div>

        <div className="relative">
          <textarea
            value={currentQuery}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            placeholder="Ask a question about your data... (e.g., 'Show all transactions above $500')"
            rows={3}
            className="w-full resize-none rounded-xl border border-border bg-background p-4 pr-14 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <button
            onClick={handleSubmit}
            disabled={!currentQuery.trim() || isLoading}
            className="absolute bottom-3 right-3 flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-all hover:bg-primary/90 disabled:opacity-50 glow-primary"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 rounded-xl border border-destructive/30 bg-destructive/5 px-5 py-4 text-sm text-destructive"
        >
          <AlertTriangle className="h-5 w-5 shrink-0" />
          {error}
        </motion.div>
      )}

      {/* Results */}
      {lastResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Metrics bar */}
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2 rounded-lg bg-card border border-border px-4 py-2.5">
              <Hash className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-foreground">{lastResult.count} results</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-card border border-border px-4 py-2.5">
              <Zap className="h-4 w-4 text-chart-2" />
              <span className="text-sm font-medium text-foreground">{lastResult.execution_time_ms}ms</span>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-card border border-border px-4 py-2.5">
              <Database className="h-4 w-4 text-chart-3" />
              <span className="text-sm font-medium text-foreground capitalize">{String(lastResult.iqr?.operation ?? '')}</span>
            </div>
            <div className={`flex items-center gap-2 rounded-lg border px-4 py-2.5 ${
              lastResult.risk_level === 'high'
                ? 'border-destructive/30 bg-destructive/5 text-destructive'
                : lastResult.risk_level === 'medium'
                ? 'border-chart-4/30 bg-chart-4/5 text-chart-4'
                : 'border-chart-2/30 bg-chart-2/5 text-chart-2'
            }`}>
              <AlertTriangle className="h-4 w-4" />
              <span className="text-sm font-medium capitalize">{lastResult.risk_level} risk</span>
            </div>

            <button
              onClick={() => setShowQuery(!showQuery)}
              className="ml-auto flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            >
              {showQuery ? 'Hide' : 'Show'} Query
              {showQuery ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>
          </div>

          {/* Generated query */}
          {showQuery && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="rounded-xl border border-border bg-card p-4"
            >
              <h3 className="mb-2 text-xs font-semibold uppercase text-muted-foreground">Generated Query</h3>
              <pre className="overflow-x-auto rounded-lg bg-background p-3 text-xs text-foreground">
                {JSON.stringify(lastResult.generated_query, null, 2)}
              </pre>
            </motion.div>
          )}

          {/* Results table */}
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="overflow-x-auto">
              {lastResult.results.length > 0 ? (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border bg-muted/30">
                      {Object.keys(lastResult.results[0]).map((key) => (
                        <th
                          key={key}
                          className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground"
                        >
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {lastResult.results.map((row, i) => (
                      <tr
                        key={i}
                        className="border-b border-border/50 transition-colors hover:bg-muted/10"
                      >
                        {Object.values(row).map((val: unknown, j: number) => (
                          <td key={j} className="whitespace-nowrap px-4 py-3 text-foreground">
                            {typeof val === 'object' ? JSON.stringify(val) : String(val ?? '')}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="p-12 text-center text-muted-foreground">
                  No results found for this query.
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* History sidebar */}
      {showHistory && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass rounded-2xl p-5"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-foreground">Query History</h3>
            <button
              onClick={clearHistory}
              className="text-xs text-muted-foreground hover:text-destructive transition-colors"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          </div>
          {history.length === 0 ? (
            <p className="text-xs text-muted-foreground">No queries yet</p>
          ) : (
            <div className="space-y-2">
              {history.map((h, i) => (
                <button
                  key={i}
                  onClick={() => setQuery(h.query)}
                  className="w-full text-left rounded-lg border border-border/50 bg-background/50 p-3 text-xs transition-colors hover:border-primary/30"
                >
                  <div className="truncate text-foreground">{h.query}</div>
                  <div className="mt-1 flex items-center gap-2 text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {new Date(h.timestamp).toLocaleTimeString()}
                    <span>• {h.resultCount} results</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
