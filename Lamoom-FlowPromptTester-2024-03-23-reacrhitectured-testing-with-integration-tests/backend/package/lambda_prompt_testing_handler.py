
import json
from common.locallogging import setup_logging, setup_logging_for_event

from common.utils import try_except

metrics_namespace = 'lambda_prompt_testing_handler'
logger = setup_logging(metrics_namespace)

@try_except
def lambda_handler(event, context):
    setup_logging_for_event(event, metrics_namespace)
    results = {}
    return {"statusCode": 200, "body": json.dumps(results)}
