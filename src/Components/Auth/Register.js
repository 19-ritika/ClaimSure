import React, { useState } from 'react';
import './Register.css';  // Import the CSS file
import { Link } from 'react-router-dom';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [userSub, setUserSub] = useState('');  // State to store UserSub
  const [username, setUsername] = useState('');  // State to store Username (email)

  // Determine the base URL for the backend
  const baseURL = process.env.REACT_APP_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'http://claim-lb-2074056079.us-east-1.elb.amazonaws.com');

  const handleRegister = async (e) => {
    e.preventDefault();
    console.log('Registering:', { email, password });

    const response = await fetch(`${baseURL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })  // Send only email and password
    });

    const data = await response.json();

    if (response.ok) {
      setMessage(data.message);
      setUserSub(data.UserSub);  // Set the UserSub (user ID)
      setUsername(data.Username);  // Set the Username (email)
      setError('');
    } else {
      setError(data.error);
      setMessage('');
    }
  };

  return (
    <div className="container">
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
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
        <button type="submit">Register</button>
        <p>Already have an account? <Link to="/login">Login here</Link></p>
      </form>

      {message && <p className="message">{message}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default Register;
