import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [needsSetup, setNeedsSetup] = useState(false);
  const [loading, setLoading] = useState(true);

  const checkAuthStatus = useCallback(async () => {
    try {
      const status = await api.getAuthStatus();
      setNeedsSetup(!status.password_configured);

      // Check if we have a valid token
      const token = localStorage.getItem('pmtracker_token');
      if (token && status.password_configured) {
        // Verify token is still valid by making a test request
        try {
          await api.getPortfolioSummary();
          setIsAuthenticated(true);
        } catch (err) {
          // Token invalid, clear it
          localStorage.removeItem('pmtracker_token');
          setIsAuthenticated(false);
        }
      } else if (!status.password_configured) {
        // No password set up yet, show setup screen
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  const login = async (password) => {
    const response = await api.login(password);
    localStorage.setItem('pmtracker_token', response.access_token);
    setIsAuthenticated(true);
    return response;
  };

  const setup = async (password) => {
    const response = await api.setupPassword(password);
    localStorage.setItem('pmtracker_token', response.access_token);
    setNeedsSetup(false);
    setIsAuthenticated(true);
    return response;
  };

  const logout = () => {
    localStorage.removeItem('pmtracker_token');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        needsSetup,
        loading,
        login,
        setup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
