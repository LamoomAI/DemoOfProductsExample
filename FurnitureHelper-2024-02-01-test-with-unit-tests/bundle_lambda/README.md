# BundleLambda
Creates furniture bundles based on the selected layout and user preferences, interacts with OpenSearch to find matching furniture items, and caches results.

### Triggers
API Gateway generate_bundles Receives layout ID and preferences to generate furniture bundles.

### Downstream Dependencies
OpenSearch query_furniture_items Queries for furniture items based on the furniture types and bundle’s keywords.
##Initial plan:

- calls:
    - main(request) -> List[Bundle]:
        - authenticate(request.headers) -> User
        - parse_input(request.body) -> (LayoutID, UserPreferences)
        - query_opensearch(LayoutID, UserPreferences) -> List[FurnitureItem]
        - generate_bundles(List[FurnitureItem], UserPreferences) -> List[Bundle]
        - cache_results(List[Bundle]):
- classes:
    - Bundle:
        - items: List[FurnitureItem]
        - total_price: float
        - fits_budget(UserPreferences): bool
    - FurnitureItem:
        - type: str
        - color: str
        - material: str
        - price: float
    - UserPreferences:
        - budget: float
        - color_preferences: List[str]
        - material_preferences: List[str]
    - SearchQuery:
        - layout_id: str
        - preferences: UserPreferences
        - construct_query() -> dict

##Function calls details

{
    "plan": [
        {
            "function": "authenticate",
            "description": "Authenticates the incoming request and retrieves the user information.",
            "input_format": {"authorization_header": "string"},
            "output_format": "User",
            "filepath": "src/utils.py"
        },
        {
            "function": "parse_input",
            "description": "Parses the input data to extract layout ID and user preferences.",
            "input_format": {"body": "string"},
            "output_format": {"LayoutID": "string", "UserPreferences": "UserPreferences"},
            "filepath": "src/utils.py"
        },
        {
            "function": "query_opensearch",
            "description": "Queries OpenSearch with the layout ID and user preferences to find matching furniture items.",
            "input_format": {"LayoutID": "string", "UserPreferences": "UserPreferences"},
            "output_format": "List[FurnitureItem]",
            "filepath": "src/search.py"
        },
        {
            "function": "generate_bundles",
            "description": "Generates furniture bundles based on the search results and user preferences.",
            "input_format": {"List[FurnitureItem]": "list", "UserPreferences": "UserPreferences"},
            "output_format": "List[Bundle]",
            "filepath": "src/bundle.py"
        },
        {
            "function": "cache_results",
            "description": "Caches the generated bundles for similar future requests.",
            "input_format": {"List[Bundle]": "list"},
            "output_format": "None",
            "filepath": "src/cache.py"
        }
    ]
}
