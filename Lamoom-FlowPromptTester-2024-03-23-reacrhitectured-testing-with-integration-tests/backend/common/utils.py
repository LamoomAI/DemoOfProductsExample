# common/utils.py
import json

def serialize_response(status_code: int, body: dict or str) -> dict:
    """
    Serializes the response data for the Web Interface.

    :param status_code: The HTTP status code for the response.
    :param body: The response body, which can be a dict or a string.
    :return: A dictionary representing the serialized response.
    """
    # Ensure the body is a JSON string
    if isinstance(body, dict):
        body = json.dumps(body, cls=DecimalEncoder)
    elif not isinstance(body, str):
        raise TypeError("The body of the response must be a dict or a string.")

    # Construct the response object with CORS headers
    response = {
        "statusCode": status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        },
        "body": body
    }

    # Log the response for debugging purposes
    logger.info(f"Serialized response: {response}")

    return response