import logging
import uuid
import boto3
from src.errors import CustomError
from src.utils import try_except
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
dynamodb = boto3.resource('dynamodb')

@try_except
def update_shopping_cart(event):
    """
    Updates the user's shopping cart with the new bundle.

    :param event: An event object containing the user and bundle_id.
    :return: True if the cart was updated successfully, False otherwise.
    :raises CustomError: If the update fails or input is invalid.
    """
    trace_id = event.get('trace_id', str(uuid.uuid4()))
    logger.info(f"Trace ID {trace_id}: Received event for cart update")

    user = event.get('User')
    user_id = user.get('user_id') if user else None
    bundle_id = event.get('bundle_id')
    if not user_id:
        logger.error(f"Trace ID {trace_id}: Missing user_id")
        raise CustomError('Missing user_id', status_code=400, error_type='cart_update_error', trace_id=trace_id)
    if not bundle_id:
        logger.error(f"Trace ID {trace_id}: Missing bundle_id")
        raise CustomError('Missing bundle_id', status_code=400, error_type='cart_update_error', trace_id=trace_id)

    try:
        table = dynamodb.Table('shopping_cart')
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='ADD bundles :bundle',
            ExpressionAttributeValues={':bundle': {bundle_id}},
            ReturnValues='UPDATED_NEW'
        )
        logger.info(f"Trace ID {trace_id}: Cart updated for user {user_id} with bundle {bundle_id}")
        return True
    except Exception as e:
        logger.error(f"Trace ID {trace_id}: Failed to update cart for user {user_id} with bundle {bundle_id}: {e}")
        raise CustomError('Failed to update shopping cart', status_code=500, error_type='cart_update_error', trace_id=trace_id)