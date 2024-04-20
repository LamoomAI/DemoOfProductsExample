import pytest
from unittest.mock import patch, MagicMock
from src.cart import update_shopping_cart
from src.errors import CustomError

# Mock the DynamoDB Table object instead of the DynamoDB ServiceResource
mock_table = MagicMock()

@patch('src.cart.dynamodb.Table', return_value=mock_table)
def test_update_shopping_cart_success():
    event = {
        'User': {'user_id': 'user123'},
        'bundle_id': 'bundle456',
        'trace_id': 'test-trace-id'
    }
    mock_table.update_item.return_value = {'Attributes': {'bundles': [event['bundle_id']]}}
    assert update_shopping_cart(event) is True

@patch('src.cart.dynamodb.Table', return_value=mock_table)
def test_update_shopping_cart_failure(mock_table):
    mock_table.update_item.side_effect = Exception("DynamoDB update failed")
    event = {
        'User': {'user_id': 'user123'},
        'bundle_id': 'bundle456',
        'trace_id': 'test-trace-id'
    }
    with pytest.raises(CustomError) as exc_info:
        update_shopping_cart(event)
    assert exc_info.value.status_code == 500
    assert exc_info.value.error_type == 'cart_update_error'

def test_update_shopping_cart_missing_user_id():
    event = {'User': {}, 'bundle_id': 'valid_bundle_id'}
    with pytest.raises(CustomError) as exc_info:
        update_shopping_cart(event)
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == 'cart_update_error'

def test_update_shopping_cart_missing_bundle_id():
    event = {'User': {'user_id': 'valid_user_id'}}
    with pytest.raises(CustomError) as exc_info:
        update_shopping_cart(event)
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_type == 'cart_update_error'