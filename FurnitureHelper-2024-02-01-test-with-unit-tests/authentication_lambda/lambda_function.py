import json
import boto3
import logging
from src.tracing import setup_logging
from src.utils import try_except, extract_authorization_header
from src.settings import COGNITO_USER_POOL_ID, COGNITO_CLIENT_ID

logger = logging.getLogger()
cognito_client = boto3.client('cognito-idp')

@try_except
def lambda_handler(event, context):
    setup_logging(event)
    authorization_header = extract_authorization_header(event)
    
    body = json.loads(event.get('body', '{}'))
    username = body.get('username')
    password = body.get('password')
    
    if not username or not password:
        logger.warning("Username or password not provided in the request.")
        return {"statusCode": 400, "body": json.dumps({"message": "Username and password are required"})}
    
    try:
        response = cognito_client.admin_initiate_auth(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            }
        )
        results = response
    except cognito_client.exceptions.UserNotFoundException:
        logger.warning("User not found during authentication attempt.")
        return {"statusCode": 404, "body": json.dumps({"message": "User not found"})}
    except cognito_client.exceptions.NotAuthorizedException:
        logger.warning("Not authorized attempt to authenticate.")
        return {"statusCode": 401, "body": json.dumps({"message": "Not authorized"})}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"message": "An error occurred"})}
    
    return {"statusCode": 200, "body": json.dumps(results)}