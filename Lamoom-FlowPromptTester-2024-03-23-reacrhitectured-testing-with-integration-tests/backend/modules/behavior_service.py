import boto3
import logging
import requests
from common.errors import CustomError
from boto3.dynamodb.conditions import Key
from common.constants import AZURE_OPENAI_KEYS, OPENAI_ORG, OPENAI_API_KEY

PROMPTS_TABLE_NAME = "Prompts"
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
        pass

    def create_behavior(self, behavior_data):
        pass

    def get_behavior(self, behavior_id):
        pass

    def update_behavior(self, behavior_id, behavior_data):
        pass

    def delete_behavior(self, behavior_id):
        pass

def load_behavior_config(behavior_name: str) -> BehaviorConfig:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(BEHAVIORS_TABLE_NAME)

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

def invoke_ai_model(ai_model_request: dict) -> AIModelResponse:
    try:
        prompt_text = ai_model_request['prompt_text']
        context_text = ai_model_request['context_text']
        behavior_name = ai_model_request['behavior_name']

        behavior_config = load_behavior_config(behavior_name)
        ai_model_details = behavior_config.get_ai_model_details()

        ai_model_endpoint = AZURE_OPENAI_KEYS[ai_model_details.realm]['url']
        ai_model_key = AZURE_OPENAI_KEYS[ai_model_details.realm]['key']

        headers = {
            'Authorization': f'Bearer {ai_model_key}',
            'OpenAI-Organization': OPENAI_ORG,
            'Content-Type': 'application/json'
        }

        body = {
            'prompt': prompt_text,
            'max_tokens': ai_model_details.max_tokens,
            'support_functions': ai_model_details.support_functions
        }

        response = requests.post(ai_model_endpoint, headers=headers, json=body)

        if response.status_code != 200:
            raise CustomError(f"AI model invocation failed with status code: {response.status_code}", status_code=response.status_code)

        response_content = response.json()
        ai_response_content = response_content.get('choices', [{}])[0].get('text', '')

        return AIModelResponse(content=ai_response_content)

    except CustomError as e:
        logger.error(f"Failed to invoke AI model: {e}")
        raise e
    except Exception as e:
        logger.exception(f"An unexpected error occurred while invoking the AI model: {e}")
        raise CustomError("Failed to invoke AI model due to an unexpected error.", status_code=500)