import os
import boto3
from botocore.exceptions import ClientError

TEST_EVENTS_TABLE_NAME = os.environ.get("TEST_EVENTS_TABLE_NAME")
LAST_TEST_EVENTS_TABLE_NAME = os.environ.get("LAST_TEST_EVENTS_TABLE_NAME")
IS_QA_ENV = os.environ.get("IS_QA_ENV", "false").lower() == "true"
BEHAVIORS_TABLE_NAME = os.environ.get("BEHAVIORS_TABLE_NAME")
AI_MODEL_ENDPOINT = os.environ.get("AI_MODEL_ENDPOINT")

def get_secret(secret_name: str) -> str:
    secrets_client = boto3.client('secretsmanager')
    try {
        secret_value = secrets_client.get_secret_value(SecretId=secret_name)
        return secret_value['SecretString']
    } except ClientError as e {
        raise Exception(f"Unable to retrieve secret {secret_name}: " + e.response['Error']['Message'])
    }
}

def get_parameter(parameter_name: str) -> str {
    ssm_client = boto3.client('ssm')
    try {
        parameter = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return parameter['Parameter']['Value']
    } except ClientError as e {
        raise Exception(f"Unable to retrieve parameter {parameter_name}: " + e.response['Error']['Message'])
    }
}

JWT_SECRET_KEY = get_secret('JWTSecretKey')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_DELTA_SECONDS = int(os.environ.get('JWT_EXPIRATION_DELTA_SECONDS', 3600))

COGNITO_USER_POOL_ID = get_parameter('/myapp/cognito_user_pool_id')
COGNITO_CLIENT_ID = get_parameter('/myapp/cognito_client_id')