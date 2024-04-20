import jwt
import requests
import logging
from dataclasses import dataclass
from typing import Dict
from src.constants import COGNITO_USER_POOL_ID, AWS_REGION
from src.errors import UnauthorizedError, CustomError
from src.metrics import send_metric_to_cloudwatch
from src.settings import DYNAMODB_TABLE_NAME, OPENAI_API_KEY

logger = logging.getLogger()

COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"

@dataclass
class User:
    user_id: str

def get_cognito_keys() -> Dict:
    url = f"{COGNITO_ISSUER}/.well-known/jwks.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

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

@try_except
def authenticate_user(authorization_header: str) -> User:
    try:
        token = authorization_header.split(" ")[1]
    except IndexError:
        raise UnauthorizedError("Invalid authorization header format.")

    keys = get_cognito_keys()

    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next((key for key in keys['keys'] if key['kid'] == unverified_header['kid']), None)
        if rsa_key:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=COGNITO_USER_POOL_ID,
                issuer=COGNITO_ISSUER
            )
            return User(user_id=payload['sub'])
        else:
            raise UnauthorizedError("Public key not found.")
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token is expired.")
    except jwt.JWTClaimsError:
        raise UnauthorizedError("Incorrect claims, please check the audience and issuer.")
    except Exception as e:
        logger.exception("Error decoding token: %s", e)
        raise UnauthorizedError("Error decoding token.")

class GPT3Client:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_structured_preferences(self, user_str_preferences):
        # Call the OpenAI API to get structured preferences
        response = requests.post(
            "https://api.openai.com/v1/engines/davinci-codex/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": user_str_preferences, "max_tokens": 1024}
        )
        response.raise_for_status()
        return response.json()