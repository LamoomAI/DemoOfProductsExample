import pytest
from src.bundle import generate_bundles, Bundle
from src.utils import UserPreferences
from src.search import FurnitureItem
from unittest.mock import patch, MagicMock

@pytest.fixture
def furniture_items():
    return [
        FurnitureItem(furniture_id='chair001', type='chair', color='blue', material='wood', price=250.0),
        FurnitureItem(furniture_id='table002', type='table', color='grey', material='metal', price=500.0),
        FurnitureItem(furniture_id='sofa003', type='sofa', color='blue', material='wood', price=750.0)
    ]

@pytest.fixture
def user_preferences():
    return UserPreferences(budget=1500, color_preferences=["blue", "grey"], material_preferences=["wood", "metal"], trace_id="123456")

@patch('src.bundle.cache_results')
def test_generate_bundles(mock_cache_results, furniture_items, user_preferences):
    bundles = generate_bundles(furniture_items, user_preferences)
    assert isinstance(bundles, list)
    assert len(bundles) > 0
    assert all(isinstance(bundle, Bundle) for bundle in bundles)
    assert all(bundle.fits_budget(user_preferences.budget) for bundle in bundles)
    assert all(bundle.total_price <= user_preferences.budget for bundle in bundles)
    mock_cache_results.assert_called_once_with(bundles)

# Test case to ensure that cache_results is called with the correct parameters
@patch('src.bundle.cache_results')
def test_cache_results_called_with_correct_parameters(mock_cache_results, furniture_items, user_preferences):
    bundles = generate_bundles(furniture_items, user_preferences)
    cache_results(bundles, user_preferences)
    expected_cache_key = f"bundles:{user_preferences.budget}:{':'.join(user_preferences.color_preferences)}:{':'.join(user_preferences.material_preferences)}"
    mock_cache_results.assert_called_once_with(expected_cache_key, ANY)

# Updated test case to reflect the expected behavior when cache_results encounters an exception
@patch('src.bundle.cache_results')
def test_cache_results_handles_exceptions(mock_cache_results, furniture_items, user_preferences):
    mock_cache_results.side_effect = Exception("Cache service error")
    try:
        bundles = generate_bundles(furniture_items, user_preferences)
        cache_results(bundles)
    except Exception as e:
        pytest.fail(f"cache_results did not handle the exception gracefully: {e}")