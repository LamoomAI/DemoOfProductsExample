import os
import logging
import json
import base64
import hashlib
from dataclasses import dataclass
from typing import List
from src.errors import CustomError, ValidationError
from src.metrics import send_metric_to_cloudwatch

logger = logging.getLogger()

class User:
    def __init__(self, user_id, email, roles):
        self.user_id = user_id
        self.email = email
        self.roles = roles

    def __repr__(self):
        return f"User(user_id={self.user_id}, email={self.email}, roles={self.roles})"

@dataclass
class UserPreferences:
    budget: float
    color_preferences: List[str]
    material_preferences: List[str]
    trace_id: str

def authenticate(authorization_header: str) -> User:
    try:
        token = authorization_header.split(" ")[1]
        logger.info(f"Authenticating user with token: {token}")

        payload_encoded = token.split(".")[1]
        padding = '=' * (4 - len(payload_encoded) % 4)
        payload_encoded += padding
        payload_bytes = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_bytes.decode('utf-8'))

        if not validate_token_mock(token):
            raise ValidationError("Invalid token", status_code=401)

        user_id = payload.get("sub")
        email = payload.get("email")
        roles = payload.get("cognito:groups", [])

        user = User(user_id=user_id, email=email, roles=roles)
        logger.info(f"Authenticated user: {user}")
        return user

    except IndexError as error:
        logger.exception("Malformed authorization header")
        raise ValidationError("Malformed authorization header", status_code=400) from error
    except (json.JSONDecodeError, base64.binascii.Error) as error:
        logger.exception("Invalid token encoding")
        raise ValidationError("Invalid token encoding", status_code=400) from error
    except ValidationError as error:
        logger.exception("Authentication failed")
        raise error
    except Exception as error:
        logger.exception("Unknown error during authentication")
        raise ValidationError("Unknown error during authentication", status_code=500) from error

def validate_token_mock(token: str) -> bool:
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    return token_hash.endswith("a4c")

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

def parse_input(body: str) -> dict:
    try:
        data = json.loads(body)
        logger.info(f"Parsing input: {data}")

        layout_id = data.get('layout_id')
        if not layout_id:
            raise ValidationError("Missing 'layout_id' in the input data", status_code=400)

        preferences = data.get('preferences')
        if not preferences:
            raise ValidationError("Missing 'preferences' in the input data", status_code=400)

        user_preferences = UserPreferences(
            budget=preferences.get('budget'),
            color_preferences=preferences.get('color_preferences', []),
            material_preferences=preferences.get('material_preferences', []),
            trace_id=preferences.get('trace_id', str(uuid.uuid4()))  # Default to a new UUID if not provided
        )

        if user_preferences.budget is None or not isinstance(user_preferences.budget, (int, float)):
            raise ValidationError("Invalid or missing 'budget' in preferences", status_code=400)

        return {
            'LayoutID': layout_id,
            'UserPreferences': user_preferences
        }

    except json.JSONDecodeError as error:
        logger.exception("Invalid JSON format")
        raise ValidationError("Invalid JSON format", status_code=400) from error
    except ValidationError as error:
        logger.exception("Validation error during input parsing")
        raise error
    except Exception as error:
        logger.exception("Unknown error during input parsing")
        raise ValidationError("Unknown error during input parsing", status_code=500) from error