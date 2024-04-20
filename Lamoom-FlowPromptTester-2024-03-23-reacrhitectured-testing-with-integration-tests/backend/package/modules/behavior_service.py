import boto3
import logging
from common.errors import CustomError
from boto3.dynamodb.conditions import Key

# Assuming PROMPTS_TABLE_NAME is the name of the DynamoDB table where prompts are stored.
# This should be defined in constants.py or settings.py, or you can define it here.
PROMPTS_TABLE_NAME = "Prompts"
# Assuming the context data is stored in a table named 'ContextData'
CONTEXT_DATA_TABLE_NAME = "ContextData"

logger = logging.getLogger(__name__)

class BehaviorConfig:
    def __init__(self, attempts, ai_model):
        self.attempts = attempts
        self.ai_model = ai_model

class AIModelResponse:
    def __init__(self, content):
        self.content = content

class Behavior:
    def __init__(self, name, attempts):
        self.name = name
        self.attempts = attempts

    def get_ai_model_details(self):
        if self.attempts:
            return self.attempts[0].ai_model
        else:
            raise ValueError("Behavior does not contain any attempts.")

class BehaviorService:
    def check_permissions(self, user_info, operation):
        # Implement permission checks here
        pass

    def create_behavior(self, behavior_data):
        # Implement behavior creation here
        pass

    def get_behavior(self, behavior_id):
        # Implement behavior retrieval here
        pass

    def update_behavior(self, behavior_id, behavior_data):
        # Implement behavior update here
        pass

    def delete_behavior(self, behavior_id):
        # Implement behavior deletion here
        pass

def load_behavior_config(behavior_name: str) -> BehaviorConfig:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table( )

    try:
        response = table.query(
            KeyConditionExpression=Key('behavior_name').eq(behavior_name)
        )
        items = response.get('Items', [])
        if not items:
            raise CustomError(f"Behavior configuration for '{behavior_name}' not found.", status_code=404)

        behavior_config_data = items[0].get('config')
        if not behavior_config_data:
            raise CustomError(f"Behavior configuration for '{behavior_name}' is empty.", status_code=404)

        behavior_config = BehaviorConfig(**behavior_config_data)

        logger.info(f"Loaded behavior configuration for '{behavior_name}'.")
        return behavior_config

    except CustomError as e:
        logger.error(f"Failed to load behavior configuration: {e}")
        raise e
    except Exception as e:
        logger.exception(f"An unexpected error occurred while loading behavior configuration: {e}")
        raise CustomError("Failed to load behavior configuration due to an unexpected error.", status_code=500)

def retrieve_prompt_data(prompt_id: str) -> dict:
    """
    Retrieves prompt data from DynamoDB using the prompt_id.

    :param prompt_id: The unique identifier for the prompt.
    :return: A dictionary containing the prompt text.
    :raises CustomError: If the prompt data cannot be retrieved.
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(PROMPTS_TABLE_NAME)

    try:
        logger.info(f"Retrieving prompt data for prompt_id: {prompt_id}")
        response = table.get_item(Key={'prompt_id': prompt_id})
        item = response.get('Item')

        if not item:
            logger.error(f"No prompt data found for prompt_id: {prompt_id}")
            raise CustomError(f"No prompt data found for prompt_id: {prompt_id}", status_code=404)

        prompt_text = item.get('prompt_text')
        logger.info(f"Successfully retrieved prompt data for prompt_id: {prompt_id}")
        return {'prompt_text': prompt_text}

    except CustomError as e:
        logger.error(f"Failed to retrieve prompt data: {e}")
        raise e
    except Exception as e:
        logger.exception(f"An unexpected error occurred while retrieving prompt data: {e}")
        raise CustomError("Failed to retrieve prompt data due to an unexpected error.", status_code=500)

def retrieve_context_data(context_id: str) -> dict:
    """
    Retrieves context data from DynamoDB using the context_id.

    :param context_id: The unique identifier for the context data.
    :return: A dictionary containing the context text.
    :raises CustomError: If the context data cannot be retrieved.
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CONTEXT_DATA_TABLE_NAME)

    try:
        logger.info(f"Retrieving context data for context_id: {context_id}")
        response = table.get_item(Key={'context_id': context_id})
        item = response.get('Item')

        if not item:
            logger.error(f"Context data not found for context_id: {context_id}")
            raise CustomError(f"Context data not found for context_id: {context_id}", status_code=404)

        context_text = item.get('context_text')
        logger.info(f"Successfully retrieved context data for context_id: {context_id}")
        return {'context_text': context_text}

    except CustomError as e:
        logger.error(f"Failed to retrieve context data: {e}")
        raise e
    except Exception as e:
        logger.exception(f"An unexpected error occurred while retrieving context data: {e}")
        raise CustomError("Failed to retrieve context data due to an unexpected error.", status_code=500)