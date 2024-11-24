import boto3
from botocore.exceptions import ClientError
import jwt  


# initialize the Cognito client for interacting with AWS Cognito using boto3 sdk
cognito_client = boto3.client('cognito-idp', region_name='us-east-1')

# function to create a user pool 
def create_user_pool(pool_name):
    try:
        # list all user pools
        response = cognito_client.list_user_pools(MaxResults=60)
        for pool in response['UserPools']:
            if pool['Name'] == pool_name:
                print(f"User pool '{pool_name}' already exists.")
                return pool['Id']  
        
        # if pool doesn't exist, use create user pool function using parameters
        #PoolName, usernameattributes,autoverifiedattributes and mfaconfiguration.
        response = cognito_client.create_user_pool(
            PoolName=pool_name,
            UsernameAttributes=['email'],  
            AutoVerifiedAttributes=['email'],  
            MfaConfiguration='OFF',  
            
        )
        
        print(f"User pool created successfully with ID: {response['UserPool']['Id']}")
        return response['UserPool']['Id']
    except ClientError as e:
        print(f"Error creating user pool: {e}")
        return None

# Create an app client function for the user pool if it doesn't exist using parameters
#userpoolid, clientname, generatesecret, explicitauthflows, supportedidentify providers
def create_app_client(user_pool_id, client_name):
    try:
        if not user_pool_id:
            print("Error: Invalid User Pool ID. Cannot create app client.")
            return None

        # list existing app clients for the pool to check if it exists
        response = cognito_client.list_user_pool_clients(UserPoolId=user_pool_id)
        for client in response['UserPoolClients']:
            if client['ClientName'] == client_name:
                print(f"App client '{client_name}' already exists.")
                return client['ClientId']  
        
        # If app client doesn't exist, create one
        response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName=client_name,
            GenerateSecret=False,  # do not generate client secret
            ExplicitAuthFlows=['ALLOW_USER_PASSWORD_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH'],  # allow password logins and refresh tokens
            SupportedIdentityProviders=['COGNITO'],  # default identity provider (Cognito)
        )
        print(f"App client created successfully with Client ID: {response['UserPoolClient']['ClientId']}")
        return response['UserPoolClient']['ClientId']
    except ClientError as e:
        print(f"Error creating app client: {e}")
        return None

# import function to create SNS topic and set up SNS client for notifications through AWS SNS
from components.sns import create_sns_topic 
sns_client = boto3.client('sns', region_name='us-east-1')
import json
# function for registering a user (signup with email and password) using parameters
#clientid, username, password and user attributes
def register_user(client_id, user_pool_id, email, password):
    try:
        # register the user
        response = cognito_client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}],
        )
        print(f"User registered successfully: {response}")

        # function to confirm the user account automatically using parameters
        #userpoolid and username
        cognito_client.admin_confirm_sign_up(
            UserPoolId=user_pool_id,
            Username=email
        )
        print(f"User account confirmed for {email}")

        # function to mark the user email as verified using parameters
        #userpoolid, username and user attributes
        cognito_client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[{'Name': 'email_verified', 'Value': 'true'}]
        )
        print(f"Email verified for {email}")

        # subscribe the user to an SNS topic
        user_sub = response['UserSub']
        topic_name = "ClaimSubmissionTopic"
        sns_topic_arn = create_sns_topic(topic_name)
        
        if sns_topic_arn:
            # subscribe to SNS using email
            sns_client.subscribe(
                TopicArn=sns_topic_arn,
                Protocol='email',
                Endpoint=email,
                Attributes={
                    'FilterPolicy': json.dumps({
                        'UserID': [user_sub]
                    })
                }
            )
            print(f"User email {email} subscribed to SNS topic: {sns_topic_arn}")
        
        # Return user details upon success
        return {
            'UserSub': user_sub,
            'Username': email
        }

    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"ClientError in registering user: {error_message}")
        # Return the error message 
        return {'error': error_message}

def login_user(client_id, email, password):
    try:
        # function to authenticate the user using parameters like authflows, clientid and authparameters
    
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=client_id,
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        # extract the ID Token and Access Token
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        
        # decode the ID Token to get user informate
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})  
        user_id = decoded_token['sub']  # unique id in cognito
        
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
        # function to log the user out from all devices using access token parameter 
        response = cognito_client.global_sign_out(AccessToken=access_token)
        print("Cognito logout response:", response)  
        return response
    except ClientError as e:
        print(f"Error logging out user: {e}")
        return None

def initiate_password_reset(client_id, email):
    """
    Initiates a password reset by sending an OTP to the user's email.
    """
    try:
        response = cognito_client.forgot_password(
            ClientId=client_id,  # Client ID passed as an argument
            Username=email
        )
        print(f"Password reset initiated for {email}: {response}")
        return response
    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"Error initiating password reset: {error_message}")
        return {'error': error_message}


def confirm_password_reset(client_id, email, otp, new_password):
    """
    Confirms the password reset by validating the OTP and updating the password.
    """
    try:
        response = cognito_client.confirm_forgot_password(
            ClientId=client_id,  # Client ID passed as an argument
            Username=email,
            ConfirmationCode=otp,
            Password=new_password
        )
        print(f"Password reset confirmed for {email}.")
        return response
    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(f"Error confirming password reset: {error_message}")
        return {'error': error_message}