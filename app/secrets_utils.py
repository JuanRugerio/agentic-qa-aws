import boto3
import json

#PULLS OUT SECRET FROM SECRETS MANAGER
def get_secrets(secret_name, region_name=None):
    """Fetch secret JSON from AWS Secrets Manager and return as dict."""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    resp = client.get_secret_value(SecretId=secret_name)
    secret_string = resp.get("SecretString")
    return json.loads(secret_string)