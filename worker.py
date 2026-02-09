import os
import json
import time
import uuid
import boto3
from sentence_transformers import SentenceTransformer
from app.pinecone_utils import init_pinecone
from app.secrets_utils import get_secrets


QUEUE_URL = os.getenv("SQS_URL")
SECRET_NAME = os.getenv("AWS_SECRET_NAME")
DYNAMO_TABLE = os.getenv("DYNAMO_TABLE")
CFG_INDEX = os.getenv("PINECONE_INDEX", "agentic-index")
PINE_DIM = int(os.getenv("PINECONE_DIM", "384"))


sqs = boto3.client('sqs')
s3 = boto3.client('s3')
dynamo = boto3.resource('dynamodb')


secrets = get_secrets(SECRET_NAME)

#SETS PINECONE VARS AND EMBEDDER
pine_idx = init_pinecone(secrets["pinecone_api_key"],CFG_INDEX,PINE_DIM)
embedder = SentenceTransformer(os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))


table = dynamo.Table(DYNAMO_TABLE)


#LOADS MESSAGE BODY, BUCKET, PATH AND DOWNLOADS FROM S3 BUCKET. 

def process_message(msg):
    body = json.loads(msg['Body'])
    bucket = body['bucket']
    key = body['key']
    local_path = f"/tmp/{uuid.uuid4().hex}"
    s3.download_file(bucket, key, local_path)


# Basic text handling: assumes text files. Extend with PDF/DOCX extraction as needed.
    with open(local_path, "r", encoding="utf-8") as f:
        text = f.read()


# Simple chunking and embeds. Appends id, vector, and former text and key as metadata. Upserts to pinecone
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    embeddings = embedder.encode(chunks).tolist()


    vectors = []
    for i, (vec, chunk) in enumerate(zip(embeddings, chunks)):
        vid = f"{os.path.basename(key)}_{i}"
        vectors.append({"id": vid, "values": vec, "metadata": {"text": chunk, "s3_key": key}})


    pine_idx.upsert(vectors=vectors)


# log to dynamo

    doc_id = key  # use S3 object key as the document ID

    table.put_item(
        Item={
            "doc_id": doc_id,          # ✅ REQUIRED partition key
            "s3_key": key,             # optional but useful
            "chunks": len(chunks),
            "ts": int(time.time())
        }
    )
    return True



#PULLS MESSAGES WHILE THERE ARE, PROCESSES MESSAGE, 
def run_loop():
    while True:
        resp = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=1, WaitTimeSeconds=20)
        msgs = resp.get("Messages", [])
        if not msgs:
            time.sleep(2)
            continue
        for m in msgs:
            try:
                process_message(m)
                sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=m['ReceiptHandle'])
            except Exception as e:
                print("processing error:", e)


if __name__ == "__main__":
    run_loop()