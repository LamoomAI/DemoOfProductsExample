import logging
import json
from src.tracing import setup_logging
from src.utils import try_except, authenticate, parse_change_request, find_replacement_items, update_bundle_in_database, build_response

logger = logging.getLogger()

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    authorization_header = event.get('headers', {}).get('Authorization', '')
    auth_result = authenticate(authorization_header)
    if 'user_id' in auth_result:
        change_request = parse_change_request(json.loads(event['body']))
        replacement_items = find_replacement_items(change_request)
        update_confirmation = update_bundle_in_database(replacement_items)
        response = build_response(update_confirmation)
        return {
            "statusCode": response.status_code,
            "body": json.dumps(response.body)
        }
    else:
        return auth_result