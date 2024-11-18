// NaviBar.js
import React from 'react';
import './NaviBar.css';  // Import the CSS for the navigation bar

const NaviBar = ({ navigate }) => {
  const handleLogout = () => {
    // Clear localStorage (remove auth tokens and user_id)
    localStorage.removeItem('auth_tokens');
    localStorage.removeItem('user_id');

    // Redirect to login page after logout
    navigate('/login');
  };

  return (
    <div className="navbar">
      <div className="logo">
        <h1>Claim <span styel = {{color: 'yellow'}}>Sure</span></h1>
      </div>
      <div className="tabs">
        <button onClick={() => navigate('/submit-claim')}>Submit Claim</button>
        <button onClick={() => navigate('/manage-claims')}>Manage your claims</button>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  );
};

export default NaviBar;
