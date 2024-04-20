import pytest
import json
from src.errors import CustomError, ValidationError
from src.utils import try_except, authenticate, User, parse_input, UserPreferences

@try_except
def raise_exception(class_exception=Exception):
    raise class_exception("test exception")

def test_try_except():
    response = raise_exception()
    assert response["statusCode"] == 500

def test_try_custom_except():
    response = raise_exception(class_exception=CustomError)
    assert response["statusCode"] == 500

def test_authenticate_success():
    authorization_header = "Bearer valid.mocked.jwt.token"
    user = authenticate(authorization_header)
    assert isinstance(user, User)
    assert user.user_id is not None
    assert user.email is not None

def test_authenticate_failure():
    authorization_header = "Bearer invalid.mocked.jwt.token"
    with pytest.raises(ValidationError) as exc_info:
        authenticate(authorization_header)
    assert exc_info.value.status_code == 401

def test_authenticate_malformed_header():
    authorization_header = "invalid_header_format"
    with pytest.raises(ValidationError) as exc_info:
        authenticate(authorization_header)
    assert exc_info.value.status_code == 400

def test_authenticate_missing_header():
    with pytest.raises(ValidationError) as exc_info:
        authenticate("")
    assert exc_info.value.status_code == 401
    assert "Missing authorization header" in str(exc_info.value)

def test_authenticate_invalid_header_format():
    with pytest.raises(ValidationError) as exc_info:
        authenticate("invalid_format")
    assert exc_info.value.status_code == 401
    assert "Invalid authorization header format" in str(exc_info.value)

def test_authenticate_invalid_token():
    with pytest.raises(ValidationError) as exc_info:
        authenticate("Bearer invalid_token")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value)

def test_parse_input_valid():
    body = json.dumps({
        'layout_id': 'layout123',
        'preferences': {
            'budget': 1000,
            'color_preferences': ['blue', 'green'],
            'material_preferences': ['wood', 'metal']
        }
    })
    result = parse_input(body)
    assert result['LayoutID'] == 'layout123'
    assert result['UserPreferences'].budget == 1000
    assert 'blue' in result['UserPreferences'].color_preferences
    assert 'wood' in result['UserPreferences'].material_preferences

def test_parse_input_missing_layout_id():
    body = json.dumps({
        'preferences': {
            'budget': 1000
        }
    })
    with pytest.raises(ValidationError) as excinfo:
        parse_input(body)
    assert 'Missing \'layout_id\'' in str(excinfo.value)

def test_parse_input_invalid_json():
    body = "{ this is not a valid json }"
    with pytest.raises(ValidationError) as excinfo:
        parse_input(body)
    assert 'Invalid JSON format' in str(excinfo.value)

def test_parse_input_invalid_budget():
    body = json.dumps({
        'layout_id': 'layout123',
        'preferences': {
            'budget': 'not a number',
            'color_preferences': ['blue'],
            'material_preferences': ['wood']
        }
    })
    with pytest.raises(ValidationError) as excinfo:
        parse_input(body)
    assert 'Invalid or missing \'budget\'' in str(excinfo.value)