import React from 'react';
import { Navigate } from 'react-router-dom'; // Outlet removed
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  isAdminRoute?: boolean;
  children: React.ReactNode; // Explicitly define children
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ isAdminRoute = false, children }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    // You might want to show a loading spinner here
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (isAdminRoute && !user?.is_admin) {
    // If it's an admin route and user is not admin, redirect to home or a "not authorized" page
    return <Navigate to="/" replace />;
  }

  return <>{children}</>; // Render children directly
};

export default ProtectedRoute;
