import os
import json
import boto3

#ENSEMBLES SQS CLIENT, AND FIXES SQS URL, PULLS BUCKET NAME, KEY, BODY AND SENDS MESSAGE TO SQS
sqs = boto3.client('sqs')
QUEUE_URL = os.getenv('SQS_URL')




def lambda_handler(event, context):
    for rec in event.get('Records', []):
        bucket = rec['s3']['bucket']['name']
        key = rec['s3']['object']['key']
        body = {"bucket": bucket, "key": key}
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(body))
    return {"status": "ok"}