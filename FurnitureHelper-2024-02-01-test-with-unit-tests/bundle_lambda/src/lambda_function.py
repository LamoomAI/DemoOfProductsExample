import logging
import json
from src.tracing import setup_logging, get_trace_id
from src.utils import authenticate, try_except, parse_input
from src.search import query_opensearch
from src.bundle import generate_bundles
from src.errors import ValidationError

logger = logging.getLogger()

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    
    authorization_header = event.get('headers', {}).get('Authorization', '')
    
    user = authenticate(authorization_header)
    logger.info(f"Authenticated user: {user.user_id}")
    
    body = event.get("body")
    if not body:
        raise ValidationError("Missing request body")
    
    input_data = parse_input(body)
    layout_id = input_data['LayoutID']
    user_preferences = input_data['UserPreferences']
    logger.info(f"Received layout ID: {layout_id} and user preferences: {user_preferences}")
    
    trace_id = get_trace_id(event)
    user_preferences.trace_id = trace_id
    
    furniture_items = query_opensearch(layout_id, user_preferences)
    
    bundles = generate_bundles(furniture_items, user_preferences)
    
    return {
        'statusCode': 200,
        'body': json.dumps({'bundles': bundles})
    }