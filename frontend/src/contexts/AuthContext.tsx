import React, { createContext, useContext, useEffect, useState } from 'react';
import { apis, RegisterRequest, User } from '../lib/api';

interface AuthContextType {
  user: User | null; // User type now includes is_admin?
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  ssoLogin: (accessToken: string) => Promise<void>;
  register: (
    username: string,
    password: string,
    email: string,
    fullName: string,
    phone: string,
    institution: string
  ) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('token');
    if (token) {
      // If token exists, fetch current user data
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const userData = await apis.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      // If token is invalid or expired, remove it
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await apis.login(username, password);
      localStorage.setItem('token', response.access_token);

      // Fetch user data after successful login
      await fetchCurrentUser();
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const ssoLogin = async (accessToken: string) => {
    localStorage.setItem('token', accessToken);
    await fetchCurrentUser();
  };

  const register = async (
    username: string,
    password: string,
    email: string,
    fullName: string,
    phone: string,
    institution: string
  ): Promise<boolean> => {
    try {
      const registerData: RegisterRequest = {
        username,
        password,
        email,
        full_name: fullName,
        phone,
        institution
      };

      // Register the user
      await apis.register(registerData);

      // After successful registration, login the user
      return await login(username, password);
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = async () => {
    // Try to call the logout API (which will clear the cookie)
    await apis.logout().catch(console.error);

    // Always clear local storage token regardless of API call success
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    // You can return a loading spinner or component here
    return <div>Loading...</div>;
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, ssoLogin, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
