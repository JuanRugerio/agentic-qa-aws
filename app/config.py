import os
from dotenv import load_dotenv

# Load .env from project root
#Different configurable variables
load_dotenv()

class Config:
    AWS_SECRET_NAME = os.getenv("AWS_SECRET_NAME", "agentic-app/credentials")
    APP_ENV = os.getenv("APP_ENV", "dev")
    AWS_REGION = os.getenv("AWS_REGION")

    S3_BUCKET = os.getenv("S3_BUCKET")
    DYNAMO_TABLE = os.getenv("DYNAMO_TABLE")

    PINECONE_INDEX = os.getenv("PINECONE_INDEX")
    PINECONE_DIM = int(os.getenv("PINECONE_DIM", 384))

    EMBED_MODEL = os.getenv("EMBED_MODEL")
    OPENAI_MODEL= os.getenv("OPENAI_MODEL")





