import boto3
from botocore.exceptions import ClientError

def get_ai_model_credentials(realm):
    """
    Retrieves AI model credentials for the specified realm from AWS Secrets Manager.
    :param realm: str - The realm for which to retrieve the AI model credentials.
    :return: dict - The credentials for the AI model.
    """
    secrets_manager_client = boto3.client('secretsmanager')
    try:
        secret_name = f"AI_MODEL_CREDENTIALS_{realm.upper()}"
        get_secret_value_response = secrets_manager_client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error(f"Failed to retrieve AI model credentials: {str(e)}")
        return None

    # Assuming the secret is stored as a JSON string
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)