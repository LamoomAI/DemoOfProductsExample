from dataclasses import dataclass, field
from typing import List
from itertools import combinations
import uuid
import logging
from src.utils import UserPreferences
from src.cache import cache_results
from unittest.mock import Mock

@dataclass
class FurnitureItem:
    furniture_id: str
    type: str
    color: str
    material: str
    price: float

@dataclass
class Bundle:
    bundle_id: str
    items: List[FurnitureItem] = field(default_factory=list)
    total_price: float = 0.0

    def add_item(self, item: FurnitureItem):
        self.items.append(item)
        self.total_price += item.price

    def fits_budget(self, budget: float) -> bool:
        return self.total_price <= budget

def generate_bundles(furniture_items: List[FurnitureItem], user_preferences: UserPreferences) -> List[Bundle]:
    logging.info(f"Generating bundles with furniture items: {furniture_items} and preferences: {user_preferences}")
    
    # Filter out furniture items that do not match the user's color and material preferences
    filtered_items = [
        item for item in furniture_items
        if item.color in user_preferences.color_preferences
        and item.material in user_preferences.material_preferences
    ]
    
    # Generate all possible combinations of furniture items
    all_combinations = []
    for r in range(1, len(filtered_items) + 1):
        all_combinations.extend(combinations(filtered_items, r))
    
    # Create bundles from combinations that fit within the user's budget
    valid_bundles = []
    for combo in all_combinations:
        total_price = sum(item.price for item in combo)
        if total_price <= user_preferences.budget:
            valid_bundles.append(Bundle(bundle_id=str(uuid.uuid4()), items=list(combo), total_price=total_price))
    
    for bundle in valid_bundles:
        logging.info(f"Generated bundle {bundle.bundle_id} with total price {bundle.total_price} and preferences: {user_preferences}")
    
    # Call to cache_results function
    cache_results(valid_bundles)
    
    return valid_bundles