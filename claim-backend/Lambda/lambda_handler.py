import json
import boto3
from components.utilities.email_report import generate_email_report  # Import your utility function

# Initialize SNS client
sns_client = boto3.client('sns', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Lambda function triggered by DynamoDB Stream.
    It processes the event, generates an email report, and sends it via SNS.
    """

    # Iterate through the records in the DynamoDB Stream event
    for record in event['Records']:
        if record['eventName'] == 'INSERT':  # Process only INSERT events (for new claims)
            new_item = record['dynamodb']['NewImage']

            # Extract necessary information from the new DynamoDB item
            claim_id = new_item['ClaimID']['S']
            user_id = new_item['UserID']['S']
            claim_title = new_item['ClaimTitle']['S']
            claim_details = new_item['ClaimDetails']['S']

            # Generate the email report
            email_body = generate_email_report(claim_id, claim_title, claim_details)

            # Publish the email report to an SNS topic
            sns_topic_arn = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:YourSNSTopic'  # Replace with your SNS ARN
            sns_response = sns_client.publish(
                TopicArn=sns_topic_arn,
                Subject=f'Claim Submitted: {claim_title}',
                Message=email_body
            )
            print(f"Email sent to SNS: {sns_response}")

    return {
        'statusCode': 200,
        'body': json.dumps('Lambda function processed the DynamoDB Stream event successfully')
    }
