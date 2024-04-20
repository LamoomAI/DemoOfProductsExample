import logging
import boto3
import json
from botocore.exceptions import ClientError
from dataclasses import dataclass
from src.errors import CustomError
from src.tracing import get_trace_id
from src.metrics import send_metric_to_cloudwatch
from src.settings import DYNAMODB_TABLE_NAME, AWS_REGION

logger = logging.getLogger()
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

@dataclass
class ChangeRequest:
    bundle_id: str
    item_to_replace: str
    new_attributes: dict

@dataclass
class ReplacementItems:
    items: list
    bundle_id: str

@dataclass
class UpdateConfirmation:
    success: bool
    updated_bundle: dict

@dataclass
class Response:
    status_code: int
    body: dict

def authenticate(authorization_header: str) -> dict:
    """
    Simulate an authentication process.

    :param authorization_header: The authorization header containing the credentials.
    :return: A dictionary with a user_id if authentication is successful.
    """
    # Placeholder for actual authentication logic
    # Assuming the authentication is successful and returning a dummy user_id
    return {'user_id': 'dummy_user_id'}

def parse_change_request(request_body: dict) -> ChangeRequest:
    """
    Parse the change request from the request body.

    :param request_body: The request body containing the change request details.
    :return: A ChangeRequest object with the parsed data.
    """
    # Placeholder for actual parsing logic
    # Assuming the request body contains all necessary fields
    if 'bundle_id' not in request_body or 'item_to_replace' not in request_body or 'new_attributes' not in request_body:
        raise ValueError("Missing required fields in the change request")
    return ChangeRequest(
        bundle_id=request_body['bundle_id'],
        item_to_replace=request_body['item_to_replace'],
        new_attributes=request_body['new_attributes']
    )

def try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CustomError as error:
            return error_response(error)
        except Exception as error:
            logger.exception(error)
            send_metric_to_cloudwatch("unknown_exception", 1)
            return {"statusCode": 500, "body": "Internal error occurred"}
    return wrapper

def build_response(update_confirmation: UpdateConfirmation) -> Response:
    trace_id = get_trace_id()
    logger.info(f"Building response for update confirmation, trace_id: {trace_id}")
    
    if update_confirmation.success:
        logger.info(f"Bundle update successful, trace_id: {trace_id}")
        response = Response(
            status_code=200,
            body={
                "message": "Bundle updated successfully",
                "updated_bundle": update_confirmation.updated_bundle,
                "trace_id": trace_id
            }
        )
    else:
        logger.error(f"Bundle update failed, trace_id: {trace_id}")
        response = Response(
            status_code=500,
            body={
                "message": "Failed to update the bundle",
                "error": "Internal Server Error",
                "trace_id": trace_id
            }
        )
    
    logger.info(f"Response built: {response}, trace_id: {trace_id}")
    return response

@try_except
def update_bundle_in_database(replacement_items: ReplacementItems) -> UpdateConfirmation:
    trace_id = get_trace_id()
    logger.info(f"Updating bundle in database with new items: {replacement_items.items}, trace_id: {trace_id}")
    
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    try:
        response = table.update_item(
            Key={'bundle_id': replacement_items.bundle_id},
            UpdateExpression='SET items = :newItems',
            ExpressionAttributeValues={
                ':newItems': replacement_items.items
            },
            ReturnValues='ALL_NEW'
        )
        
        updated_bundle = response.get('Attributes', {})
        logger.info(f"Bundle updated successfully in database, bundle_id: {replacement_items.bundle_id}, trace_id: {trace_id}")
        return UpdateConfirmation(success=True, updated_bundle=updated_bundle)
    
    except ClientError as e:
        logger.error(f"Failed to update bundle in database, bundle_id: {replacement_items.bundle_id}, error: {e}, trace_id: {trace_id}")
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            raise CustomError("Bundle does not exist", status_code=404)
        else:
            raise CustomError("Error updating bundle in database", status_code=500)