import boto3
from botocore.exceptions import ClientError
import jwt  


# Initialize the Cognito client
cognito_client = boto3.client('cognito-idp', region_name='us-east-1')  # Ensure your AWS region is correct

# Create a user pool if it doesn't exist
def create_user_pool(pool_name):
    try:
        # List all user pools
        response = cognito_client.list_user_pools(MaxResults=60)
        for pool in response['UserPools']:
            if pool['Name'] == pool_name:
                print(f"User pool '{pool_name}' already exists.")
                return pool['Id']  # Return existing pool ID
        
        # If pool doesn't exist, create one
        response = cognito_client.create_user_pool(
            PoolName=pool_name,
            UsernameAttributes=['email'],  # Use email as the primary username
            AutoVerifiedAttributes=['email'],  # Automatically verify email
            MfaConfiguration='OFF',  # No MFA for simplicity
            # Removed AliasAttributes completely
        )
        
        print(f"User pool created successfully with ID: {response['UserPool']['Id']}")
        return response['UserPool']['Id']
    except ClientError as e:
        print(f"Error creating user pool: {e}")
        return None

# Create an app client for the user pool if it doesn't exist
def create_app_client(user_pool_id, client_name):
    try:
        if not user_pool_id:
            print("Error: Invalid User Pool ID. Cannot create app client.")
            return None

        # List existing app clients for the pool to check if it exists
        response = cognito_client.list_user_pool_clients(UserPoolId=user_pool_id)
        for client in response['UserPoolClients']:
            if client['ClientName'] == client_name:
                print(f"App client '{client_name}' already exists.")
                return client['ClientId']  # Return existing client ID
        
        # If app client doesn't exist, create one
        response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
            GenerateSecret=False,  # Don't generate client secret (suitable for public clients like mobile/web)
            ExplicitAuthFlows=['ALLOW_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH'],  # Allow auth with email/password and refresh tokens
            SupportedIdentityProviders=['COGNITO'],  # Default identity provider (Cognito)
        )
        print(f"App client created successfully with Client ID: {response['UserPoolClient']['ClientId']}")
        return response['UserPoolClient']['ClientId']
    except ClientError as e:
        print(f"Error creating app client: {e}")
        return None

from components.sns import create_sns_topic 
sns_client = boto3.client('sns', region_name='us-east-1')
import json
# Register a user (signup with email and password)
def register_user(client_id, email, password):
    try:
        response = cognito_client.sign_up(
            ClientId=client_id,
            Username=email,  # Email as the username
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}],  # Only email attribute
        )
        print(f"User registered successfully: {response}")
         # After user is registered, subscribe the user to an SNS topic
        user_sub = response['UserSub']
        topic_name = "ClaimSubmissionTopic"  # You can define a specific topic name here
        
        # Get or create the SNS topic
        sns_topic_arn = create_sns_topic(topic_name)
        
        # Subscribe the user's email to the SNS topic
        if sns_topic_arn:
            sns_client.subscribe(
                TopicArn=sns_topic_arn,
                Protocol='email',
                Endpoint=email,  # The user's email
                Attributes={
                    'FilterPolicy': json.dumps({
                        'UserID': [user_sub]  # Filter policy based on the UserSub (UserID)
                    })
                }
            )
            print(f"User email {email} subscribed to SNS topic: {sns_topic_arn}")
        return {
            'UserSub': response['UserSub'],  # Correct way to access UserSub
            'Username': email  # Use email as the username
        }  
    except ClientError as e:
        print(f"Error registering user: {e}")
        # Print full error response for debugging
        if e.response:
            print(f"Cognito error response: {e.response['Error']}")
        return None

def login_user(client_id, email, password):
    try:
        # Authenticate the user using email and password
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=client_id,
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        # Extract the ID Token and Access Token
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        
        # Decode the ID Token to extract the 'sub' (user_id)
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})  # Decode without verifying signature (for now)
        user_id = decoded_token['sub']  # This is the unique user ID (sub) in Cognito
        
        print(f"User logged in successfully. User ID: {user_id}")
        
        # Return both the tokens and user_id
        return response, user_id

    except ClientError as e:
        print(f"Error logging in user: {e}")
        if e.response:
            print(f"Cognito error response: {e.response['Error']}")
        return None, None

def logout_user(access_token):
    try:
        # Log the user out from all devices
        response = cognito_client.global_sign_out(AccessToken=access_token)
        print("Cognito logout response:", response)  # Debugging line to confirm successful logout
        return response
    except ClientError as e:
        print(f"Error logging out user: {e}")
        return None

