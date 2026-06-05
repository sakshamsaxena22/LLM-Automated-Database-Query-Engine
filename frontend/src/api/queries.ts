import apiClient from './client';
import type { QueryRequest, QueryResult, QueryHistoryItem } from '@/types/query';

export const queryApi = {
  execute: async (payload: QueryRequest): Promise<QueryResult> => {
    const { data } = await apiClient.post<QueryResult>('/ai/query', payload);
    return data;
  },

  getHistory: async (): Promise<QueryHistoryItem[]> => {
    const { data } = await apiClient.get<QueryHistoryItem[]>('/ai/history');
    return data;
  },
};
