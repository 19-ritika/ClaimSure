import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SubmitClaim.css';

const SubmitClaim = () => {
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [claimTitle, setClaimTitle] = useState('');
  const [claimType, setClaimType] = useState('');
  const [claimDetails, setClaimDetails] = useState('');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  // Handle file change
  const handleFileChange = (e) => {
    const newFile = e.target.files[0];

    // If file size exceeds 50MB, alert the user
    if (newFile && newFile.size > 50 * 1024 * 1024) {
      alert("File size exceeds 50MB. Please upload a smaller file.");
      return;
    }

    setFile(newFile);
  };

  // Handle form submission
  const handleFormSubmit = async (e) => {
    e.preventDefault();

    const userId = localStorage.getItem('user_id');
    if (!userId) {
      alert("User ID not found. Please log in again.");
      return;
    }

    // Prepare the form data, including the file if it exists
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('claimTitle', claimTitle);
    formData.append('claimType', claimType);
    formData.append('claimDetails', claimDetails);
    if (file) {
      formData.append('file', file);
    }

    setUploading(true);  // Indicate that submission is in progress

    try {
      // Submit the claim data and file to the backend
      const response = await fetch('http://localhost:5000/claims/submit-claim', {
        method: 'POST',
        body: formData,  // Do not set 'Content-Type', let the browser handle it
      });

      const data = await response.json();

      if (response.ok) {
        alert('Claim submitted successfully!');
        navigate('/manage-claims');
      } else {
        alert("Error submitting claim: " + data.error);
      }
    } catch (error) {
      console.error("Error submitting claim:", error);
      alert("An error occurred while submitting the claim.");
    } finally {
      setUploading(false);  // Reset uploading status
    }
  };

  return (
    <div className="submit-claim-container">
      {!isFormVisible ? (
        <div className="intro-text">
          <h2>Welcome to ClaimSure!</h2>
          <button className="submit-claim-btn" onClick={() => setIsFormVisible(true)}>
            Submit a Claim
          </button>
        </div>
      ) : (
        <div className="claim-form">
          <h2>Submit Your Claim</h2>
          <form onSubmit={handleFormSubmit}>
            <input
              type="text"
              placeholder="Claim Title (max 20 characters)"
              value={claimTitle}
              onChange={(e) => setClaimTitle(e.target.value)}
              maxLength="20"
              required
            />
            <select
              value={claimType}
              onChange={(e) => setClaimType(e.target.value)}
              required
            >
              <option value="">Select Claim Type</option>
              <option value="medical">Medical</option>
              <option value="life">Life</option>
              <option value="car">Car</option>
              <option value="home">Home</option>
              <option value="property">Property</option>
            </select>
            <textarea
              placeholder="Claim Details"
              value={claimDetails}
              onChange={(e) => setClaimDetails(e.target.value)}
              required
            ></textarea>
            <input
              type="file"
              onChange={handleFileChange}
            />
            {file && (
              <p className="file-info-text">
                Upload only one consolidated PDF under 50MB. If you want to select another file, click on "Choose file" again.
              </p>
            )}
            <button id="submitBtn" type="submit" disabled={uploading}>
              {uploading ? "Submitting..." : "Submit Claim"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default SubmitClaim;
