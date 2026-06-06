import { useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import apiClient from '../api/client';

function decodeJwt(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      window.atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

export function useAuth() {
  const { user, isAuthenticated, setTokens, setUser, logout } = useAuthStore();

  const login = useCallback(async (email: string, password: string) => {
    // Clear any stale tokens first
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    const { data } = await apiClient.post('/auth/login', { email, password });
    setTokens(data.access_token, data.refresh_token);

    // Decode token to populate user store immediately
    const payload = decodeJwt(data.access_token);
    setUser({
      id: payload?.sub || data.user_id,
      email: payload?.email || email,
      full_name: payload?.full_name || 'User',
      role: payload?.role || 'viewer',
      org_id: payload?.org_id || '',
    });

    // Gracefully fetch full profile in the background
    try {
      const { data: profile } = await apiClient.get('/auth/me');
      setUser({
        id: profile._id || data.user_id,
        email: profile.email,
        full_name: profile.full_name,
        role: profile.role,
        org_id: profile.org_id || '',
      });
    } catch (err) {
      console.warn('Profile fetch failed, using token claims:', err);
    }

    return data;
  }, [setTokens, setUser]);

  const register = useCallback(async (email: string, password: string, fullName: string) => {
    // Clear stale tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    const { data } = await apiClient.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    setTokens(data.access_token, data.refresh_token);

    const payload = decodeJwt(data.access_token);
    setUser({
      id: payload?.sub || data.user_id,
      email: payload?.email || email,
      full_name: fullName,
      role: payload?.role || 'viewer',
      org_id: payload?.org_id || '',
    });

    try {
      const { data: profile } = await apiClient.get('/auth/me');
      setUser({
        id: profile._id || data.user_id,
        email: profile.email,
        full_name: profile.full_name,
        role: profile.role,
        org_id: profile.org_id || '',
      });
    } catch (err) {
      console.warn('Profile fetch failed, using token claims:', err);
    }

    return data;
  }, [setTokens, setUser]);

  return { user, isAuthenticated, login, register, logout };
}
