import pytest
from src.utils import extract_authorization_header, try_except
from src.errors import CustomError

@try_except
def raise_exception(class_exception=Exception):
    raise class_exception("test exception")

def test_try_except():
    response = raise_exception()
    assert response["statusCode"] == 500

def test_try_custom_except():
    response = raise_exception(class_exception=CustomError)
    assert response["statusCode"] == 500

def test_extract_authorization_header_with_valid_header():
    event = {'headers': {'Authorization': 'Bearer valid_token'}}
    assert extract_authorization_header(event) == 'Bearer valid_token'

def test_extract_authorization_header_with_missing_header():
    event = {'headers': {}}
    with pytest.raises(KeyError):
        extract_authorization_header(event)

def test_extract_authorization_header_with_no_headers():
    event = {}
    with pytest.raises(KeyError):
        extract_authorization_header(event)