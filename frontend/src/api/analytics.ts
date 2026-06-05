import apiClient from './client';
import type { AnalyticsOverview, HealthStatus, DbHealthStatus } from '@/types/api';

export const analyticsApi = {
  getOverview: async (): Promise<AnalyticsOverview> => {
    const { data } = await apiClient.get<AnalyticsOverview>('/analytics/overview');
    return data;
  },

  getHealth: async (): Promise<HealthStatus> => {
    const { data } = await apiClient.get<HealthStatus>('/health');
    return data;
  },

  getDbHealth: async (): Promise<DbHealthStatus> => {
    const { data } = await apiClient.get<DbHealthStatus>('/health/db');
    return data;
  },
};
