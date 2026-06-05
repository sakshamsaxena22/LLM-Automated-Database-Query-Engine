import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import apiClient from '@/api/client';
import { Database, Plus, Pencil, Trash2, Search, Loader2 } from 'lucide-react';

export function DataManagerPage() {
  const [collection, setCollection] = useState('transactions');
  const [documents, setDocuments] = useState<Record<string, unknown>[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const { data } = await apiClient.get(`/crud/${collection}`, {
        params: { skip: page * 20, limit: 20 },
      });
      setDocuments(data.documents || []);
      setTotal(data.total || 0);
    } catch {
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [collection, page]);

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this document?')) return;
    try {
      await apiClient.delete(`/crud/${collection}/${id}`);
      fetchDocs();
    } catch {}
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Database className="h-6 w-6 text-primary" />
            Data Manager
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">Browse and manage your collections</p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-3">
        <select
          value={collection}
          onChange={(e) => { setCollection(e.target.value); setPage(0); }}
          className="rounded-lg border border-border bg-card px-4 py-2 text-sm text-foreground focus:border-primary focus:outline-none"
        >
          {['transactions', 'users', 'orders', 'products', 'query_history'].map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter documents…"
            className="w-full rounded-lg border border-border bg-card py-2 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
          />
        </div>

        <span className="text-sm text-muted-foreground">{total} documents</span>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        ) : documents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {Object.keys(documents[0]).slice(0, 8).map((key) => (
                    <th key={key} className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">{key}</th>
                  ))}
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc, i) => (
                  <tr key={i} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    {Object.values(doc).slice(0, 8).map((val, j) => (
                      <td key={j} className="max-w-[200px] truncate whitespace-nowrap px-4 py-3 text-foreground">
                        {typeof val === 'object' ? JSON.stringify(val) : String(val ?? '')}
                      </td>
                    ))}
                    <td className="whitespace-nowrap px-4 py-3 text-right">
                      <button
                        onClick={() => handleDelete(String(doc._id || ''))}
                        className="rounded p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-muted-foreground">No documents in this collection</div>
        )}
      </div>

      {/* Pagination */}
      {total > 20 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent disabled:opacity-50"
          >
            Previous
          </button>
          <span className="text-sm text-muted-foreground">
            Page {page + 1} of {Math.ceil(total / 20)}
          </span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={(page + 1) * 20 >= total}
            className="rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
