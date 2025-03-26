import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apis } from '../lib/api';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      // Explicitly check auth status with backend
      apis.getCurrentUser()
        .then(() => setAuthChecked(true))
        .catch(() => setAuthChecked(true));
    } else {
      setAuthChecked(true);
    }
  }, [isAuthenticated]);

  if (!isAuthenticated && authChecked) {
    // Redirect to login page with message and current location for redirect after login
    return (
      <Navigate
        to="/login"
        state={{
          from: location,
          message: "您需要登录才能查看此页面" // "You should be logged in to view this page"
        }}
        replace
      />
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
