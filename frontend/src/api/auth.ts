import apiClient from './client';
import type { LoginRequest, RegisterRequest, LoginResponse, RegisterResponse, User } from '@/types/auth';

export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    const { data } = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  },

  register: async (payload: RegisterRequest): Promise<RegisterResponse> => {
    const { data } = await apiClient.post<RegisterResponse>('/auth/register', payload);
    return data;
  },

  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },

  refresh: async (refreshToken: string) => {
    const { data } = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  },
};
