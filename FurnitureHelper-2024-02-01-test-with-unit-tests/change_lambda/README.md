# ChangeLambda
Processes user requests to change items in the bundle, identifies suitable replacements, and updates the bundle in DynamoDB.

### Triggers
API Gateway change_item Receives bundle ID and item change request from the user.

### Downstream Dependencies
DynamoDB update_bundle Updates the bundle with the new item changes.
##Initial plan:

- calls:
    - main(request) -> Response:
        - authenticate(authorization_header) -> User
        - parse_change_request(request_body) -> ChangeRequest
        - find_replacement_items(ChangeRequest) -> ReplacementItems
        - update_bundle_in_database(ReplacementItems) -> UpdateConfirmation
        - build_response(UpdateConfirmation) -> Response
- classes:
    - User:
        - user_id: string
    - ChangeRequest:
        - bundle_id: string
        - item_change_details: dict
    - ReplacementItems:
        - items: list
    - UpdateConfirmation:
        - success: boolean
        - updated_bundle: dict
    - Response:
        - status_code: int
        - body: dict

##Function calls details

{
    "plan": [
        {
            "function": "authenticate",
            "description": "Authenticates the incoming request to ensure it's from a valid user",
            "input_format": {"authorization_header": "string"},
            "output_format": {"user_id": "string"},
            "filepath": "src/utils.py"
        },
        {
            "function": "parse_change_request",
            "description": "Parses the request body to extract the change request details",
            "input_format": {"request_body": "dict"},
            "output_format": {"ChangeRequest": "object"},
            "filepath": "src/utils.py"
        },
        {
            "function": "find_replacement_items",
            "description": "Finds suitable replacement items based on the change request",
            "input_format": {"ChangeRequest": "object"},
            "output_format": {"ReplacementItems": "object"},
            "filepath": "src/utils.py"
        },
        {
            "function": "update_bundle_in_database",
            "description": "Updates the bundle in DynamoDB with the new item changes",
            "input_format": {"ReplacementItems": "object"},
            "output_format": {"UpdateConfirmation": "object"},
            "filepath": "src/utils.py"
        },
        {
            "function": "build_response",
            "description": "Builds the response object to be returned by the lambda",
            "input_format": {"UpdateConfirmation": "object"},
            "output_format": {"Response": "object"},
            "filepath": "src/utils.py"
        }
    ]
}
