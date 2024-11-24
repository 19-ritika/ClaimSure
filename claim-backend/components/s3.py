import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

# Initialize an S3 client 
s3_client = boto3.client('s3', region_name='us-east-1')

bucket_name = "claimsure-app-bucket-cpp" #defining the bucket name


def create_s3_bucket(bucket_name, region=None):
    # function to create s3 bucket using parameters bucket, createbucketconfiguration
    try:
        # Check if the bucket already exists
        s3_client.head_bucket(Bucket=bucket_name)
        return f"Bucket '{bucket_name}' already exists."
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # If the bucket does not exist, create it
            if region is None:
                region = 'us-east-1'
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': region #specify region for bucket
                    }
                )
            return f"Bucket '{bucket_name}' created successfully."
        else:
            return f"Error checking bucket: {e.response['Error']['Message']}"

def upload_file_to_s3(user_id, claim_id, file):
    try:
        # secure the filename and create a unique file key
        filename = secure_filename(file.filename)
        file_key = f"{user_id}/{claim_id}/{filename}"

        # function to Upload the file to the S3 bucket
        s3_client.upload_fileobj(file, bucket_name, file_key)

        # Construct the file URL
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"

        return file_url
    except ClientError as e:
        raise Exception(f"Error uploading file to S3: {e}")
    
def generate_presigned_url(user_id, claim_id, filename, expiration=3600):
    """Generate a pre-signed URL to access an S3 object"""
    try:
        # Construct the S3 object key (path)
        file_key = f"{user_id}/{claim_id}/{filename}"
        
        # Generate the pre-signed URL
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name, 'Key': file_key},
                                                    ExpiresIn=expiration)
        return response
    except ClientError as e:
        raise Exception(f"Error generating presigned URL: {e}")