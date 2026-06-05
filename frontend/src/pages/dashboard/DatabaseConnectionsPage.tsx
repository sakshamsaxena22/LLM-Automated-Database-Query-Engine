import { Server, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import apiClient from '@/api/client';

export function DatabaseConnectionsPage() {
  const [health, setHealth] = useState<{status: string; database?: string; collections?: number} | null>(null);
  const [appHealth, setAppHealth] = useState<{status: string; redis?: string} | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiClient.get('/health/db').then(({ data }) => setHealth(data)).catch(() => {}),
      apiClient.get('/health').then(({ data }) => setAppHealth(data)).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Server className="h-6 w-6 text-primary" />
          Database Connections
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">Service health and database status</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 max-w-3xl">
        {/* MongoDB */}
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            {health?.status === 'connected' ? (
              <CheckCircle className="h-5 w-5 text-chart-2" />
            ) : (
              <AlertCircle className="h-5 w-5 text-destructive" />
            )}
            <h3 className="text-lg font-semibold text-foreground">MongoDB</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <span className={`font-medium ${health?.status === 'connected' ? 'text-chart-2' : 'text-destructive'}`}>
                {health?.status || 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Database</span>
              <span className="text-foreground">{health?.database || '—'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Collections</span>
              <span className="text-foreground">{health?.collections ?? '—'}</span>
            </div>
          </div>
        </div>

        {/* Redis */}
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-4">
            {appHealth?.redis === 'connected' ? (
              <CheckCircle className="h-5 w-5 text-chart-2" />
            ) : (
              <AlertCircle className="h-5 w-5 text-chart-4" />
            )}
            <h3 className="text-lg font-semibold text-foreground">Redis</h3>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <span className={`font-medium ${
                appHealth?.redis === 'connected' ? 'text-chart-2' : 'text-chart-4'
              }`}>
                {appHealth?.redis || 'disabled'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Purpose</span>
              <span className="text-foreground">Query caching</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
