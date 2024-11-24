import React from 'react';
import { Navigate } from 'react-router-dom';

// function to only let logged in users access required pages
const ProtectedRoute = ({ children }) => {
  // Check if user is logged in by checking in localStorage
  const userId = localStorage.getItem('user_id');

  if (!userId) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
