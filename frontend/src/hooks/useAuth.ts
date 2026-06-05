import { useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import apiClient from '../api/client';

export function useAuth() {
  const { user, isAuthenticated, setTokens, setUser, logout } = useAuthStore();

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await apiClient.post('/auth/login', { email, password });
    setTokens(data.access_token, data.refresh_token);
    // Fetch user profile
    const { data: profile } = await apiClient.get('/auth/me');
    setUser({
      id: profile._id || data.user_id,
      email: profile.email,
      full_name: profile.full_name,
      role: profile.role,
      org_id: profile.org_id || '',
    });
    return data;
  }, [setTokens, setUser]);

  const register = useCallback(async (email: string, password: string, fullName: string) => {
    const { data } = await apiClient.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    setTokens(data.access_token, data.refresh_token);
    const { data: profile } = await apiClient.get('/auth/me');
    setUser({
      id: profile._id || data.user_id,
      email: profile.email,
      full_name: profile.full_name,
      role: profile.role,
      org_id: profile.org_id || '',
    });
    return data;
  }, [setTokens, setUser]);

  return { user, isAuthenticated, login, register, logout };
}
