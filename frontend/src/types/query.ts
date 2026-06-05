export interface QueryRequest {
  query: string;
}

export interface QueryResult {
  generated_query: Record<string, unknown>;
  results: Record<string, unknown>[];
  count: number;
  execution_time_ms: number;
  query_type?: string;
}

export interface QueryHistoryItem {
  id: string;
  query: string;
  timestamp: string;
  result_count: number;
  execution_time_ms: number;
  status: 'success' | 'error';
}

export interface ExampleQuery {
  id: string;
  text: string;
  icon: string;
}

export const EXAMPLE_QUERIES: ExampleQuery[] = [
  { id: 'eq-1', text: 'Show all failed transactions', icon: '❌' },
  { id: 'eq-2', text: 'Transactions above ₹5000', icon: '💰' },
  { id: 'eq-3', text: 'Total successful payment amount', icon: '✅' },
  { id: 'eq-4', text: 'Show Amazon transactions this week', icon: '🛒' },
  { id: 'eq-5', text: 'Average transaction amount by merchant', icon: '📊' },
  { id: 'eq-6', text: 'Count of pending UPI payments', icon: '⏳' },
];
