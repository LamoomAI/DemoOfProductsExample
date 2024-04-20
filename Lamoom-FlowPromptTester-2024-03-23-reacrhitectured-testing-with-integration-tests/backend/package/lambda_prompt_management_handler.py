import json
import uuid
from common.locallogging import setup_logging, setup_logging_for_event
from common.utils import try_except
from modules.behavior_service import create_behavior, read_behavior, update_behavior, delete_behavior
from common.errors import OperationError

metrics_namespace = 'lambda_prompt_management_handler'
logger = setup_logging(metrics_namespace)

@try_except
def lambda_handler(event, context):
    return main(event, context)

@try_except
def main(event, context):
    """
    Entry point for the lambda function, orchestrates the CRUD operations.
    :param event: AWS Lambda event object.
    :param context: AWS Lambda context object.
    :return: CRUDResponse object with the outcome of the operation.
    """
    # Extract or generate a trace_id for logging and correlation
    trace_id = event.get('trace_id', str(uuid.uuid4()))
    logger.info(f"Trace ID: {trace_id} - Received event: {event}")

    # Set up logging with trace_id for the current event
    setup_logging_for_event(event, metrics_namespace, trace_id)

    # Parse the incoming event to determine the operation and extract relevant data
    parsed_event = parse_event(event)
    logger.info(f"Trace ID: {trace_id} - Parsed event: {parsed_event}")

    # Handle the CRUD operation based on the parsed event
    operation_result = handle_operation(parsed_event)
    logger.info(f"Trace ID: {trace_id} - Operation result: {operation_result}")

    # Construct the response object
    response = {
        'statusCode': 200 if operation_result.success else 400,
        'body': json.dumps({
            'success': operation_result.success,
            'message': operation_result.message,
            'data': operation_result.data,
            'trace_id': trace_id
        }),
        'headers': {
            'Content-Type': 'application/json',
            'X-Trace-ID': trace_id
        }
    }

    # Log the response with trace_id
    logger.info(f"Trace ID: {trace_id} - Response: {response}")

    return response

# Additional functions like parse_event and handle_operation would be defined here