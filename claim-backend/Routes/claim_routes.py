from flask import Blueprint, request, jsonify
from components.utilities.uniq_claim_id import generate_unique_claim_id
from components.dynamoDB import add_claim_to_dynamoDB, get_claims_by_user_id
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