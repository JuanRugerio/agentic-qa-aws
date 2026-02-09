import boto3
#S3 CLIENT, FUNCTION TO UPLOAD FILE TO BUCKET. FUNCTION TO DOWNLOAD FILE FROM S3

s3 = boto3.client('s3')


def upload_file_to_s3(local_path, bucket, key):
    s3.upload_file(local_path, bucket, key)


def download_file_from_s3(bucket, key, local_path):
    s3.download_file(bucket, key, local_path)