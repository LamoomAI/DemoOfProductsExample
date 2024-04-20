import logging
import json
from src.tracing import setup_logging
from src.utils import try_except, authenticate_user, get_bundle_id
from src.cart import update_shopping_cart

logger = logging.getLogger()

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    user = authenticate_user(event)
    bundle_id = get_bundle_id(event)
    results = {}
    
    if event.get('action') == 'add_to_cart':
        # Update the shopping cart
        update_status = update_shopping_cart(user, bundle_id)
        
        # Generate a response based on the update status
        response = generate_confirmation_response(update_status)
        
        return response

    return {"statusCode": 200, "body": json.dumps(results)}