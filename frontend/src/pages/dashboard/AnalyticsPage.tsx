import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import apiClient from '@/api/client';
import { BarChart3, Users, Database, AlertTriangle, Activity, Loader2 } from 'lucide-react';

interface OverviewData {
  total_users: number;
  total_queries: number;
  queries_last_24h: number;
  queries_last_7d: number;
  total_audit_logs: number;
  high_risk_operations: number;
  error_rate_24h_pct: number;
  operation_breakdown_7d: { _id: string; count: number }[];
}

const statCards = (data: OverviewData) => [
  { icon: Users, label: 'Total Users', value: data.total_users, color: 'text-primary bg-primary/10' },
  { icon: Database, label: 'Total Queries', value: data.total_queries, color: 'text-chart-2 bg-chart-2/10' },
  { icon: Activity, label: 'Queries (24h)', value: data.queries_last_24h, color: 'text-chart-3 bg-chart-3/10' },
  { icon: BarChart3, label: 'Queries (7d)', value: data.queries_last_7d, color: 'text-chart-4 bg-chart-4/10' },
  { icon: AlertTriangle, label: 'High Risk Ops', value: data.high_risk_operations, color: 'text-destructive bg-destructive/10' },
  { icon: Activity, label: 'Error Rate (24h)', value: `${data.error_rate_24h_pct}%`, color: 'text-chart-5 bg-chart-5/10' },
];

export function AnalyticsPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get('/analytics/overview')
      .then(({ data }) => setData(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        Failed to load analytics data
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-primary" />
          Analytics
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">Platform overview and usage metrics</p>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {statCards(data).map(({ icon: Icon, label, value, color }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 * i }}
            className="glass rounded-2xl p-6 transition-all hover:border-primary/20"
          >
            <div className="flex items-center gap-4">
              <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${color}`}>
                <Icon className="h-6 w-6" />
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">{value}</div>
                <div className="text-sm text-muted-foreground">{label}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Operation breakdown */}
      {data.operation_breakdown_7d && data.operation_breakdown_7d.length > 0 && (
        <div className="glass rounded-2xl p-6">
          <h3 className="mb-4 text-sm font-semibold text-foreground">Operations (Last 7 Days)</h3>
          <div className="space-y-3">
            {data.operation_breakdown_7d.map(({ _id, count }) => {
              const max = Math.max(...data.operation_breakdown_7d.map((o) => o.count));
              const pct = max > 0 ? (count / max) * 100 : 0;
              return (
                <div key={_id} className="flex items-center gap-3">
                  <span className="w-24 text-sm text-muted-foreground capitalize">{_id || 'unknown'}</span>
                  <div className="flex-1 rounded-full bg-muted/30 h-2.5 overflow-hidden">
                    <motion.div
                      className="h-full rounded-full bg-primary"
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.6, ease: 'easeOut' }}
                    />
                  </div>
                  <span className="w-12 text-right text-sm font-medium text-foreground">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
