import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'; // Import useNavigate and BrowserRouter
import NaviBar from './Components/NaviBar';
import Login from './Components/Auth/Login';
import Register from './Components/Auth/Register';
import SubmitClaim from './Components/SubmitClaim';
import ManageClaims from './Components/ManageClaims'; // Import the ManageClaims component
import ForgotPassword from './Components/Auth/ForgotPassword';

// Main App component that renders the navigation and routes
function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div>
        <AppWithRouter />
      </div>
    </BrowserRouter>
  );
}

// This component is wrapped inside the BrowserRouter
const AppWithRouter = () => {
  const navigate = useNavigate(); // Use useNavigate inside this component

  return (
    <div>
      <NaviBar navigate={navigate} /> {/* Pass navigate function as prop */}
      <Routes>
        {/* Home route (the page shown when user first lands) */}
        <Route path="/" element={<SubmitClaim />} /> {/* Will show the submit claim intro page initially */}

        {/* SubmitClaim Route */}
        <Route path="/submit-claim" element={<SubmitClaim />} /> {/* Submit Claim form page */}

        {/* Manage Claims Route */}
        <Route path="/manage-claims" element={<ManageClaims />} /> {/* Manage Claims page */}

        {/* Authentication Routes */}
        <Route path="/login" element={<Login />} /> {/* Login page */}
        <Route path="/register" element={<Register />} /> {/* Register page */}
        <Route path="/forgot-password" element={<ForgotPassword />} /> {/* Forgot Password page */}
      </Routes>
    </div>
  );
};

export default App;
