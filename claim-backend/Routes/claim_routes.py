from flask import Blueprint, request, jsonify
from claims_lib import generate_unique_claim_id
from components.dynamoDB import add_claim_to_dynamoDB, get_claims_by_user_id, update_claim_in_dynamoDB, delete_claim_from_dynamoDB
from components.s3 import upload_file_to_s3, generate_presigned_url
from werkzeug.utils import secure_filename
from claims_lib.claims_due_count import count_claims_due_in_next_days

# creating a blueprint for claim routes
claim_routes = Blueprint('claim_routes', __name__) 

# creating a route to submit claim
@claim_routes.route('/submit-claim', methods=['POST'])
def submit_claim():
    data = request.form  
    user_id = data.get('user_id')
    claim_title = data.get('claimTitle')
    claim_type = data.get('claimType')
    claim_details = data.get('claimDetails')

    # check that required fields are provided
    if not user_id or not claim_title or not claim_type or not claim_details:
        return jsonify({"error": "All fields are required"}), 400

    # generate unique Claim ID
    claim_id = generate_unique_claim_id()

    # if no files are uploaded set file url to none
    file_url = None

    # if there is a file in the request, upload it to S3 and get the URL
    if 'file' in request.files:
        file = request.files['file']
        file_url = upload_file_to_s3(user_id, claim_id, file)  

        # for accessing the file create a temporary secure link
        file_url = generate_presigned_url(user_id, claim_id, secure_filename(file.filename))

    # save claim data into DynamoDB
    add_claim_to_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details, file_url)


    return jsonify({'status': 'Claim submitted successfully', 'claim_id': claim_id, 'file_url': file_url}), 200

# creating a route to get claim
@claim_routes.route('/get-claims', methods=['GET'])
def get_claims():
    # get user_id from query parameters
    user_id = request.args.get('user_id')

    # check if user_id is provided
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        # fetch claims from DynamoDB by user_id
        claims = get_claims_by_user_id(user_id)

    
        if not claims:
            return jsonify({"message": "No claims found for this user."}), 404

        
        return jsonify({"claims": claims}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# creating a route to update claim    
@claim_routes.route('/update-claim', methods=['POST'])
def update_claim():
    # extract data from json
    data = request.json
    user_id = data.get('user_id')
    claim_id = data.get('claim_id')
    claim_title = data.get('ClaimTitle')  
    claim_type = data.get('ClaimType')
    claim_details = data.get('ClaimDetails')

    if not all([user_id, claim_id, claim_title, claim_type, claim_details]):
        return jsonify({"error": "All fields are required for updating the claim"}), 400

    try:
        # calling update_claim_in_dynamoDB function
        update_claim_in_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details)
        return jsonify({'status': 'Claim updated successfully'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# creating a route to delete claim    
@claim_routes.route('/delete-claim', methods=['DELETE'])
def delete_claim():
    # get user_id and claim_id from URL query parameter
    user_id = request.args.get('user_id')
    claim_id = request.args.get('claim_id')

    if not user_id or not claim_id:
        return jsonify({"error": "User ID and Claim ID are required for deletion"}), 400

    try:
        # try deleting the claim from Dynamodb using user_id and claim_id
        delete_claim_from_dynamoDB(user_id, claim_id)
        return jsonify({'status': 'Claim deleted successfully'}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@claim_routes.route('/count-due', methods=['GET'])
def get_claims_due_in_next_30_days():
    user_id = request.args.get('user_id')

    # Check if user_id is provided
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        # Fetch claims from DynamoDB by user_id
        claims = get_claims_by_user_id(user_id)

        if not claims:
            return jsonify({"message": "No claims found for this user."}), 404

        # Call the function from the library to count claims that are due in the next 30 days
        claims_due_count = count_claims_due_in_next_days(claims, 30)

        return jsonify({'claims_due_in_next_30_days': claims_due_count}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500