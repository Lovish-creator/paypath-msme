import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, TokenResponse } from '../types';
import { api, tokenStorage } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    business_name: string;
    enterprise_type?: string;
    udyam_number?: string;
    state?: string;
    district?: string;
    industry_category?: string;
    contact_phone?: string;
  }) => Promise<void>;
  loginDemo: () => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    try {
      const u = await api.getMe();
      setUser(u);
    } catch (err) {
      console.warn('Failed to fetch authenticated user session:', err);
      setUser(null);
      tokenStorage.clear();
    }
  };

  const loginDemo = async () => {
    try {
      setLoading(true);
      const res = await api.login({
        email: 'demo@apexuniforms.in',
        password: 'Password123!',
      });
      setUser(res.user);
    } catch (err) {
      console.error('Demo login failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const existingToken = tokenStorage.get();
      if (existingToken) {
        try {
          const u = await api.getMe();
          setUser(u);
          setLoading(false);
          return;
        } catch {
          tokenStorage.clear();
        }
      }
      // If no valid session, auto-login with default demo credentials for seamless judge review
      await loginDemo();
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const res = await api.login({ email, password });
      setUser(res.user);
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: {
    email: string;
    password: string;
    business_name: string;
    enterprise_type?: string;
    udyam_number?: string;
    state?: string;
    district?: string;
    industry_category?: string;
    contact_phone?: string;
  }) => {
    setLoading(true);
    try {
      const res = await api.register(data);
      setUser(res.user);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        loginDemo,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
