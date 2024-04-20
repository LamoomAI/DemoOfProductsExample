import boto3
import logging
from common.errors import CustomError

# Define the logger for this module
logger = logging.getLogger(__name__)

def retrieve_ai_model_keys() -> dict:
    """
    Retrieves AI Model keys from AWS Secrets Manager.

    :return: A dictionary containing the AI Model keys.
    :raises CustomError: If the keys cannot be retrieved.
    """
    secrets_manager_client = boto3.client('secretsmanager')
    keys = ['AZURE_OPENAI_KEYS', 'OPENAI_ORG', 'OPENAI_API_KEY']
    retrieved_keys = {}

    for key in keys:
        try:
            # Fetch the secret value from Secrets Manager
            secret_value = secrets_manager_client.get_secret_value(SecretId=key)
            # Extract the secret string and convert it to a dictionary
            secret_dict = secret_value.get('SecretString', '{}')
            retrieved_keys[key] = secret_dict
            logger.info(f"Retrieved secret for key: {key}")
        except secrets_manager_client.exceptions.ResourceNotFoundException:
            logger.error(f"Secret {key} not found in Secrets Manager.")
            raise CustomError(f"Secret {key} not found.", status_code=404)
        except Exception as e:
            logger.exception(f"An error occurred while retrieving secret {key}: {e}")
            raise CustomError("Failed to retrieve AI Model keys due to an unexpected error.", status_code=500)

    return retrieved_keys