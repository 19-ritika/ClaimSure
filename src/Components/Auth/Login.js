import React, { useState } from 'react';
import './Login.css';  // Import the CSS file
import { Link, useNavigate } from 'react-router-dom';  // Use useNavigate instead of useHistory

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');  // To store any error message
  const navigate = useNavigate();  // Initialize useNavigate hook for redirection

  const handleLogin = async (e) => {
    e.preventDefault();
    console.log('Logging in:', { email, password });
    
    try {
      // Send credentials to the backend for authentication
      const response = await fetch('http://localhost:5000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })  // Send email instead of username
      });
    
      const data = await response.json();
    
      if (response.ok) {
        // If login is successful, store user_id and tokens in local storage
        const { message, tokens, user_id } = data;
        
        console.log('user_id:', user_id);  // Ensure user_id is correctly retrieved
        localStorage.setItem('user_id', user_id);  // Store user_id locally
        localStorage.setItem('auth_tokens', JSON.stringify(tokens));  // Store tokens for later use
  
        // If login is successful, redirect to /submit-claim
        setMessage(message);
        setError('');
        navigate('/submit-claim');  // Use navigate to redirect after successful login
      } else {
        // If login fails, show error message
        setError(data.error);
        setMessage('');
      }
    } catch (error) {
      setError('An error occurred during login.');
      setMessage('');
    }
  };
    

  return (
    <div className="container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <br />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <br />
        <button type="submit">Login</button>
      </form>

      {/* Forgot Password Button - Link to ForgotPassword component */}
      <div className="forgot-password">
        <Link to="/forgot-password" className="forgot-button">
          Forgot Password?
        </Link>
      </div>

      {/* Don't have an account? Sign up link */}
      <div className="signup-link">
        <p>Don't have an account? <Link to="/register">Sign Up</Link></p>
      </div>

      {message && <p className="message">{message}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default Login;
