import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import NaviBar from './Components/NaviBar';
import Login from './Components/Auth/Login';
import Register from './Components/Auth/Register';
import SubmitClaim from './Components/SubmitClaim';
import ManageClaims from './Components/ManageClaims';
import ForgotPassword from './Components/Auth/ForgotPassword';
import ProtectedRoute from './Components/ProtectedRoute';

// main app component
function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div>
        <AppWithRouter />
      </div>
    </BrowserRouter>
  );
}

// routing logic
const AppWithRouter = () => {
  const navigate = useNavigate();

  return (
    // html components with protect routes to only allow logged in users 
    <div>
      <NaviBar navigate={navigate} />
      <Routes>
        {/* Protected Routes */}
        <Route path="/submit-claim" element={
          <ProtectedRoute>
            <SubmitClaim />
          </ProtectedRoute>
        } />
        <Route path="/manage-claims" element={
          <ProtectedRoute>
            <ManageClaims />
          </ProtectedRoute>
        } />

        {/* public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* Redirect root path to login */}
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </div>
  );
};

export default App;
