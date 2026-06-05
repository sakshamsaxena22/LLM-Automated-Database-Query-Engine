export interface ApiResponse<T = unknown> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface HealthStatus {
  status: string;
  document_count?: number;
  error?: string;
  version?: string;
  uptime?: number;
}

export interface DbHealthStatus {
  status: 'connected' | 'disconnected';
  document_count?: number;
  error?: string;
  latency_ms?: number;
}

export interface AuditLog {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  resource: string;
  details: Record<string, unknown>;
  ip_address: string;
  timestamp: string;
}

export interface AnalyticsOverview {
  total_queries: number;
  total_users: number;
  total_collections: number;
  total_documents: number;
  avg_response_time_ms: number;
  queries_today: number;
  queries_this_week: number;
  query_trend: { date: string; count: number }[];
  popular_queries: { query: string; count: number }[];
  query_types: { type: string; count: number }[];
}
