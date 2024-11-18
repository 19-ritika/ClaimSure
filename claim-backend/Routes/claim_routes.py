from flask import Blueprint, request, jsonify
from claims_lib import generate_unique_claim_id
from components.dynamoDB import add_claim_to_dynamoDB, get_claims_by_user_id, update_claim_in_dynamoDB, delete_claim_from_dynamoDB
from components.s3 import upload_file_to_s3, generate_presigned_url
from werkzeug.utils import secure_filename

claim_routes = Blueprint('claim_routes', __name__)

@claim_routes.route('/submit-claim', methods=['POST'])
def submit_claim():
    data = request.form  # Access form data
    user_id = data.get('user_id')
    claim_title = data.get('claimTitle')
    claim_type = data.get('claimType')
    claim_details = data.get('claimDetails')

    # Ensure that required fields are provided
    if not user_id or not claim_title or not claim_type or not claim_details:
        return jsonify({"error": "All fields are required"}), 400

    # Generate unique Claim ID
    claim_id = generate_unique_claim_id()

    # Initialize file_url to None (in case file is not uploaded)
    file_url = None

    # If there is a file in the request, upload it to S3
    if 'file' in request.files:
        file = request.files['file']
        file_url = upload_file_to_s3(user_id, claim_id, file)  # Pass claim_id to the upload function

        # Generate a pre-signed URL for accessing the file
        file_url = generate_presigned_url(user_id, claim_id, secure_filename(file.filename))

    # Insert claim data into DynamoDB
    add_claim_to_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details, file_url)

    # Return success response
    return jsonify({'status': 'Claim submitted successfully', 'claim_id': claim_id, 'file_url': file_url}), 200

@claim_routes.route('/get-claims', methods=['GET'])
def get_claims():
    # Get user_id from query parameters
    user_id = request.args.get('user_id')

    # Check if user_id is provided
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        # Fetch claims from DynamoDB by UserID
        claims = get_claims_by_user_id(user_id)

        # If no claims found
        if not claims:
            return jsonify({"message": "No claims found for this user."}), 404

        # Return the claims as a JSON response
        return jsonify({"claims": claims}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@claim_routes.route('/update-claim', methods=['POST'])
def update_claim():
    data = request.json
    user_id = data.get('user_id')
    claim_id = data.get('claim_id')
    claim_title = data.get('ClaimTitle')  # Fixed to match client JSON
    claim_type = data.get('ClaimType')
    claim_details = data.get('ClaimDetails')

    if not all([user_id, claim_id, claim_title, claim_type, claim_details]):
        return jsonify({"error": "All fields are required for updating the claim"}), 400

    try:
        update_claim_in_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details)
        return jsonify({'status': 'Claim updated successfully'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claim_routes.route('/delete-claim', methods=['DELETE'])
def delete_claim():
    user_id = request.args.get('user_id')
    claim_id = request.args.get('claim_id')

    if not user_id or not claim_id:
        return jsonify({"error": "User ID and Claim ID are required for deletion"}), 400

    try:
        delete_claim_from_dynamoDB(user_id, claim_id)
        return jsonify({'status': 'Claim deleted successfully'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500