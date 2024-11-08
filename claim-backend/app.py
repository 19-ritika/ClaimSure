from flask import Flask
from flask_cors import CORS
from Routes.cognito_routes import cognito_routes
from Routes.claim_routes import claim_routes
from components.cognito import create_user_pool, create_app_client
from components.dynamoDB import create_table  # Import the create_table function
from components.s3 import create_s3_bucket

# Initialize Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS)
CORS(app)

# Create Cognito resources (user pool, app client) on startup
user_pool_name = "claimSure-user-pool"
user_pool_id = create_user_pool(user_pool_name)
app_client_id = create_app_client(user_pool_id, "my_app_client")

# Create DynamoDB table if it doesn't already exist
table_name = "ClaimsTable"
create_table(table_name)

# Create S3 bucket
bucket_name = "claimsure-app-bucket-cpp"
response = create_s3_bucket(bucket_name)
print(response)

# Register cognito and claim routes
app.register_blueprint(cognito_routes, url_prefix='/auth')
app.register_blueprint(claim_routes, url_prefix='/claims')

if __name__ == "__main__":
    app.run(debug=True)
