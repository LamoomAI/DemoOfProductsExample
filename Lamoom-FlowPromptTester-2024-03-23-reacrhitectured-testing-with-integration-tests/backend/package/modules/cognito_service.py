import requests
import logging
from common.errors import InternalError
from common.locallogging import setup_logging

COGNITO_TOKEN_ENDPOINT = "https://<your_cognito_domain>/oauth2/token"
CLIENT_ID = "<your_client_id>"
CLIENT_SECRET = "<your_client_secret>"

logger = setup_logging(__name__)

def exchange_code_for_token(code_token: str) -> dict:
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code_token,
        "redirect_uri": "<your_redirect_uri>"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        logger.info(f"Attempting to exchange code for JWT token: {code_token}")
        response = requests.post(COGNITO_TOKEN_ENDPOINT, data=payload, headers=headers)
        response.raise_for_status()
        
        jwt_token = response.json().get('id_token')
        if not jwt_token:
            raise ValueError("JWT token not found in the response.")
        
        logger.info(f"Successfully exchanged code for JWT token.")
        return {"jwt_token": jwt_token}
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
        raise InternalError(message="Failed to exchange code for token due to an HTTP error.")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        raise InternalError(message="Failed to exchange code for token due to a request error.")
    except ValueError as val_err:
        logger.error(f"Value error occurred: {val_err}")
        raise InternalError(message="Failed to exchange code for token due to a value error.")
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
        raise InternalError(message="An unexpected error occurred while exchanging code for token.")

def generate_jwt(user: User) -> str:
    return "dummy_jwt_token_for_user_" + user.id