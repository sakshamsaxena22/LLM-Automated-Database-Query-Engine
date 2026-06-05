import { useState, useEffect } from 'react';
import apiClient from '@/api/client';
import { Shield, Loader2, Clock, AlertTriangle } from 'lucide-react';

interface AuditEntry {
  _id: string;
  user_id: string;
  operation: string;
  entity: string;
  risk_level: string;
  status: string;
  timestamp: string;
}

export function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);

  useEffect(() => {
    setLoading(true);
    apiClient
      .get('/audit/logs', { params: { skip: page * 50, limit: 50 } })
      .then(({ data }) => {
        setLogs(data.logs || []);
        setTotal(data.total || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  const riskColor = (risk: string) => {
    if (risk === 'high') return 'bg-destructive/10 text-destructive';
    if (risk === 'medium') return 'bg-chart-4/10 text-chart-4';
    return 'bg-chart-2/10 text-chart-2';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Shield className="h-6 w-6 text-primary" />
          Audit Logs
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{total} entries</p>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-6 w-6 animate-spin text-primary" />
          </div>
        ) : logs.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Timestamp</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">User</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Operation</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Entity</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Risk</th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log._id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                  <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">
                    <Clock className="inline h-3 w-3 mr-1" />
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-foreground font-mono text-xs">{log.user_id?.slice(0, 8)}…</td>
                  <td className="px-4 py-3 text-foreground capitalize">{log.operation}</td>
                  <td className="px-4 py-3 text-muted-foreground">{log.entity}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${riskColor(log.risk_level)}`}>
                      {log.risk_level === 'high' && <AlertTriangle className="h-3 w-3" />}
                      {log.risk_level}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-foreground capitalize">{log.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-12 text-center text-muted-foreground">No audit logs</div>
        )}
      </div>

      {total > 50 && (
        <div className="flex items-center justify-center gap-2">
          <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0} className="rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent disabled:opacity-50">Previous</button>
          <span className="text-sm text-muted-foreground">Page {page + 1}</span>
          <button onClick={() => setPage(page + 1)} disabled={(page + 1) * 50 >= total} className="rounded-lg border border-border px-3 py-1.5 text-sm text-muted-foreground hover:bg-accent disabled:opacity-50">Next</button>
        </div>
      )}
    </div>
  );
}
