import apiClient from './client';
import type { AuditLog, PaginatedResponse } from '@/types/api';

export const auditApi = {
  getLogs: async (params?: {
    page?: number;
    limit?: number;
    user_id?: string;
    action?: string;
  }): Promise<PaginatedResponse<AuditLog>> => {
    const { data } = await apiClient.get<PaginatedResponse<AuditLog>>('/audit/logs', {
      params,
    });
    return data;
  },
};
