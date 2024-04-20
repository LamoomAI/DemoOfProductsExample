import os
import boto3
from botocore.exceptions import ClientError

DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')

def get_secret(secret_name):
    region_name = os.getenv('AWS_REGION')

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            return get_secret_value_response['SecretBinary']

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or get_secret('OpenAiApiKeySecretName')