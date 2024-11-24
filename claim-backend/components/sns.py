import boto3
from botocore.exceptions import ClientError

# Initialize the SNS client
sns_client = boto3.client('sns', region_name='us-east-1')  

def create_sns_topic(topic_name):
    try:
        # check if the topic already exists by listing all topics
        existing_topics = sns_client.list_topics()
        
        # Look for the topic in the list of existing topics
        existing_arns = [topic['TopicArn'] for topic in existing_topics.get('Topics', [])]
        
        # If topic already exists, return the ARN of the existing topic
        for arn in existing_arns:
            if arn.endswith(topic_name):  # Check if the ARN ends with the topic name
                print(f"SNS topic '{topic_name}' already exists with ARN: {arn}")
                return arn

        # function to create sns topic if the topic doesn't exist using parameters name
        response = sns_client.create_topic(
            Name=topic_name
        )
        
        # extract the ARN of the newly created topic
        topic_arn = response['TopicArn']
        print(f"SNS topic '{topic_name}' created successfully with ARN: {topic_arn}")
        return topic_arn
    
    except ClientError as e:
        print(f"Error creating SNS topic: {e}")
        return None
