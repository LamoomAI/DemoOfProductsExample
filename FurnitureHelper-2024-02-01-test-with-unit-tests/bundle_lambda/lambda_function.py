import logging
import json
from src.tracing import setup_logging
from src.utils import authenticate, try_except

logger = logging.getLogger()

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    
    # Extract the authorization header from the event
    authorization_header = event.get('headers', {}).get('Authorization', '')
    
    # Authenticate the request
    user = authenticate(authorization_header)
    logger.info(f"Authenticated user: {user['user_id']}")
    
    results = {}
    return {"statusCode": 200, "body": json.dumps(results)}