import json
import requests
from common.locallogging import setup_logging, setup_logging_for_event
from common.utils import try_except
from common.errors import ValidationError, AIModelInvocationError
from dataclasses import dataclass
from modules.secrets_manager_service import get_ai_model_credentials

metrics_namespace = 'lambda_ai_model_interaction_handler'
logger = setup_logging(metrics_namespace)

@dataclass
class ValidatedRequest:
    prompt_data: str
    context_data: str
    behavior_name: str

def validate_request(event: dict) -> ValidatedRequest:
    """
    Validates the incoming request for required parameters.

    :param event: The incoming event as a dictionary.
    :return: A ValidatedRequest object containing the validated data.
    :raises ValidationError: If any required parameters are missing.
    """
    prompt_data = event.get('prompt_data')
    context_data = event.get('context_data')
    behavior_name = event.get('behavior_name')

    missing_params = [param for param in ["prompt_data", "context_data", "behavior_name"] if event.get(param) is None]
    if missing_params:
        missing_params_str = ", ".join(missing_params)
        logger.error(f"Missing required parameters: {missing_params_str}")
        raise ValidationError(message=f"Missing required parameters: {missing_params_str}")

    logger.info(f"Validated request with prompt_data: {prompt_data[:100]}, context_data: {context_data[:100]}, behavior_name: {behavior_name}")

    return ValidatedRequest(prompt_data=prompt_data, context_data=context_data, behavior_name=behavior_name)

class AIModelResponse:
    def __init__(self, content):
        self.content = content

@try_except
def invoke_ai_model(prompt_data, context_data, AIModelBehavior):
    """
    Invokes the AI Model with the prompt data, context data, and behavior.
    :param prompt_data: str - The prompt data to send to the AI model.
    :param context_data: str - The context data to send to the AI model.
    :param AIModelBehavior: AIModelBehavior - The behavior object defining how to call the AI model.
    :return: AIModelResponse - The response from the AI model.
    """
    # Validate input data
    if not prompt_data or not context_data:
        raise ValueError("Prompt data and context data cannot be empty.")

    # Retrieve AI model credentials
    credentials = get_ai_model_credentials(AIModelBehavior.realm)
    if not credentials:
        raise AIModelInvocationError("Failed to retrieve AI model credentials.")

    # Construct the request payload
    payload = {
        "prompt": prompt_data,
        "context": context_data,
        # Additional parameters can be added here based on AIModelBehavior
    }

    # Send the request to the AI model
    try:
        response = requests.post(
            credentials['url'],
            headers={"Authorization": f"Bearer {credentials['key']}"},
            json=payload
        )
        response.raise_for_status()  # Raise an exception for HTTP error responses
    except requests.exceptions.RequestException as e:
        logger.error(f"AI model invocation failed: {str(e)}")
        raise AIModelInvocationError(f"AI model invocation failed: {str(e)}")

    # Log the request and response for monitoring
    logger.info(f"AI model request payload: {json.dumps(payload)}")
    logger.info(f"AI model response: {response.text}")

    # Return the AI model's response
    return AIModelResponse(content=response.text)

@try_except
def lambda_handler(event, context):
    setup_logging_for_event(event, metrics_namespace)
    validated_request = validate_request(event)
    results = {}
    return {"statusCode": 200, "body": json.dumps(results)}