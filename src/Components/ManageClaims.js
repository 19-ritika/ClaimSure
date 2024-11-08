import React, { useState, useEffect } from 'react';
import './ManageClaim.css';

const ManageClaims = () => {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingClaim, setEditingClaim] = useState(null);
  const [editedData, setEditedData] = useState({});

  const claimTypes = [
    { value: '', label: 'Select Claim Type' },
    { value: 'medical', label: 'Medical' },
    { value: 'life', label: 'Life' },
    { value: 'car', label: 'Car' },
    { value: 'home', label: 'Home' },
    { value: 'property', label: 'Property' },
  ];

  useEffect(() => {
    const fetchClaims = async () => {
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        setError("User ID not found. Please log in.");
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`http://localhost:5000/claims/get-claims?user_id=${userId}`);
        const data = await response.json();

        if (response.ok) {
          setClaims(data.claims);
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

  const handleDelete = async (claimId) => {
    const userId = localStorage.getItem('user_id');
    try {
      const response = await fetch(`http://localhost:5000/claims/delete-claim?user_id=${userId}&claim_id=${claimId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setClaims(claims.filter(claim => claim.ClaimID.S !== claimId));
      } else {
        const data = await response.json();
        setError(data.error || "Failed to delete the claim.");
      }
    } catch {
      setError("An error occurred while deleting the claim.");
    }
  };

  const handleEdit = (claim) => {
    setEditingClaim(claim.ClaimID.S);
    setEditedData({
      ClaimTitle: claim.ClaimTitle.S,
      ClaimType: claim.ClaimType.S,
      ClaimDetails: claim.ClaimDetails.S
    });
  };

  const handleSave = async () => {
    const userId = localStorage.getItem('user_id');
    try {
      const response = await fetch(`http://localhost:5000/claims/update-claim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          claim_id: editingClaim,
          ...editedData
        })
      });

      if (response.ok) {
        setClaims(claims.map(claim => claim.ClaimID.S === editingClaim ? {
          ...claim,
          ClaimTitle: { S: editedData.ClaimTitle },
          ClaimType: { S: editedData.ClaimType },
          ClaimDetails: { S: editedData.ClaimDetails }
        } : claim));
        setEditingClaim(null);
      } else {
        const data = await response.json();
        setError(data.error || "Failed to update the claim.");
      }
    } catch {
      setError("An error occurred while updating the claim.");
    }
  };

  const handleCancel = () => {
    setEditingClaim(null);
    setEditedData({});
  };

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
                  <th>Submission Date</th>
                  <th>Due Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {claims.map((claim) => (
                  <tr key={claim.ClaimID.S}>
                    <td>
                      {editingClaim === claim.ClaimID.S ? (
                        <input
                          type="text"
                          value={editedData.ClaimTitle}
                          onChange={(e) => setEditedData({ ...editedData, ClaimTitle: e.target.value })}
                        />
                      ) : (
                        claim.ClaimTitle.S
                      )}
                    </td>
                    <td>
                      {editingClaim === claim.ClaimID.S ? (
                        <select
                          value={editedData.ClaimType}
                          onChange={(e) => setEditedData({ ...editedData, ClaimType: e.target.value })}
                        >
                          {claimTypes.map((type) => (
                            <option key={type.value} value={type.value}>{type.label}</option>
                          ))}
                        </select>
                      ) : (
                        claim.ClaimType.S
                      )}
                    </td>
                    <td>
                      {editingClaim === claim.ClaimID.S ? (
                        <input
                          type="text"
                          value={editedData.ClaimDetails}
                          onChange={(e) => setEditedData({ ...editedData, ClaimDetails: e.target.value })}
                        />
                      ) : (
                        claim.ClaimDetails.S
                      )}
                    </td>
                    <td>
                      {claim.FileURL.S ? (
                        <a href={claim.FileURL.S} target="_blank" rel="noopener noreferrer">View File</a>
                      ) : (
                        <span>No file</span>
                      )}
                    </td>
                    <td>{claim.submission_date}</td>
                    <td>{claim.due_date}</td>
                    <td>
                      {editingClaim === claim.ClaimID.S ? (
                        <div className="icon-container">
                          <span className="icon" onClick={handleSave}>✔️</span>
                          <span className="icon" onClick={handleCancel}>❌</span>
                        </div>
                      ) : (
                        <div className="icon-container">
                          <span className="icon" onClick={() => handleEdit(claim)}>✏️</span>
                          <span className="icon" onClick={() => handleDelete(claim.ClaimID.S)}>🗑️</span>
                        </div>
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
