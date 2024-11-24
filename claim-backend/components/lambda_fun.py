import boto3
import zipfile
import os
import io
from botocore.exceptions import ClientError

# Initialize the Boto3 clients
lambda_client = boto3.client('lambda')
sns_client = boto3.client('sns', region_name='us-east-1')  # Specify region if needed

# Lambda function code as a string (This includes SNS integration and email report generation)
lambda_code = """
import json
import boto3
from sns import create_sns_topic  # Import the function from sns.py
from utilities.email_report import generate_email_report  # Import utility function

# Initialize SNS client
sns_client = boto3.client('sns', region_name='us-east-1')  # Adjust region if necessary

def lambda_handler(event, context):
    # Iterate through the records in the DynamoDB Stream event
    for record in event['Records']:
        if record['eventName'] == 'INSERT':  # Process only INSERT events (for new claims)
            new_item = record['dynamodb']['NewImage']

            # Extract necessary information from the new DynamoDB item
            claim_data = {
                'ClaimID': new_item['ClaimID']['S'],
                'UserID': new_item['UserID']['S'],
                'ClaimTitle': new_item['ClaimTitle']['S'],
                'ClaimDetails': new_item['ClaimDetails']['S'],
                'SubmissionDate': new_item.get('SubmissionDate', {}).get('S', 'N/A'),
                'DueDate': new_item.get('DueDate', {}).get('S', 'N/A')
            }

            # Generate the email report by passing the claim_data as a dictionary
            email_report = generate_email_report(claim_data)

            # Use the create_sns_topic function to get the SNS topic ARN
            topic_name = 'ClaimSubmissionTopic'  # Replace with your actual SNS topic name
            sns_topic_arn = create_sns_topic(topic_name)

            if sns_topic_arn:
                # Publish the email report to the SNS topic
                sns_response = sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Subject=email_report['subject'],
                    Message=email_report['body'],
                    MessageAttributes={
                        'UserID': {
                            'DataType': 'String',
                            'StringValue': claim_data['UserID']  # Attach the UserID as a message attribute
                        }
                    }
                )
                print(f"Email sent to SNS: {sns_response}")
            else:
                print("Error: SNS topic ARN could not be retrieved")

    return {
        'statusCode': 200,
        'body': json.dumps('Lambda function processed the DynamoDB Stream event successfully')
    }
"""

def get_lambda_zip_bytes():
    """
    Creates an in-memory zip file containing the Lambda function code and all required components.
    """
    # Create an in-memory bytes buffer
    buffer = io.BytesIO()

    # Create a zip file and add the lambda code and necessary components
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the lambda function code to the root of the zip file
        zip_file.writestr('lambda_function.py', lambda_code)

        # Add the components directory and its contents (including sns.py and email_report.py)
        components_dir = 'components'
        for folder_name, subfolders, filenames in os.walk(components_dir):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                # Write the file with the correct relative path
                zip_file.write(file_path, os.path.relpath(file_path, components_dir))

    # Get the byte content of the zip file
    buffer.seek(0)
    return buffer.read()


def create_lambda_function(function_name, role_arn, handler):
    # create a lambda function
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        return f"Lambda function '{function_name}' already exists."
    except ClientError as e:
        # when the function does not exist
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # retrieve the deployment package (zip file)
            zip_bytes = get_lambda_zip_bytes()

            # Create the Lambda function using the paramters 
            #functionname, runtime, role, handler, code, description, timeout and memorysize
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.8',  # Adjust to the correct runtime
                Role=role_arn,
                Handler=handler,  # Use the handler provided
                Code={'ZipFile': zip_bytes},
                Description='Lambda function to process claims and send emails',
                Timeout=30,
                MemorySize=128
            )

            return f"Lambda function '{function_name}' created successfully."
        else:
            return f"Error creating Lambda function: {e.response['Error']['Message']}"
