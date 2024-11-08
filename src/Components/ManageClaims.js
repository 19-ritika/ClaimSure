import React, { useState, useEffect } from 'react';
import './ManageClaim.css'

const ManageClaims = () => {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch claims for the logged-in user from the backend
  useEffect(() => {
    const fetchClaims = async () => {
      const userId = localStorage.getItem('user_id');  // Assuming the user_id is saved in localStorage

      if (!userId) {
        setError("User ID not found. Please log in.");
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`http://localhost:5000/claims/get-claims?user_id=${userId}`);
        const data = await response.json();

        if (response.ok) {
          setClaims(data.claims);  // Set claims data from response
        } else {
          setError(data.error || "No claims.");
        }
      } catch (error) {
        setError("An error occurred while fetching claims.");
      } finally {
        setLoading(false);
      }
    };

    fetchClaims();
  }, []);

  return (
    <div className="manage-claims-container">
      <h2>Manage Your Claims</h2>

      {loading ? (
        <p>Loading claims...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div className="claims-table">
          {claims.length === 0 ? (
            <p>No claims available.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Claim Title</th>
                  <th>Claim Type</th>
                  <th>Claim Details</th>
                  <th>File</th>
                </tr>
              </thead>
              <tbody>
                {claims.map((claim) => (
                  <tr key={claim.ClaimID.S}>  {/* Use ClaimID as key */}
                    <td>{claim.ClaimTitle.S}</td>
                    <td>{claim.ClaimType.S}</td>
                    <td>{claim.ClaimDetails.S}</td>
                    <td>
                      {claim.FileURL.S ? (
                        <a href={claim.FileURL.S} target="_blank" rel="noopener noreferrer">View File</a>
                      ) : (
                        <span>No file</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
};

export default ManageClaims;
