import pytest
from unittest.mock import patch
from src.search import query_opensearch
from src.utils import UserPreferences

@pytest.fixture
def user_preferences():
    return UserPreferences(budget=1500, color_preferences=["blue", "grey"], material_preferences=["wood", "metal"])

@pytest.fixture
def layout_id():
    return "layout123"

@patch('src.search.search_client')
def test_query_opensearch_success(mock_search_client, user_preferences, layout_id):
    mock_search_client.search.return_value = {
        'hits': {
            'hits': [
                {'_id': 'chair001', '_source': {'type': 'chair', 'color': 'blue', 'material': 'wood', 'price': 250.0}},
                {'_id': 'table002', '_source': {'type': 'table', 'color': 'grey', 'material': 'metal', 'price': 500.0}}
            ]
        }
    }
    results = query_opensearch(layout_id, user_preferences)
    assert results == [
        {'furniture_id': 'chair001', 'type': 'chair', 'color': 'blue', 'material': 'wood', 'price': 250.0},
        {'furniture_id': 'table002', 'type': 'table', 'color': 'grey', 'material': 'metal', 'price': 500.0}
    ]
    assert all(isinstance(item, dict) for item in results)

@patch('src.search.search_client')
def test_query_opensearch_no_results(mock_search_client, user_preferences, layout_id):
    mock_search_client.search.return_value = {'hits': {'hits': []}}
    results = query_opensearch(layout_id, user_preferences)
    assert results == []

def test_query_opensearch_invalid_layout_id(user_preferences):
    with pytest.raises(ValueError):
        query_opensearch("invalid_layout_id", user_preferences)

def test_query_opensearch_invalid_preferences(layout_id):
    with pytest.raises(ValueError):
        query_opensearch(layout_id, "invalid_preferences")