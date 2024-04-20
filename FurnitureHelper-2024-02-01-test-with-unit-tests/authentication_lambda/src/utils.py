import logging
from src.errors import CustomError
from src.metrics import send_metric_to_cloudwatch

logger = logging.getLogger(__name__)

def extract_authorization_header(event):
    """
    Extracts the authorization header from the API Gateway event.
    
    :param event: The event dictionary containing the HTTP headers.
    :return: The value of the Authorization header.
    :raises KeyError: If the headers or the Authorization header are missing.
    """
    try:
        # Extract the Authorization header from the event
        authorization_header = event['headers']['Authorization']
        logger.info(f"Authorization header extracted: {authorization_header}")
        return authorization_header
    except KeyError as e:
        logger.error(f"Authorization header missing in the event: {event}")
        raise e

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