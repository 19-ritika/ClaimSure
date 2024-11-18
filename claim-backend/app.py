from flask import Flask, send_from_directory
from flask_cors import CORS
from Routes.cognito_routes import cognito_routes
from Routes.claim_routes import claim_routes
from components.cognito import create_user_pool, create_app_client
from components.dynamoDB import create_table, create_event_source_mapping  # Import the create_table function
from components.s3 import create_s3_bucket
from components.lambda_fun import create_lambda_function
from components.sns import create_sns_topic
import os

# Initialize Flask app
app = Flask(__name__, static_folder='build')

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

topic_arn = create_sns_topic("ClaimSubmissionTopic")

# Lambda configuration
function_name = "claimsure-email-report"
role_arn = "arn:aws:iam::298550657963:role/LabRole"  # Replace with your IAM role ARN
handler = "lambda_function.lambda_handler"  # The handler function inside the lambda function

# Create the Lambda function (calls the function from lambda_function.py)
lambda_response = create_lambda_function(function_name, role_arn, handler)
if lambda_response:
    print("Lambda function created successfully.")
else:
    print("Failed to create Lambda function.")

create_event_source_mapping("claimsure-email-report", "ClaimsTable")

# Register Cognito and Claim routes
app.register_blueprint(cognito_routes, url_prefix='/auth')
app.register_blueprint(claim_routes, url_prefix='/claims')

# Serve React static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(f"build/{path}"):
        return send_from_directory('build', path)
    else:
        return send_from_directory('build', 'index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
