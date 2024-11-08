import React, { useState } from 'react';
import './ForgotPassword.css';  // Import the CSS file for styling

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleForgotPassword = (e) => {
    e.preventDefault();
    // Simulate the process of sending a reset link
    if (email) {
      console.log('Sending reset link to:', email);
      setMessage('A reset link has been sent to your email address.');
      setError('');
    } else {
      setError('Please enter a valid email address.');
      setMessage('');
    }
  };

  return (
    <div className="container">
      <h2>Forgot Password</h2>
      <form onSubmit={handleForgotPassword}>
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <br />
        <button type="submit">Send Reset Link</button>
      </form>

      {message && <p className="message">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="back-to-login">
        <button onClick={() => window.history.back()}>Back to Login</button>
      </div>
    </div>
  );
};

export default ForgotPassword;
