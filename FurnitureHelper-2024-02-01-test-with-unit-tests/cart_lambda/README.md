# CartLambda
Adds the finalized bundle to the user's shopping cart and confirms the update.

### Triggers
API Gateway add_to_cart Receives finalized bundle ID from the user.

### Downstream Dependencies
DynamoDB update_cart Updates the user's shopping cart with the finalized bundle.
##Initial plan:

- calls:
    - main(event, context) -> Response:
        - authenticate_user(event) -> User
        - get_bundle_id(event) -> str
        - update_shopping_cart(User, bundle_id) -> bool
        - generate_confirmation_response(update_status) -> Response
- classes:
    - User:
        - user_id: str
    - Bundle:
        - bundle_id: str
        - items: list
    - Cart:
        - user_id: str
        - bundles: list
    - Response:
        - status: str
        - message: str

##Function calls details

{
    "plan": [
        {
            "function": "authenticate_user",
            "description": "Authenticates the user making the request",
            "input_format": {"event": "object"},
            "output_format": "User",
            "filepath": "src/utils.py"
        },
        {
            "function": "get_bundle_id",
            "description": "Extracts the bundle ID from the event",
            "input_format": {"event": "object"},
            "output_format": "str",
            "filepath": "src/utils.py"
        },
        {
            "function": "update_shopping_cart",
            "description": "Updates the user's shopping cart with the new bundle",
            "input_format": {"User": "User", "bundle_id": "str"},
            "output_format": "bool",
            "filepath": "src/cart.py"
        },
        {
            "function": "generate_confirmation_response",
            "description": "Generates a response confirming the cart update",
            "input_format": {"update_status": "bool"},
            "output_format": "Response",
            "filepath": "src/utils.py"
        }
    ]
}
