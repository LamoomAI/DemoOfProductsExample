import logging
import json
from src.tracing import setup_logging
from src.utils import try_except, authenticate, parse_change_request

logger = logging.getLogger()

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    # Extract the authorization header from the event
    authorization_header = event.get('headers', {}).get('Authorization', '')
    # Authenticate the request
    auth_result = authenticate(authorization_header)
    if 'user_id' in auth_result:
        # Parse the change request
        change_request = parse_change_request(event['body'])
        # Proceed with the rest of the lambda logic
        results = {}
        return {"statusCode": 200, "body": json.dumps(results)}
    else:
        # Return the error response from authentication
        return auth_result