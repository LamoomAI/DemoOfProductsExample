from src.errors import CustomError
from src.utils import try_except, parse_change_request, ChangeRequest, find_replacement_items, ReplacementItems, update_bundle_in_database, UpdateConfirmation, build_response
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Dummy function to test the try_except decorator
@try_except
def dummy_function():
    raise Exception("test exception")

@try_except
def dummy_function_custom_error():
    raise CustomError("test custom exception", status_code=400)

def test_try_except():
    response = dummy_function()
    assert response["statusCode"] == 500
    assert response["body"] == "Internal error occurred"

def test_try_custom_except():
    response = dummy_function_custom_error()
    assert response["statusCode"] == 400
    assert response["body"] == "test custom exception"

def test_parse_change_request_valid():
    request_body = {
        "bundle_id": "bundle123",
        "item_to_replace": "chair789",
        "new_attributes": {
            "color": "red",
            "material": "leather"
        }
    }
    expected_output = ChangeRequest(
        bundle_id="bundle123",
        item_to_replace="chair789",
        new_attributes={
            "color": "red",
            "material": "leather"
        }
    )
    assert parse_change_request(request_body) == expected_output

def test_parse_change_request_missing_fields():
    request_body = {
        "item_to_replace": "chair789",
        "new_attributes": {
            "color": "red"
        }
    }
    try:
        parse_change_request(request_body)
        assert False, "Expected ValueError for missing fields"
    except ValueError as e:
        assert str(e) == "Missing required fields in the change request: bundle_id"

@patch('src.utils.get_replacement_items_from_db')
def test_find_replacement_items_success(mock_get_replacement_items):
    mock_get_replacement_items.return_value = [
        {"furniture_id": "chair101", "color": "red", "material": "leather"}
    ]
    change_request = ChangeRequest(
        bundle_id="bundle123",
        item_to_replace="chair789",
        new_attributes={"color": "red", "material": "leather"}
    )
    expected_output = ReplacementItems(items=[
        {"furniture_id": "chair101", "color": "red", "material": "leather"}
    ])
    assert find_replacement_items(change_request) == expected_output

@patch('src.utils.get_replacement_items_from_db')
def test_find_replacement_items_no_match(mock_get_replacement_items):
    mock_get_replacement_items.return_value = []
    change_request = ChangeRequest(
        bundle_id="bundle123",
        item_to_replace="chair789",
        new_attributes={"color": "green", "material": "cotton"}
    )
    expected_output = ReplacementItems(items=[])
    assert find_replacement_items(change_request) == expected_output

@patch('src.utils.boto3.resource')
def test_update_bundle_in_database_success(mock_dynamodb_resource):
    mock_table = MagicMock()
    mock_dynamodb_resource.return_value.Table.return_value = mock_table
    mock_table.update_item.return_value = {
        'Attributes': {
            'bundle_id': 'test_bundle',
            'items': [{'furniture_id': 'chair101', 'color': 'red', 'price': 160}]
        }
    }
    
    replacement_items = ReplacementItems(bundle_id='test_bundle', items=[{'furniture_id': 'chair101', 'color': 'red', 'price': 160}])
    update_confirmation = update_bundle_in_database(replacement_items)
    
    assert update_confirmation.success == True
    assert update_confirmation.updated_bundle['bundle_id'] == 'test_bundle'
    assert 'items' in update_confirmation.updated_bundle

@patch('src.utils.boto3.resource')
def test_update_bundle_in_database_failure(mock_dynamodb_resource):
    mock_table = MagicMock()
    mock_dynamodb_resource.return_value.Table.return_value = mock_table
    mock_table.update_item.side_effect = ClientError({'Error': {'Code': 'ConditionalCheckFailedException'}}, 'UpdateItem')
    
    replacement_items = ReplacementItems(bundle_id='non_existing_bundle', items=[{'furniture_id': 'chair101', 'color': 'red', 'price': 160}])
    
    try:
        update_bundle_in_database(replacement_items)
        assert False, "CustomError not raised"
    except CustomError as e:
        assert e.status_code == 404

@patch('src.utils.get_trace_id')
def test_build_response_success(mock_get_trace_id):
    mock_get_trace_id.return_value = 'test_trace_id'
    update_confirmation = UpdateConfirmation(
        success=True,
        updated_bundle={
            'bundle_id': 'test_bundle',
            'items': [{'furniture_id': 'chair101', 'color': 'red', 'price': 160}]
        }
    )
    response = build_response(update_confirmation)
    assert response.status_code == 200
    assert response.body['message'] == "Bundle updated successfully"
    assert 'trace_id' in response.body
    assert response.body['trace_id'] == 'test_trace_id'

@patch('src.utils.get_trace_id')
def test_build_response_failure(mock_get_trace_id):
    mock_get_trace_id.return_value = 'test_trace_id'
    update_confirmation = UpdateConfirmation(
        success=False,
        updated_bundle={}
    )
    response = build_response(update_confirmation)
    assert response.status_code == 500
    assert response.body['message'] == "Failed to update the bundle"
    assert 'trace_id' in response.body
    assert response.body['trace_id'] == 'test_trace_id'