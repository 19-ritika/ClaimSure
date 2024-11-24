from flask import Blueprint, request, jsonify
from components.cognito import create_user_pool, create_app_client, register_user, login_user, logout_user
import boto3
from botocore.exceptions import ClientError
from components.cognito import initiate_password_reset, confirm_password_reset

# define the blueprint for authentication routes
cognito_routes = Blueprint('cognito_routes', __name__)

# AWS Cognito client (need to ensure region and credentials are correct)
cognito_client = boto3.client('cognito-idp', region_name='us-east-1')

# create new Cognito user pool to manage users
user_pool_name = "claimSure-user-pool"
user_pool_id = create_user_pool(user_pool_name)
app_client_id = create_app_client(user_pool_id, "my_app_client")

@cognito_routes.route('/register', methods=['POST'])
def register():
    try:
        # get user data from request
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password: 
            return jsonify({"error": "Missing email or password"}), 400

        # register the user using Cognito
        register_response = register_user(app_client_id, user_pool_id, email, password)

        # check if there was an error in the registration 
        if 'error' in register_response:
            return jsonify({"error": register_response['error']}), 500

        # if registration successful, return user details
        return jsonify({
            "message": "User registered successfully",
            "UserSub": register_response['UserSub'],
            "Username": register_response['Username']
        }), 201

    except Exception as e:
        print(f"Error registering user: {str(e)}")
        return jsonify({"error": f"Error registering user: {str(e)}"}), 500

# login a user
@cognito_routes.route('/login', methods=['POST'])
def login():
    try:
        # Get login credentials from request
        data = request.json
        email = data.get('email')  
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Missing email or password"}), 400

        # log in the user using Cognito 
        auth_result, user_id = login_user(app_client_id, email, password)  

        if auth_result:
            # if successful, return login tokens and user ID to frontend
            return jsonify({"message": "Login successful", "tokens": auth_result, "user_id": user_id}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# logout a user
@cognito_routes.route('/logout', methods=['POST'])
def logout():
    try:
        # get access token from request
        data = request.json
        access_token = data.get('access_token')

        if not access_token:
            return jsonify({"error": "Missing access token"}), 400

        # use Cognito to logout the user
        logout_response = logout_user(access_token)

        if logout_response:
            return jsonify({"message": "Logged out successfully"}), 200
        else:
            return jsonify({"error": "Logout failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cognito_routes.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        # Get email from request and use app_client_id instead of client_id
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({"error": "Missing email"}), 400

        # Initiate password reset using Cognito and app_client_id
        response = initiate_password_reset(app_client_id, email)

        # If successful, return success message
        if 'error' in response:
            return jsonify({"error": response['error']}), 500

        return jsonify({"message": "OTP sent to email"}), 200

    except Exception as e:
        print(f"Error initiating password reset: {str(e)}")
        return jsonify({"error": f"Error initiating password reset: {str(e)}"}), 500


# Confirm password reset - Verify OTP and set new password
@cognito_routes.route('/reset-password', methods=['POST'])
def reset_password():
    try:
       
        raw_data = request.data.decode('utf-8') 
        data = request.get_json()

        email = data.get('email', '').strip()  
        otp = data.get('otp', '').strip()  
        new_password = data.get('newPassword', '').strip()

        # Call the function to confirm the password reset with the provided data
        response = confirm_password_reset(app_client_id, email, otp, new_password)
        if 'error' in response:
            return jsonify({"error": response['error']}), 500

        return jsonify({"message": "Password reset successful"}), 200

    except Exception as e:
        print(f"Error resetting password: {str(e)}")
        return jsonify({"error": f"Error resetting password: {str(e)}"}), 500
