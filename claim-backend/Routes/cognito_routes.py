from flask import Blueprint, request, jsonify
from components.cognito import create_user_pool, create_app_client, register_user, login_user, logout_user
import boto3
from botocore.exceptions import ClientError

# Define the blueprint
cognito_routes = Blueprint('cognito_routes', __name__)

# AWS Cognito client (Ensure your region and credentials are correct)
cognito_client = boto3.client('cognito-idp', region_name='us-east-1')

# User Pool and App Client setup
user_pool_name = "claimSure-user-pool"
user_pool_id = create_user_pool(user_pool_name)
app_client_id = create_app_client(user_pool_id, "my_app_client")

# Register a user (sign-up)
@cognito_routes.route('/register', methods=['POST'])
def register():
    try:
        # Get user data from request
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        # Register the user using Cognito
        register_response = register_user(app_client_id, email, password)

        if register_response:
            return jsonify({
                "message": "User registered successfully",
                "UserSub": register_response['UserSub'],  # Return UserSub
                "Username": register_response['Username']  # Return Username (email)
            }), 201
        else:
            return jsonify({"error": "User registration failed"}), 500

    except ClientError as e:
        # More specific error handling for Cognito errors
        print(f"Cognito error response: {e.response['Error']}")
        return jsonify({"error": f"Error registering user: {e.response['Error']['Message']}"}), 500
    except Exception as e:
        # Catch any other exceptions and log them
        print(f"Error registering user: {str(e)}")
        return jsonify({"error": f"Error registering user: {str(e)}"}), 500

# Login a user
@cognito_routes.route('/login', methods=['POST'])
def login():
    try:
        # Get login credentials from request
        data = request.json
        email = data.get('email')  # Accept email instead of username
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        # Log in the user using Cognito with the email
        auth_result, user_id = login_user(app_client_id, email, password)  # Pass email instead of username

        if auth_result:
            # Send back the tokens to the frontend on successful login
            return jsonify({"message": "Login successful", "tokens": auth_result, "user_id": user_id}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Logout a user
@cognito_routes.route('/logout', methods=['POST'])
def logout():
    try:
        # Get access token from request
        data = request.json
        access_token = data.get('access_token')

        if not access_token:
            return jsonify({"error": "Missing access token"}), 400

        # Log out the user using Cognito
        logout_response = logout_user(access_token)

        if logout_response:
            return jsonify({"message": "Logged out successfully"}), 200
        else:
            return jsonify({"error": "Logout failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
