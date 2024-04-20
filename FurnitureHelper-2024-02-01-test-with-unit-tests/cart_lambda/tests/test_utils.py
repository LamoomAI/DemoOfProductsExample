import pytest
from unittest.mock import patch
from src.utils import authenticate_user, try_except, get_bundle_id, generate_confirmation_response, Response
from src.errors import CustomError
from botocore.exceptions import ClientError

@try_except
def raise_exception(class_exception=Exception):
    raise class_exception("test exception")

def test_try_except():
    response = raise_exception()
    assert response["statusCode"] == 500

def test_try_custom_except():
    response = raise_exception(class_exception=CustomError)
    assert response["statusCode"] == 500

def test_authenticate_user_success():
    event = {'token': 'valid_token'}
    with patch('boto3.client') as mock_cognito:
        mock_cognito.return_value.get_user.return_value = {'Username': 'user123'}
        user = authenticate_user(event)
        assert user['user_id'] == 'user123'

def test_authenticate_user_failure():
    event = {'token': 'invalid_token'}
    with patch('boto3.client') as mock_cognito:
        mock_cognito.return_value.get_user.side_effect = ClientError(
            error_response={'Error': {'Code': 'NotAuthorizedException'}},
            operation_name='GetUser'
        )
        with pytest.raises(CustomError) as exc_info:
            authenticate_user(event)
        assert exc_info.value.status_code == 401
        assert exc_info.value.error_type == 'authentication_error'

def test_get_bundle_id_success():
    event = {'bundle_id': 'valid_bundle_id'}
    bundle_id = get_bundle_id(event)
    assert bundle_id == 'valid_bundle_id'

def test_get_bundle_id_missing():
    event = {}
    with pytest.raises(CustomError) as exc_info:
        get_bundle_id(event)
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == 'bundle_id_missing'

def test_get_bundle_id_empty():
    event = {'bundle_id': ''}
    with pytest.raises(CustomError) as exc_info:
        get_bundle_id(event)
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == 'invalid_bundle_id'

def test_generate_confirmation_response_success():
    update_status = True
    expected_response = Response(status="success", message="Cart updated successfully.")
    assert generate_confirmation_response(update_status) == expected_response

def test_generate_confirmation_response_failure():
    update_status = False
    expected_response = Response(status="failure", message="Failed to update cart.")
    assert generate_confirmation_response(update_status) == expected_response