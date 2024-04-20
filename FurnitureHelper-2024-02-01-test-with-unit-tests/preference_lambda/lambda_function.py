import logging
import json
import os
import boto3
from openai import GPT3Client

from src.tracing import setup_logging
from src.utils import try_except, authenticate_user
from src.errors import CustomError
from src.settings import DYNAMODB_TABLE_NAME

logger = logging.getLogger()

openai_client = GPT3Client(api_key=os.getenv('OPENAI_API_KEY'))

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    try:
        auth_header = event.get('headers', {}).get('Authorization', '')
        user = authenticate_user(auth_header)
        logger.info(f"Authenticated user: {user.user_id}")
        
        body = json.loads(event.get('body', '{}'))
        user_str_preferences = body.get('user_str_preferences')

        structured_preferences = openai_client.get_structured_preferences(user_str_preferences)

        table.put_item(Item={
            'user_id': user.user_id,
            'preferences': structured_preferences
        })

        results = {
            'message': 'Preferences stored successfully',
            'structured_preferences': structured_preferences
        }
        return {"statusCode": 200, "body": json.dumps(results)}
    except CustomError as e:
        logger.error(f"Custom error occurred: {e}")
        return {"statusCode": e.status_code, "body": json.dumps({"message": e.message})}
    except Exception as e:
        logger.error(f"Unhandled exception occurred: {e}")
        return {"statusCode": 500, "body": json.dumps({"message": "Internal Server Error"})}