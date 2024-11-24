import React, { useState } from 'react';
import './ForgotPassword.css';  
import { useNavigate } from 'react-router-dom';

// function for forgot password
const ForgotPassword = () => {
    const [step, setStep] = useState(1); // Step 1: Enter email, Step 2: Enter OTP & new password
    const [email, setEmail] = useState(''); // State to store email
    const [otp, setOtp] = useState(''); // State to store OTP
    const [newPassword, setNewPassword] = useState(''); // State to store new password
    const [message, setMessage] = useState(''); // State to store success/error message
    const [error, setError] = useState(''); // State to store error message
    const navigate = useNavigate();  

    // Setting up the base URL for the backend
    const baseURL = process.env.REACT_APP_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'http://claim-lb-2074056079.us-east-1.elb.amazonaws.com');

    // Function to request OTP for password reset
    const handleRequestOtp = async () => {
        try {
            const response = await fetch(`${baseURL}/auth/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email }), 
            });

            const data = await response.json();

            if (response.ok) {
                setMessage('OTP sent to your email.');
                setStep(2); // Move to step 2 after OTP is sent
            } else {
                setMessage(data.error || 'Error sending OTP.');
                setError(data.error || 'Error sending OTP.');
            }
        } catch (error) {
            setMessage('An error occurred while requesting OTP.');
            setError(error.message || 'An error occurred.');
        }
    };

    // Function to reset the password using OTP
    const handleResetPassword = async () => {
      try {
  
          const response = await fetch(`${baseURL}/auth/reset-password`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, otp, newPassword }),  
          });
  
          const contentType = response.headers.get('Content-Type');
  
          let data = {};
          if (contentType && contentType.includes('application/json')) {
              data = await response.json();
          } else {
              const text = await response.text();
              setMessage('Error: ' + text);
              return;
          }
  
          if (response.ok) {
              setMessage('Password reset successfully. You can now log in with your new password.');
          } else {
              setMessage(data.error || 'Failed to reset password');
          }
      } catch (error) {
          setMessage('Error: ' + error.message);
      }
  };


    return (
        <div className='container'>
            <h2>Forgot Password</h2>
            {message && <p>{message}</p>}
            {error && <p className="error">{error}</p>}

            {step === 1 && (
                <div>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                    />
                    <button onClick={handleRequestOtp}>Request OTP</button>
                </div>
            )}

            {step === 2 && (
                <div>
                    <label>OTP:</label>
                    <input
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        placeholder="Enter OTP"
                    />
                    <label>New Password:</label>
                    <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        placeholder="Enter new password"
                    />
                    <button onClick={handleResetPassword}>Reset Password</button>
                    <p><a href="/login">Login</a></p>
                </div>
            )}
        </div>
    );
};

export default ForgotPassword;
