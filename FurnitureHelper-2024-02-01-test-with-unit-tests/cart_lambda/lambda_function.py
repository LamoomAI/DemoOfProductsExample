import logging
import json
from src.tracing import setup_logging
from src.utils import try_except, authenticate_user, get_bundle_id

logger = logging.getLogger()

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    user = authenticate_user(event)
    bundle_id = get_bundle_id(event)
    results = {}
    # code to use the bundle_id
    return {"statusCode": 200, "body": json.dumps(results)}