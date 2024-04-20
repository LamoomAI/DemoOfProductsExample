from dataclasses import fields
import enum
import logging
from common.errors import CustomError
from common.metrics import send_metric_to_cloudwatch
from decimal import Decimal
import boto3
from time import time
from botocore.exceptions import ClientError
import json
from common.settings import TEST_EVENTS_TABLE_NAME, LAST_TEST_EVENTS_TABLE_NAME, AWS_LAMBDA_FUNCTION_NAME
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)

def curr_timestamp_in_ms():
    return int(time() * 1000)

def error_response(error: CustomError):
    return {
        "statusCode": error.http_code,
        'headers': get_headers(),
        "error_code": error.error_code
    }

def clean_test_event(event):
    event.pop('headers', None)
    event.pop('multiValueHeaders', None)
    requestContext = event.get('requestContext')
    if requestContext:
        requestContext.pop('identity', None)
    authorizer_keys = list(requestContext.get('authorizer', {}).keys())
    for key in authorizer_keys:
        if key == 'claims':
            keys = list(requestContext['authorizer'][key].keys())
            for claim_key in keys:
                if claim_key.startswith('custom:'):
                    continue
                requestContext['authorizer'][key].pop(claim_key, None)
        else:
            requestContext['authorizer'].pop(key, None)
    event.pop("is_test_event", None)
    body = event.get('body')
    if body:
        try:
            event['body'] = json.loads(body)
        except:
            pass

def save_last_test_event(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LAST_TEST_EVENTS_TABLE_NAME)
    lambda_name = AWS_LAMBDA_FUNCTION_NAME
    is_test_event = event.get("is_test_event")
    http_method = event.get("httpMethod")
    if is_test_event:
        return
    try:
        table.put_item(Item={"lambda_name": lambda_name, "test_case": http_method, "event": event})
    except ClientError as e:
        try:
            table.update_item(
                Key={"lambda_name": lambda_name, "test_case": http_method},
                UpdateExpression="set event = :e",
                ExpressionAttributeValues={":e": event}
            )
        except Exception as e:
            logger.exception(e)
    except Exception as e:
        logger.exception(e)

def save_test_event(event, lambda_response, is_error=False):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TEST_EVENTS_TABLE_NAME)
    lambda_name = AWS_LAMBDA_FUNCTION_NAME
    http_method = event.get("httpMethod")
    is_test_event = event.get("is_test_event")
    if is_test_event:
        return
    try:
        table.put_item(Item={
            "lambda_name": lambda_name,
            "timestamp": curr_timestamp_in_ms(),
            "http_method": http_method,
            "event": event,
            "is_error": is_error,
            "lambda_response": lambda_response
        })
    except ClientError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)

def get_trace_id_from_event(event: dict) -> str:
    return event.get('trace_id', str(uuid.uuid4()))

def get_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS', 
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    }

def get_200_response(body):
    return {
        "statusCode": 200, 
        'headers': get_headers(),
        "body": json.dumps(body, cls=DecimalEncoder)
    }

def dynamic_init(cls, data):
    try:
        if isinstance(data, dict):
            field_types = {f.name: f.type for f in fields(cls)}
            return cls(**{
                key: dynamic_init(field_types[key], value) 
                for key, value in data.items() 
                if key in field_types
            })
        elif isinstance(data, list):
            elem_type = cls.__args__[0]
            return [dynamic_init(elem_type, item) for item in data]
        elif issubclass(cls, enum.Enum):
            return cls(data)
        else:
            return data
    except Exception as e:
        logger.error(f"Dynamic init failed: {cls} {data}")
        logger.exception(f"Dynamic init failed: {cls} {data}")
        raise e

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def serialize_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": json.dumps(body) if isinstance(body, dict) else body
    }