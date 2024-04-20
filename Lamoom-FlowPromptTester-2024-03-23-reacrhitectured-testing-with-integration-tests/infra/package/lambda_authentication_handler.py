import json
import os
from common.locallogging import setup_logging, setup_logging_for_event
from common.utils import try_except, get_trace_id_from_event
from modules.cognito_service import exchange_code_for_token
from common.errors import ValidationError
from common.settings import COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID

metrics_namespace = 'lambda_authentication_handler'
logger = setup_logging(metrics_namespace)

class Token:
    def __init__(self, token: str):
        self.token = token

@try_except
def lambda_handler(event, context):
    setup_logging_for_event(event, metrics_namespace)
    
    if 'RequestType' in event:
        handle_custom_resource_event(event)
        return

    try:
        token = validate_token(event)
        return {
            "statusCode": 200,
            "body": json.dumps({"jwt_token": token.token}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    except ValidationError as e:
        logger.error(f"Validation error: {e}", extra={'trace_id': get_trace_id_from_event(event)})
        return {
            "statusCode": e.status_code,
            "body": json.dumps({"message": str(e)}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", extra={'trace_id': get_trace_id_from_event(event)})
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def handle_custom_resource_event(event):
    logger.info(f"Handling custom resource event: {event['RequestType']}")

@try_except
def validate_token(event: dict) -> Token:
    logger = setup_logging_for_event(event, metrics_namespace)
    trace_id = get_trace_id_from_event(event)
    
    code_token = event.get('queryStringParameters', {}).get('code', None)
    if not code_token:
        logger.error(f"Missing 'code' parameter in event", extra={'trace_id': trace_id})
        raise ValidationError("Missing 'code' parameter.", status_code=400)

    try:
        logger.info(f"Exchanging code token for JWT token", extra={'trace_id': trace_id})
        token_response = exchange_code_for_token(code_token)
        jwt_token = token_response.get('jwt_token')
        if not jwt_token:
            logger.error(f"JWT token not received after exchanging code token", extra={'trace_id': trace_id})
            raise ValidationError("JWT token not received after exchanging code token.", status_code=400)
        
        logger.info(f"Successfully exchanged code token for JWT token", extra={'trace_id': trace_id})
        return Token(token=jwt_token)
    except ValidationError as e:
        logger.error(f"Validation error while exchanging code token: {e}", extra={'trace_id': trace_id})
        raise
    except Exception as e:
        logger.error(f"Unexpected error while validating code token: {e}", extra={'trace_id': trace_id})
        raise ValidationError("Unexpected error while validating code token.", status_code=500)