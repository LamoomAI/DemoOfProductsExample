import logging
import boto3
from botocore.exceptions import ClientError
from src.errors import CustomError
from src.metrics import send_metric_to_cloudwatch
from dataclasses import dataclass

logger = logging.getLogger()

COGNITO_USER_POOL_ID = 'us-east-1_example'
COGNITO_APP_CLIENT_ID = 'exampleclientid123'

@dataclass
class Response:
    status: str
    message: str

def authenticate_user(event):
    """
    Authenticates the user by validating the provided token with AWS Cognito.

    :param event: The event object containing the user's token.
    :return: A User object with the user's ID if authentication is successful.
    :raises CustomError: If the token is invalid or any other error occurs.
    """
    try:
        # Extract the token from the event object
        token = event.get('token')
        if not token:
            raise CustomError('Missing token', status_code=400, error_type='authentication_error')

        # Initialize the Cognito client
        cognito_client = boto3.client('cognito-idp')

        # Validate the token and get the user details from Cognito
        user_details = cognito_client.get_user(AccessToken=token)

        # Extract the user ID from the response
        user_id = user_details.get('Username')
        if not user_id:
            raise CustomError('User ID not found', status_code=404, error_type='authentication_error')

        # Return a User object with the user's ID
        return {'user_id': user_id}

    except ClientError as e:
        # Handle Cognito client errors
        error_code = e.response['Error']['Code']
        if error_code == 'NotAuthorizedException':
            raise CustomError('Invalid token', status_code=401, error_type='authentication_error')
        else:
            raise CustomError('Cognito client error', status_code=500, error_type='authentication_error')
    except Exception as e:
        # Handle unexpected errors
        raise CustomError(str(e), status_code=500, error_type='authentication_error')

def error_response(error: CustomError):
    if error.status_code >= 500:
        logger.exception(error)
    send_metric_to_cloudwatch(error.error_type, 1)
    return {"statusCode": error.status_code, "body": error.message}

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

def get_bundle_id(event):
    """
    Extracts the bundle ID from the event.
    :param event: The event object containing the bundle ID.
    :return: The extracted bundle ID as a string.
    :raises: CustomError if the bundle ID is not found or is invalid.
    """
    try:
        bundle_id = event['bundle_id']
        if not bundle_id:
            raise ValueError("Bundle ID is empty")
        return bundle_id
    except KeyError:
        logger.exception("Bundle ID not found in the event")
        raise CustomError(message="Bundle ID not found", status_code=400, error_type="bundle_id_missing")
    except ValueError as e:
        logger.exception(str(e))
        raise CustomError(message=str(e), status_code=400, error_type="invalid_bundle_id")

def generate_confirmation_response(update_status: bool) -> Response:
    """
    Generates a response confirming the cart update.

    :param update_status: A boolean indicating the success or failure of the cart update.
    :return: A Response object with the status and message.
    """
    if update_status:
        return Response(status="success", message="Cart updated successfully.")
    else:
        return Response(status="failure", message="Failed to update cart.")