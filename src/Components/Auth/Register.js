import React, { useState } from 'react';
import './Register.css';  
import { Link } from 'react-router-dom';

//Defining the components for register function
const Register = () => {     
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [userSub, setUserSub] = useState('');  
  const [username, setUsername] = useState('');  

  // setting up base URL for the backend
  const baseURL = process.env.REACT_APP_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'http://claim-lb-2074056079.us-east-1.elb.amazonaws.com');
  
  // Function runs when user submits form
  const handleRegister = async (e) => {
    e.preventDefault();
    console.log('Registering:', { email, password });

    // Sending the email and password to backend
    const response = await fetch(`${baseURL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })  
    });

    const data = await response.json();

    if (response.ok) {
      setMessage(data.message);
      setUserSub(data.UserSub);  
      setUsername(data.Username);  
      setError('');
    } else {
      setError(data.error);
      setMessage('');
    }
  };

  return (
    // html for register page
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
