import React from 'react';
import './NaviBar.css';  

// main nav bar function
const NaviBar = ({ navigate }) => {
  const handleLogout = () => {
    // clear stored user data stored from local storage
    localStorage.removeItem('auth_tokens');
    localStorage.removeItem('user_id');

    navigate('/login');
  };

  return (
    // function for nav bar which has buttons for submit, manage claims and logout
    <div className="navbar">
      <div className="logo">
        <h1>ClaimSure</h1>
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
