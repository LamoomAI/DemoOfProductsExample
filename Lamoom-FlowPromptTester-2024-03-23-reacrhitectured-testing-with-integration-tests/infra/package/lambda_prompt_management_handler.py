import json
import os
from common.locallogging import setup_logging, setup_logging_for_event
from common.utils import try_except, get_trace_id_from_event
from modules.behavior_service import create_behavior, read_behavior, update_behavior, delete_behavior
from common.errors import OperationError

metrics_namespace = 'lambda_prompt_management_handler'
logger = setup_logging(metrics_namespace)

class OperationResult:
    def __init__(self, success, message, data=None):
        self.success = success
        self.message = message
        self.data = data

@try_except
def parse_event(event):
    logger.info("Parsing the incoming event.")
    parsed_event = {'operation': None, 'data': {}}
    http_method = event.get('httpMethod')
    operation_mapping = {
        'GET': 'read',
        'POST': 'create',
        'PUT': 'update',
        'DELETE': 'delete'
    }
    parsed_event['operation'] = operation_mapping.get(http_method)
    if parsed_event['operation'] is None:
        logger.error(f"Unsupported HTTP method: {http_method}")
        raise ValueError(f"Unsupported HTTP method: {http_method}")
    if http_method in ['POST', 'PUT']:
        try:
            parsed_event['data'] = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON body: {e}")
            raise ValueError("Invalid JSON in the request body.")
    elif http_method == 'GET':
        parsed_event['data'] = {
            'queryStringParameters': event.get('queryStringParameters', {}),
            'pathParameters': event.get('pathParameters', {})
        }
    elif http_method == 'DELETE':
        parsed_event['data'] = {'pathParameters': event.get('pathParameters', {})}
    logger.info(f"Parsed event: {parsed_event}")
    return parsed_event

@try_except
def handle_operation(parsed_event):
    operation = parsed_event['operation']
    data = parsed_event['data']
    result = None
    try:
        if operation == 'create':
            result = create_behavior(data)
        elif operation == 'read':
            result = read_behavior(data)
        elif operation == 'update':
            result = update_behavior(data)
        elif operation == 'delete':
            result = delete_behavior(data)
        else:
            raise OperationError(f"Unsupported operation: {operation}")
        logger.info(f"Operation {operation} completed with result: {result}")
        if result['success']:
            return OperationResult(success=True, message="Operation successful.", data=result.get('data'))
        else:
            return OperationResult(success=False, message=result.get('message'))
    except Exception as e:
        logger.error(f"Error during operation {operation}: {e}")
        raise OperationError(f"Error during operation {operation}: {e}")

@try_except
def construct_response(operation_result):
    logger.info("Constructing the response based on the operation result.")
    status_code = 200 if operation_result.success else 400
    response_body = {
        'message': operation_result.message,
        'data': operation_result.data if operation_result.data is not None else {}
    }
    response_body_json = json.dumps(response_body)
    response = {
        'statusCode': status_code,
        'body': response_body_json
    }
    logger.info(f"Constructed response: {response}")
    return response

@try_except
def lambda_handler(event, context):
    setup_logging_for_event(event, metrics_namespace)
    
    if 'RequestType' in event:
        handle_custom_resource_event(event)
        return

    parsed_event = parse_event(event)
    operation_result = handle_operation(parsed_event)
    response = construct_response(operation_result)
    return response

def handle_custom_resource_event(event):
    request_type = event['RequestType']
    if request_type == 'Create':
        pass
    elif request_type == 'Update':
        pass
    elif request_type == 'Delete':
        pass
    else:
        raise ValueError(f"Unsupported request type: {request_type}")

    logger.info(f"Handled custom resource event: {request_type}")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Custom resource event handled successfully."})
    }