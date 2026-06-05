import apiClient from './client';
import type { User } from '@/types/auth';

export const usersApi = {
  list: async (): Promise<User[]> => {
    const { data } = await apiClient.get<User[]>('/users');
    return data;
  },

  get: async (id: string): Promise<User> => {
    const { data } = await apiClient.get<User>(`/users/${id}`);
    return data;
  },

  update: async (id: string, payload: Partial<User>): Promise<User> => {
    const { data } = await apiClient.put<User>(`/users/${id}`, payload);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/users/${id}`);
  },
};
