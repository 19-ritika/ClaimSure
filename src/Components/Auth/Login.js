import React, { useState } from 'react';
import './Login.css';  
import { Link, useNavigate } from 'react-router-dom';  

// function for login component
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');  
  const navigate = useNavigate();  

  // setting up the base URL for the backend
  const baseURL = process.env.REACT_APP_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'http://claim-lb-2074056079.us-east-1.elb.amazonaws.com');

  // function for login form submission
  const handleLogin = async (e) => {
    e.preventDefault();
    console.log('Logging in:', { email, password });
    
    try {
      // sending login related data to backend
      const response = await fetch(`${baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })  
      });
    
      const data = await response.json();
    
      if (response.ok) {
        
        const { message, tokens, user_id } = data;
        
        console.log('user_id:', user_id);  
        localStorage.setItem('user_id', user_id);  
        localStorage.setItem('auth_tokens', JSON.stringify(tokens));  
  
        // successful login, redirecting to /submit-claim
        setMessage(message);
        setError('');
        navigate('/submit-claim'); 
      } else {
        
        setError(data.error);
        setMessage('');
      }
    } catch (error) {
      setError('An error occurred during login.');
      setMessage('');
    }
  };

  return (
    //html for login page
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
