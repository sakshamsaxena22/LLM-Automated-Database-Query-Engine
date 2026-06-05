export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'editor' | 'viewer';
  organization?: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  organization?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginResponse extends AuthTokens {
  user: User;
}

export interface RegisterResponse {
  message: string;
  user: User;
}
