import json
import jwt
import datetime
import boto3
from common.locallogging import setup_logging, setup_logging_for_event
from common.utils import try_except, get_trace_id_from_event
from modules.cognito_service import exchange_code_for_token
from common.errors import ValidationError, UserNotFoundError
from dataclasses import dataclass
from common.settings import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_DELTA_SECONDS

metrics_namespace = 'lambda_authentication_handler'
logger = setup_logging(metrics_namespace)

@dataclass
class AuthenticationRequest:
    code_token: str

@dataclass
class AuthenticationResponse:
    jwt_token: str
    user_data: dict

@dataclass
class Token:
    token: str

@dataclass
class User:
    id: str
    email: str
    roles: list

@try_except
def validate_authentication_request(event: dict) -> Token:
    logger = setup_logging_for_event(event, metrics_namespace)
    trace_id = get_trace_id_from_event(event)
    
    code_token = event.get('queryStringParameters', {}).get('code', None)
    
    if not code_token:
        error_message = "Missing 'code' parameter in event."
        logger.error(f"{error_message} Event: {event}", extra={'trace_id': trace_id})
        raise ValidationError(error_message, status_code=400)
    
    logger.info(f"Code token extracted from event: {code_token}", extra={'trace_id': trace_id})
    
    return Token(token=code_token)

@try_except
def exchange_code_for_jwt(code_token: str) -> AuthenticationResponse:
    try:
        jwt_token, user_data = exchange_code_for_token(code_token)  # Assuming exchange_code_for_token returns a tuple (jwt_token, user_data)
        logger.info(f"Successfully exchanged code token for JWT: {jwt_token}")
        return AuthenticationResponse(jwt_token=jwt_token, user_data=user_data)
    except Exception as e:
        logger.error(f"Failed to exchange code token for JWT: {str(e)}")
        raise e

@try_except
def get_user_data(token: Token) -> User:
    token_string = token.token
    cognito_client = boto3.client('cognito-idp')
    
    try:
        response = cognito_client.get_user(AccessToken=token_string)
    except cognito_client.exceptions.UserNotFoundException:
        logger.error(f"User not found for the given token: {token_string}")
        raise UserNotFoundError("User not found.")
    except Exception as e:
        logger.error(f"An error occurred while fetching user data: {str(e)}")
        raise e
    
    user_attributes = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
    user_id = user_attributes['sub']
    email = user_attributes.get('email', '')
    roles = user_attributes.get('custom:roles', '').split(',')
    
    user = User(id=user_id, email=email, roles=roles)
    logger.info(f"Retrieved user data for user ID: {user_id}")
    return user

def generate_jwt(user: User) -> str:
    payload = {
        'user_id': user.id,
        'email': user.email,
        'roles': user.roles,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRATION_DELTA_SECONDS)
    }

    jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.info(f"JWT token generated for user {user.email}")
    return jwt_token

@try_except
def log_authentication_attempt(authentication_request: AuthenticationRequest, authentication_response: AuthenticationResponse):
    trace_id = get_trace_id_from_event(event)  # Assuming event is available in the scope, otherwise, it should be passed as a parameter.

    logger.info(f"Authentication attempt with code token: {authentication_request.code_token}", extra={'trace_id': trace_id})

    if authentication_response.jwt_token:
        logger.info(f"Authentication successful for code token: {authentication_request.code_token} with JWT token: {authentication_response.jwt_token}", extra={'trace_id': trace_id})
    else:
        logger.error(f"Authentication failed for code token: {authentication_request.code_token}. Response: {authentication_response.user_data}", extra={'trace_id': trace_id})

@try_except
def main(event: dict, context: dict) -> dict:
    logger = setup_logging_for_event(event, metrics_namespace)
    trace_id = get_trace_id_from_event(event)
    if not trace_id:
        trace_id = "generated_trace_id"  # Replace with actual trace ID generation logic

    try:
        token = validate_authentication_request(event)
        logger.info(f"Authentication request validated with code token: {token.token}", extra={'trace_id': trace_id})
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", extra={'trace_id': trace_id})
        return {"statusCode": e.status_code, "body": json.dumps({"error": str(e)})}

    try:
        auth_response = exchange_code_for_jwt(token.token)
        logger.info(f"JWT token exchanged: {auth_response.jwt_token}", extra={'trace_id': trace_id})
    except Exception as e:
        logger.error(f"Error exchanging code token for JWT: {str(e)}", extra={'trace_id': trace_id})
        return {"statusCode": 500, "body": json.dumps({"error": "Failed to exchange code token for JWT"})}

    try:
        user = get_user_data(token)
        logger.info(f"User data retrieved: {user.id}", extra={'trace_id': trace_id})
    except Exception as e:
        logger.error(f"Error retrieving user data: {str(e)}", extra={'trace_id': trace_id})
        return {"statusCode": 500, "body": json.dumps({"error": "Failed to retrieve user data"})}

    log_authentication_attempt(AuthenticationRequest(code_token=token.token), auth_response)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "jwt_token": auth_response.jwt_token,
            "user_data": auth_response.user_data
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "trace_id": trace_id
    }

# Replace the lambda_handler with the main function
lambda_handler = main