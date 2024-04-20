# AuthenticationLambda
Handles user authentication requests by interfacing with Amazon Cognito.

### Triggers
API Gateway User Authentication Request Triggered when a user attempts to authenticate.

### Downstream Dependencies
Amazon Cognito Authenticate User Validates user credentials and returns authentication token.
##Initial plan:

- calls:
    - main(event) -> Response:
        - extract_authorization_header(event) -> str
        - authenticate_user(authorization_header) -> User
        - generate_auth_token(User) -> str
        - create_success_response(auth_token) -> Response
        - create_error_response(error_message) -> Response
- classes:
    - Response:
        - status_code: int
        - body: str or dict
    - User:
        - user_id: str
        - username: str
        - attributes: dict

##Function calls details

{
    "plan": [
        {
            "function": "extract_authorization_header",
            "description": "Extracts the authorization header from the API Gateway event",
            "input_format": {"event": "dict"},
            "output_format": "str",
            "filepath": "src/utils.py"
        },
        {
            "function": "authenticate_user",
            "description": "Validates the user's credentials with Amazon Cognito",
            "input_format": {"authorization_header": "str"},
            "output_format": "User",
            "filepath": "src/utils.py"
        },
        {
            "function": "generate_auth_token",
            "description": "Generates an authentication token for the user",
            "input_format": {"User": "User"},
            "output_format": "str",
            "filepath": "src/utils.py"
        },
        {
            "function": "create_success_response",
            "description": "Creates a success response object with the authentication token",
            "input_format": {"auth_token": "str"},
            "output_format": "Response",
            "filepath": "src/utils.py"
        },
        {
            "function": "create_error_response",
            "description": "Creates an error response object with the provided error message",
            "input_format": {"error_message": "str"},
            "output_format": "Response",
            "filepath": "src/utils.py"
        }
    ]
}
