import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timezone
from claims_lib  import calculate_due_date
from claims_lib import get_submission_date


# Initialize the DynamoDB client
dynamodb_client = boto3.client('dynamodb', region_name='us-east-1') 

# function to create DynamoDB table
def create_table(table_name):
    try:
        # check if the table already exists
        existing_tables = dynamodb_client.list_tables()["TableNames"]
        if table_name in existing_tables:
            print(f"Table '{table_name}' already exists.")
            return

        # function to create the table if it does not exist using parameters 
        # tablename, attributedefinitions, keyschema, billingmode, streamspecification
        response = dynamodb_client.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {
                    'AttributeName': 'UserID',  
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'ClaimID', 
                    'AttributeType': 'S'
                } 
            ],
            KeySchema=[
                {
                    'AttributeName': 'UserID',
                    'KeyType': 'HASH'  # partition key to organize claims data per user
                },
                {
                    'AttributeName': 'ClaimID',
                    'KeyType': 'RANGE'  # sort key to uniquely identify the claims
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # pay per request for unpredictable workloads
            StreamSpecification={
                'StreamEnabled': True,        # indicates if Dynamodb streams is to be enabled
                'StreamViewType': 'NEW_IMAGE'  # captures the entire item after modified written to the stream
            }
        )
        
        print(f"Table '{table_name}' created successfully.")
    except ClientError as e:
        print(f"Error creating table: {e}")


# function to insert a claim into DynamoDB
def add_claim_to_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details, file_url):
    try:
        # importing functions from published library
        submission_date = get_submission_date()
        due_date = calculate_due_date(30)

        # claim details for dynamodb
        claim_item = {
            'UserID': {'S': user_id},
            'ClaimID': {'S': claim_id},
            'ClaimTitle': {'S': claim_title},
            'ClaimType': {'S': claim_type},
            'ClaimDetails': {'S': claim_details},
            'FileURL': {'S': file_url if file_url else ''},  # use anempty string if no file uploaded
            'submission_date': {'S': submission_date},  
            'due_date': {'S': due_date}                
        }

        # insert the claim into the DynamoDB table
        table_name = "ClaimsTable"  # to be matched with actual dynamodb table name
        # function to put or insert in dynamodb using parameters tablename and item
        response = dynamodb_client.put_item(
            TableName=table_name,
            Item=claim_item
        )

        print(f"Claim with ClaimID {claim_id} added to DynamoDB.")
        return response

    except ClientError as e:
        print(f"Error inserting claim: {e}")
        raise Exception(f"Error inserting claim: {e}")

# function to fetch claims by UserID
def get_claims_by_user_id(user_id):
    try:
        # function to scan the table for items where the UserID matches the given user_id using paramters
        # tablename, filterexpressions, expressionattributevalues
        response = dynamodb_client.scan(
            TableName="ClaimsTable",  
            FilterExpression="UserID = :user_id",  # filter for user_id that dynamodb applies after the scan
            ExpressionAttributeValues={':user_id': {'S': user_id}}  # value that can be substituted :user_id with actual value
        )

         # process claims to add submission_date and due_date as strings
        claims = response.get('Items', [])
        for claim in claims:
            claim['submission_date'] = claim.get('submission_date', {}).get('S', "N/A")
            claim['due_date'] = claim.get('due_date', {}).get('S', "N/A")


        
        return claims

    except ClientError as e:
        print(f"Error fetching claims from DynamoDB: {e}")
        raise Exception(f"Error fetching claims: {e}")
    
# function to update a claim in DynamoDB
def update_claim_in_dynamoDB(user_id, claim_id, claim_title, claim_type, claim_details):
    try:
        table_name = "ClaimsTable"  # to be matched with actual dynamodb table name
        # function to update a claim in dynamodb using parameters
        # tablename, key, updateexpressions and expressionattributevalues
        response = dynamodb_client.update_item(
            TableName=table_name,
            Key={
                'UserID': {'S': user_id},
                'ClaimID': {'S': claim_id}
            },
            UpdateExpression="SET ClaimTitle = :title, ClaimType = :type, ClaimDetails = :details",
            ExpressionAttributeValues={    #substitute token with actual values
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


# function to delete a claim from DynamoDB
def delete_claim_from_dynamoDB(user_id, claim_id):
    try:
        table_name = "ClaimsTable"  # to be matched with actual dynamodb table name
        # function to delete a claim in dynamodb using parameters tablename and key
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

# initialize the Lambda client for interacting with AWS Lambda
lambda_client = boto3.client('lambda', region_name='us-east-1')

#function to map dynamodb stream to lambda function
def create_event_source_mapping(function_name, table_name):
    try:
        # Get the stream ARN for the table for event source mapping
        response = dynamodb_client.describe_table(TableName=table_name)
        
        if 'Table' not in response or 'LatestStreamArn' not in response['Table']:
            print("No stream ARN found, ensure the stream is enabled.")
            return
        
        stream_arn = response['Table']['LatestStreamArn']
        
        # create event source mapping for DynamoDB stream to trigger the Lambda function
        event_source_mapping = lambda_client.create_event_source_mapping(
            EventSourceArn=stream_arn,
            FunctionName=function_name,
            Enabled=True,
            BatchSize=100,  # maximum records in one batch
            StartingPosition='TRIM_HORIZON'  # set the starting position to the latest
        )
        
        print(f"Event source mapping created successfully: {event_source_mapping}")
    except Exception as e:
        print(f"Error creating event source mapping: {str(e)}")