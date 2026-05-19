/**
 * StartupOS AI — Auth Hook
 * 
 * React context for global authentication state.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import * as api from '../services/api';

interface AuthState {
  user: api.User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<api.User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing token on mount
  useEffect(() => {
    if (api.isAuthenticated()) {
      api.getMe()
        .then(setUser)
        .catch(() => {
          api.logout();
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    setError(null);
    try {
      await api.login(email, password);
      const me = await api.getMe();
      setUser(me);
    } catch (err: any) {
      const msg = err?.detail || 'Login failed. Please check your credentials.';
      setError(msg);
      throw err;
    }
  };

  const register = async (email: string, password: string, name?: string) => {
    setError(null);
    try {
      await api.register(email, password, name);
      const me = await api.getMe();
      setUser(me);
    } catch (err: any) {
      const msg = err?.detail || 'Registration failed. Please try again.';
      setError(msg);
      throw err;
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      register,
      logout,
      error,
      clearError,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
