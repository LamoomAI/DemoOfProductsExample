import boto3
from boto3.dynamodb.conditions import Key
from common.errors import DatabaseError
from common.locallogging import setup_logging_for_event

# Assuming the DynamoDB table names are constants defined somewhere
from common.constants import LATEST_PROMPTS_TABLE, PROMPT_HISTORY_TABLE, BEHAVIORS_TABLE

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

def perform_crud_operation(parsed_event):
    """
    Executes the CRUD operation on DynamoDB and returns the result.

    :param parsed_event: An object containing the operation type and data.
    :return: A CRUDResult object with the outcome of the operation.
    """
    # Extract operation type and data from the parsed event
    operation = parsed_event['operation']
    data = parsed_event['data']
    table_name = None
    item = None
    response = None

    try:
        if operation == 'create':
            table_name = BEHAVIORS_TABLE if 'behavior' in data else LATEST_PROMPTS_TABLE
            item = data
            table = dynamodb.Table(table_name)
            response = table.put_item(Item=item)

        elif operation == 'read':
            table_name = LATEST_PROMPTS_TABLE
            key = data['pathParameters']
            table = dynamodb.Table(table_name)
            response = table.get_item(Key=key)

        elif operation == 'update':
            table_name = PROMPT_HISTORY_TABLE
            key = data['pathParameters']
            update_expression = "set " + ", ".join(f"{k}=:{k}" for k in data['updateData'])
            expression_attribute_values = {f":{k}": v for k, v in data['updateData'].items()}
            table = dynamodb.Table(table_name)
            response = table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW"
            )

        elif operation == 'delete':
            table_name = BEHAVIORS_TABLE
            key = data['pathParameters']
            table = dynamodb.Table(table_name)
            response = table.delete_item(Key=key)

        else:
            raise ValueError(f"Unsupported operation: {operation}")

        # Construct the CRUDResult object
        crud_result = {
            'success': True,
            'message': f"{operation.capitalize()} operation successful.",
            'data': response.get('Item') or response
        }
        return crud_result

    except Exception as e:
        logger.error(f"Error performing {operation} operation on {table_name}: {e}")
        raise DatabaseError(f"Error performing {operation} operation: {e}")