import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from claims_lib  import calculate_due_date
from claims_lib import get_submission_date
# from components.utilities.submission_date import get_submission_date
# from components.utilities.due_date import calculate_due_date

# Initialize the DynamoDB client
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')  # Adjust the region as needed

# Create DynamoDB table
def create_table(table_name):
    try:
        # Check if the table already exists
        existing_tables = dynamodb_client.list_tables()["TableNames"]
        if table_name in existing_tables:
            print(f"Table '{table_name}' already exists.")
            return

        # Create the table with On-Demand Capacity Mode
        response = dynamodb_client.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'UserID',  # Partition key
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'ClaimID',  # Sort key
                    'AttributeType': 'S'
                } 
            ],
            KeySchema=[
                {
                    'AttributeName': 'UserID',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'ClaimID',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-Demand Mode
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': 'NEW_IMAGE'  # Captures the new image of the item
            }
        )
        
        print(f"Table '{table_name}' created successfully.")
    except ClientError as e:
        print(f"Error creating table: {e}")


# Function to insert a claim into DynamoDB
def add_claim_to_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details, file_url):
    try:
        submission_date = get_submission_date()
        due_date = calculate_due_date(30)

        # Prepare the item to insert
        claim_item = {
            'UserID': {'S': user_id},
            'ClaimID': {'S': claim_id},
            'ClaimTitle': {'S': claim_title},
            'ClaimType': {'S': claim_type},
            'ClaimDetails': {'S': claim_details},
            'FileURL': {'S': file_url if file_url else ''},  # Handle missing file_url (in case no file was uploaded)
            'submission_date': {'S': submission_date},  # Wrapped in DynamoDB format
            'due_date': {'S': due_date}                # Wrapped in DynamoDB format
        }

        # Insert the claim into the DynamoDB table
        table_name = "ClaimsTable"  # Ensure this matches your actual DynamoDB table name
        response = dynamodb_client.put_item(
            TableName=table_name,
            Item=claim_item
        )

        print(f"Claim with ClaimID {claim_id} added to DynamoDB.")
        return response

    except ClientError as e:
        print(f"Error inserting claim: {e}")
        raise Exception(f"Error inserting claim: {e}")

# Function to fetch claims by UserID
def get_claims_by_user_id(user_id):
    try:
        # Scan the table for items where the UserID matches the provided user_id
        response = dynamodb_client.scan(
            TableName="ClaimsTable",  # Ensure this matches your actual DynamoDB table name
            FilterExpression="UserID = :user_id",  # Filter for UserID
            ExpressionAttributeValues={':user_id': {'S': user_id}}  # The value for :user_id
        )

         # Process claims to add submission_date and due_date as strings
        claims = response.get('Items', [])
        for claim in claims:
            claim['submission_date'] = claim.get('submission_date', {}).get('S', "N/A")
            claim['due_date'] = claim.get('due_date', {}).get('S', "N/A")


        # Return the items (claims) found
        return claims

    except ClientError as e:
        print(f"Error fetching claims from DynamoDB: {e}")
        raise Exception(f"Error fetching claims: {e}")
    
# Function to update a claim in DynamoDB
def update_claim_in_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details):
    try:
        table_name = "ClaimsTable"  # Ensure this matches your actual DynamoDB table name
        response = dynamodb_client.update_item(
            TableName=table_name,
            Key={
                'UserID': {'S': user_id},
                'ClaimID': {'S': claim_id}
            },
            UpdateExpression="SET ClaimTitle = :title, ClaimType = :type, ClaimDetails = :details",
            ExpressionAttributeValues={
                ':title': {'S': claim_title},
                ':type': {'S': claim_type},
                ':details': {'S': claim_details}
            }
        )
        print(f"Claim with ClaimID {claim_id} updated successfully.")
        return response

    except ClientError as e:
        print(f"Error updating claim: {e}")
        raise Exception(f"Error updating claim: {e}")


# Function to delete a claim from DynamoDB
def delete_claim_from_dynamoDB(user_id, claim_id):
    try:
        table_name = "ClaimsTable"  # Ensure this matches your actual DynamoDB table name
        response = dynamodb_client.delete_item(
            TableName=table_name,
            Key={
                'UserID': {'S': user_id},
                'ClaimID': {'S': claim_id}
            }
        )
        print(f"Claim with ClaimID {claim_id} deleted successfully.")
        return response

    except ClientError as e:
        print(f"Error deleting claim: {e}")
        raise Exception(f"Error deleting claim: {e}")
    
lambda_client = boto3.client('lambda', region_name='us-east-1')

def create_event_source_mapping(function_name, table_name):
    try:
        # Get the stream ARN for the table
        response = dynamodb_client.describe_table(TableName=table_name)
        
        if 'Table' not in response or 'LatestStreamArn' not in response['Table']:
            print("No stream ARN found, ensure the stream is enabled.")
            return
        
        stream_arn = response['Table']['LatestStreamArn']
        
        # Create event source mapping for DynamoDB stream to trigger the Lambda function
        event_source_mapping = lambda_client.create_event_source_mapping(
            EventSourceArn=stream_arn,
            FunctionName=function_name,
            Enabled=True,
            BatchSize=100,  # Adjust batch size based on your need
            StartingPosition='TRIM_HORIZON'  # Set the starting position to TRIM_HORIZON or LATEST
        )
        
        print(f"Event source mapping created successfully: {event_source_mapping}")
    except Exception as e:
        print(f"Error creating event source mapping: {str(e)}")