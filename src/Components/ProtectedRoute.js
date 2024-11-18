import React from 'react';
import { Navigate } from 'react-router-dom';

// ProtectedRoute component to guard routes that require authentication
const ProtectedRoute = ({ children }) => {
  // Check if user is authenticated by verifying user_id in localStorage
  const userId = localStorage.getItem('user_id');

  // If user is not authenticated, redirect them to the login page
  if (!userId) {
    return <Navigate to="/login" replace />;
  }

  // If user is authenticated, render the children (protected page)
  return children;
};

export default ProtectedRoute;
