import boto3
from botocore.exceptions import BotoCoreError, ClientError
from common.errors import AuthenticationError
from common.locallogging import get_logger

logger = get_logger(__name__)

def authenticate_user(user_info):
    """
    Authenticates the user using the provided identity token.

    :param user_info: A dictionary containing the user's identity token.
    :return: A dictionary with 'user_id' and 'roles'.
    """
    try:
        # Extract the identity token from the user_info dictionary
        identity_token = user_info.get('identity_token')
        if not identity_token:
            raise ValueError("Missing identity token in user_info")

        # Initialize Cognito Identity Provider client
        cognito_client = boto3.client('cognito-idp')

        # Verify the token and get the user's attributes
        response = cognito_client.get_user(AccessToken=identity_token)
        user_attributes = response.get('UserAttributes', [])
        user_id = None
        roles = []

        # Extract user_id and roles from user attributes
        for attribute in user_attributes:
            if attribute['Name'] == 'sub':
                user_id = attribute['Value']
            elif attribute['Name'] == 'custom:roles':
                roles = attribute['Value'].split(',')

        if not user_id:
            raise AuthenticationError("User ID (sub) not found in token claims")

        logger.info(f"User authenticated successfully: {user_id}")
        return {'user_id': user_id, 'roles': roles}

    except (BotoCoreError, ClientError, ValueError, AuthenticationError) as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise AuthenticationError(f"Authentication failed: {str(e)}")