from flask import Flask, send_from_directory
from flask_cors import CORS
from Routes.cognito_routes import cognito_routes
from Routes.claim_routes import claim_routes
from components.cognito import create_user_pool, create_app_client
from components.dynamoDB import create_table, create_event_source_mapping
from components.s3 import create_s3_bucket
from components.lambda_fun import create_lambda_function
from components.sns import create_sns_topic
import os

# create flask app to build static files
app = Flask(__name__, static_folder='build')

# enable (CORS) for front end and backend communication
CORS(app)

# create Cognito resources user pool to manage user authentication when app starts
user_pool_name = "claimSure-user-pool"
user_pool_id = create_user_pool(user_pool_name)
app_client_id = create_app_client(user_pool_id, "my_app_client")

# create DynamoDB table if it doesn't exist to store claims data
table_name = "ClaimsTable"
create_table(table_name)

# create S3 bucket for storing uploaded files
bucket_name = "claimsure-app-bucket-cpp"
response = create_s3_bucket(bucket_name)
print(response)

topic_arn = create_sns_topic("ClaimSubmissionTopic")

# setup Lambda function 
function_name = "claimsure-email-report"
role_arn = "arn:aws:iam::298550657963:role/LabRole"  # permission for making Lambda work
handler = "lambda_function.lambda_handler"  # lambda handler function 

# create the Lambda function 
lambda_response = create_lambda_function(function_name, role_arn, handler)
if lambda_response:
    print("Lambda function created successfully.")
else:
    print("Failed to create Lambda function.")

# connecting Lambda with Dynamodb table
create_event_source_mapping("claimsure-email-report", "ClaimsTable")

# register routes for Cognito and Claim 
app.register_blueprint(cognito_routes, url_prefix='/auth')
app.register_blueprint(claim_routes, url_prefix='/claims')

# serve the react static files to start frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # check if the requested file exists in the build folder, serve it
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # if file does not exist, serve the index.html for all other requests
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
