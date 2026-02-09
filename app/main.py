from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import tempfile
import os
from dotenv import load_dotenv

from .config import Config
from .s3_utils import upload_file_to_s3
from .secrets_utils import get_secrets
from .rag import orchestrate_query

#Sets app, config in variables. If it is production, retrieves secrets from Secrets Manager, if not, 
#directly from .env. Later the 2 endpoints: Upload, which creates temporary file, reads contents from 
#file and fetches, uploads to S3. Query, receives query, ensembles it with whether to use web, 
#config and secrets. Returns results

load_dotenv()

app = FastAPI(title="Agentic App")
cfg = Config()

if os.getenv("ENV") == "prod":
    secrets = get_secrets(
    cfg.AWS_SECRET_NAME,
    region_name=cfg.AWS_REGION
    )
else:
    secrets = {
        "pinecone_api_key": os.getenv("pinecone_api_key"),
        "APP_ENV": os.getenv("APP_ENV"),
        "S3_BUCKET": os.getenv("S3_BUCKET"),
        "DYNAMO_TABLE" : os.getenv("DYNAMO_TABLE"),
        "PINECONE_DIM": os.getenv("PINECONE_DIM"),
        "EMBED_MODEL": os.getenv("EMBED_MODEL"),
        "AWS_SECRET_NAME": os.getenv("AWS_SECRET_NAME"),
        "AWS_REGION": os.getenv("AWS_SECRET_NAME"),
        "SQS_URL": os.getenv("SQW_URL"),
#Just4Local
        "aws_access_key_id": os.getenv("aws_access_key_id"),
        "aws_secret_access_key": os.getenv("aws_secret_access_key"),
        "google_cx": os.getenv("google_cx"),
        "google_api_key": os.getenv("google_api_key"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...), metadata: str = "{}"):
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        content = await file.read()

        tmp.write(content)
        tmp.flush()

        key = f"uploads/{file.filename}"
        upload_file_to_s3(tmp.name, cfg.S3_BUCKET, key)

        return {
            "status": "uploaded",
            "s3_key": key
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class QueryIn(BaseModel):
    question: str
    use_web: bool = False


@app.post("/query")
async def query(q: QueryIn):
    result = orchestrate_query(
        q.question,
        use_web=q.use_web,
        cfg=cfg,
        secrets=secrets
    )
    return result
