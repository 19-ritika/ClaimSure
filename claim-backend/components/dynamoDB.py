import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone

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
            BillingMode='PAY_PER_REQUEST'  # On-Demand Mode
        )
        
        print(f"Table '{table_name}' created successfully.")
    except ClientError as e:
        print(f"Error creating table: {e}")


# Function to insert a claim into DynamoDB
def add_claim_to_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details, file_url):
    try:
        # Create a timestamp for the claim submission (UTC time with timezone)
        timestamp = datetime.now(timezone.utc).isoformat()

        # Prepare the item to insert
        claim_item = {
            'UserID': {'S': user_id},
            'ClaimID': {'S': claim_id},
            'ClaimTitle': {'S': claim_title},
            'ClaimType': {'S': claim_type},
            'ClaimDetails': {'S': claim_details},
            'FileURL': {'S': file_url if file_url else ''},  # Handle missing file_url (in case no file was uploaded)
            'Timestamp': {'S': timestamp}
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

        # Return the items (claims) found
        return response.get('Items', [])

    except ClientError as e:
        print(f"Error fetching claims from DynamoDB: {e}")
        raise Exception(f"Error fetching claims: {e}")