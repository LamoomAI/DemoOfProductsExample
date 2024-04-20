##Initial plan:

- calls:
    - main(event, context) -> dict:
        - exchange_code_for_token(event['code']) -> str
        - retrieve_user_data(token) -> dict
        - log_event(event, context, result) -> None
- classes:
    - CognitoService:
        - exchange_code_for_token(code: str) -> str
        - retrieve_user_data(token: str) -> dict
    - Logger:
        - log_event(event: dict, context: dict, result: dict) -> None

##Function calls details

{
    "plan": [
        {
            "function": "exchange_code_for_token",
            "description": "Exchanges the code token for a JWT token with AWS Cognito",
            "input_format": {"code": "str"},
            "output_format": "str",
            "filepath": "modules/cognito_service.py"
        },
        {
            "function": "retrieve_user_data",
            "description": "Retrieves user data from AWS Cognito using the JWT token",
            "input_format": {"token": "str"},
            "output_format": "dict",
            "filepath": "modules/cognito_service.py"
        },
        {
            "function": "log_event",
            "description": "Logs the event, context, and result for monitoring purposes",
            "input_format": {"event": "dict", "context": "dict", "result": "dict"},
            "output_format": "None",
            "filepath": "common/locallogging.py"
        },
        {
            "function": "main",
            "description": "Main entry point for the lambda function, orchestrates the authentication process",
            "input_format": {"event": "dict", "context": "dict"},
            "output_format": "dict",
            "filepath": "lambda_authentication_handler.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> CRUDResponse:
        - authenticate_user(event) -> UserID
        - perform_crud_operation(UserID, event['body']) -> CRUDResponse
- classes:
    - PromptData:
        - prompt_id: str
        - prompt_content: str
        - context: dict
    - BehaviorData:
        - behavior_id: str
        - behavior_content: dict
    - CRUDResponse:
        - success: bool
        - message: str
        - data: dict
    - DynamoDBService:
        - get_prompt_data(prompt_id) -> PromptData
        - get_behavior_data(behavior_id) -> BehaviorData
        - save_prompt_data(PromptData) -> bool
        - save_behavior_data(BehaviorData) -> bool
        - delete_prompt_data(prompt_id) -> bool
        - delete_behavior_data(behavior_id) -> bool

##Function calls details

{
    "plan": [
        {
            "function": "authenticate_user",
            "description": "Authenticates the user by extracting the user ID from the event's Cognito claims.",
            "input_format": {"event": "AWS Lambda event object"},
            "output_format": "UserID (str)",
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "perform_crud_operation",
            "description": "Performs the specified CRUD operation on prompt data or behavior data.",
            "input_format": {"UserID": "str", "body": "dict containing operation type and data"},
            "output_format": "CRUDResponse (dict with success, message, and data)",
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "get_prompt_data",
            "description": "Retrieves prompt data from DynamoDB based on the prompt ID.",
            "input_format": {"prompt_id": "str"},
            "output_format": "PromptData (dict)",
            "filepath": "modules/dynamodb_service.py"
        },
        {
            "function": "get_behavior_data",
            "description": "Retrieves behavior data from DynamoDB based on the behavior ID.",
            "input_format": {"behavior_id": "str"},
            "output_format": "BehaviorData (dict)",
            "filepath": "modules/dynamodb_service.py"
        },
        {
            "function": "save_prompt_data",
            "description": "Saves prompt data to DynamoDB.",
            "input_format": {"PromptData": "dict"},
            "output_format": "bool (success status)",
            "filepath": "modules/dynamodb_service.py"
        },
        {
            "function": "save_behavior_data",
            "description": "Saves behavior data to DynamoDB.",
            "input_format": {"BehaviorData": "dict"},
            "output_format": "bool (success status)",
            "filepath": "modules/dynamodb_service.py"
        },
        {
            "function": "delete_prompt_data",
            "description": "Deletes prompt data from DynamoDB based on the prompt ID.",
            "input_format": {"prompt_id": "str"},
            "output_format": "bool (success status)",
            "filepath": "modules/dynamodb_service.py"
        },
        {
            "function": "delete_behavior_data",
            "description": "Deletes behavior data from DynamoDB based on the behavior ID.",
            "input_format": {"behavior_id": "str"},
            "output_format": "bool (success status)",
            "filepath": "modules/dynamodb_service.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> Response:
        - extract_user_identity(event) -> str
        - parse_request_body(event) -> PromptTestRequest
        - load_behavior_config(behavior_name) -> BehaviorConfig
        - call_ai_model(PromptTestRequest, BehaviorConfig) -> AIModelResponse
        - format_response(AIModelResponse) -> Response
- classes:
    - PromptTestRequest:
        - prompt_data: str
        - context_data: str
        - behavior_name: str
    - BehaviorConfig:
        - attempts: list
        - ai_model: dict
    - AIModelResponse:
        - content: str

##Function calls details

{
    "plan": [
        {
            "function": "extract_user_identity",
            "description": "Extracts the user's identity from the request context provided by Cognito.",
            "input_format": {"event": "dict"},
            "output_format": "str",
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "parse_request_body",
            "description": "Parses the incoming request body to extract the prompt test request data.",
            "input_format": {"event": "dict"},
            "output_format": "PromptTestRequest",
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "load_behavior_config",
            "description": "Loads the behavior configuration based on the behavior name provided in the request.",
            "input_format": {"behavior_name": "str"},
            "output_format": "BehaviorConfig",
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "call_ai_model",
            "description": "Calls the AI Model using the flow-prompt library with the prompt and context data.",
            "input_format": {"PromptTestRequest": "PromptTestRequest", "BehaviorConfig": "BehaviorConfig"},
            "output_format": "AIModelResponse",
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "format_response",
            "description": "Formats the AI Model response into a proper HTTP response format.",
            "input_format": {"AIModelResponse": "AIModelResponse"},
            "output_format": "Response",
            "filepath": "lambda_prompt_testing_handler.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> Response:
        - exchange_code_for_token(event.code_token) -> JWTToken
        - retrieve_user_data(JWTToken) -> UserData
        - format_response(JWTToken, UserData) -> Response
- classes:
    - JWTToken:
        - token: str
    - UserData:
        - user_id: str
        - email: str
        - other_attributes: dict
    - Response:
        - jwt_token: JWTToken
        - user_data: UserData

##Function calls details

{
    "plan": [
        {
            "function": "main",
            "description": "Main handler for the lambda_authentication_handler. It processes the code token and retrieves the JWT token and user data.",
            "input_format": {"event": {"code_token": "str"}, "context": "object"},
            "output_format": {"jwt_token": "str", "user_data": "object"},
            "filepath": "lambda_authentication_handler.py"
        },
        {
            "function": "exchange_code_for_token",
            "description": "Exchanges the code token for a JWT token using AWS Cognito.",
            "input_format": {"code_token": "str"},
            "output_format": {"jwt_token": "str"},
            "filepath": "modules/cognito_service.py"
        },
        {
            "function": "retrieve_user_data",
            "description": "Retrieves user data using the JWT token from AWS Cognito.",
            "input_format": {"jwt_token": "str"},
            "output_format": {"user_data": "object"},
            "filepath": "modules/cognito_service.py"
        },
        {
            "function": "format_response",
            "description": "Formats the JWT token and user data into a response object.",
            "input_format": {"jwt_token": "str", "user_data": "object"},
            "output_format": {"response": "object"},
            "filepath": "lambda_authentication_handler.py"
        }
    ]
}##Initial plan:

- calls
    - main(event, context) -> Response:
        - parse_event(event) -> ParsedEvent
        - authenticate_user(ParsedEvent.user_info) -> User
        - perform_crud_operation(User, ParsedEvent.operation, ParsedEvent.data) -> OperationResult
        - format_response(OperationResult) -> Response
- classes:
    - ParsedEvent:
        - user_info: dict
        - operation: str
        - data: dict or list
    - User:
        - user_id: str
        - roles: list
    - OperationResult:
        - success: bool
        - data: dict or None
    - Response:
        - status_code: int
        - body: dict

##Function calls details

{
    "plan": [
        {
            "function": "parse_event",
            "description": "Parses the incoming event to extract necessary information",
            "input_format": {"event": "dict"},
            "output_format": {"user_info": "dict", "operation": "str", "data": "dict or list"},
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "authenticate_user",
            "description": "Authenticates the user using the provided information",
            "input_format": {"user_info": "dict"},
            "output_format": {"user_id": "str", "roles": "list"},
            "filepath": "modules/cognito_service.py"
        },
        {
            "function": "perform_crud_operation",
            "description": "Performs the specified CRUD operation on prompt data or behaviors",
            "input_format": {"User": "User", "operation": "str", "data": "dict or list"},
            "output_format": {"success": "bool", "data": "dict or None"},
            "filepath": "modules/behavior_service.py"
        },
        {
            "function": "format_response",
            "description": "Formats the operation result into a response object",
            "input_format": {"OperationResult": "OperationResult"},
            "output_format": {"status_code": "int", "body": "dict"},
            "filepath": "lambda_prompt_management_handler.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> Response:
        - authenticate_user(event) -> User
        - retrieve_ai_model_keys() -> Dict
        - construct_behavior(behavior_name) -> Behavior
        - invoke_ai_model(prompt_data, context_data, Behavior) -> AIModelResponse
        - log_results(AIModelResponse):
        - return_response(AIModelResponse) -> Response
- classes:
    - User:
        - user_id: str
    - Behavior:
        - name: str
        - attempts: List[Attempt]
    - AIModelResponse:
        - content: str

##Function calls details

{
    "plan": [
        {
            "function": "authenticate_user",
            "description": "Authenticates the user using JWT token from the event object",
            "input_format": {"event": "dict"},
            "output_format": "User",
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "retrieve_ai_model_keys",
            "description": "Retrieves AI Model keys from AWS Secrets Manager",
            "input_format": {},
            "output_format": "dict",
            "filepath": "modules/secrets_manager_service.py"
        },
        {
            "function": "construct_behavior",
            "description": "Constructs a behavior object based on the behavior name",
            "input_format": {"behavior_name": "str"},
            "output_format": "Behavior",
            "filepath": "modules/behavior_service.py"
        },
        {
            "function": "invoke_ai_model",
            "description": "Invokes the AI Model with the prompt data, context data, and behavior",
            "input_format": {"prompt_data": "str", "context_data": "str", "Behavior": "Behavior"},
            "output_format": "AIModelResponse",
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "log_results",
            "description": "Logs the results of the AI Model invocation",
            "input_format": {"AIModelResponse": "AIModelResponse"},
            "output_format": "None",
            "filepath": "common/locallogging.py"
        },
        {
            "function": "return_response",
            "description": "Returns the AI Model's response to the user",
            "input_format": {"AIModelResponse": "AIModelResponse"},
            "output_format": "Response",
            "filepath": "lambda_prompt_testing_handler.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> Response:
        - exchange_code_for_token(event.code) -> JWT
        - get_user_data(JWT) -> User
        - log_event(event, context):
        - handle_error(error) -> Response:
- classes:
    - JWT:
        - token: str
    - User:
        - user_id: str
        - email: str
        - name: str

##Function calls details

{
    "plan": [
        {
            "function": "exchange_code_for_token",
            "description": "Exchanges the code token for a JWT using AWS Cognito",
            "input_format": {"code": "str"},
            "output_format": {"JWT": "str"},
            "filepath": "modules/cognito_service.py"
        },
        {
            "function": "get_user_data",
            "description": "Retrieves user data from AWS Cognito using the JWT",
            "input_format": {"JWT": "str"},
            "output_format": {"User": {"user_id": "str", "email": "str", "name": "str"}},
            "filepath": "modules/cognito_service.py"
        },
        {
            "function": "log_event",
            "description": "Logs the event and context for monitoring purposes",
            "input_format": {"event": "dict", "context": "dict"},
            "output_format": "None",
            "filepath": "common/locallogging.py"
        },
        {
            "function": "handle_error",
            "description": "Handles errors by logging and redirecting to an error page",
            "input_format": {"error": "Exception"},
            "output_format": {"Response": {"statusCode": "int", "body": "str"}},
            "filepath": "lambda_authentication_handler.py"
        }
    ]
}##Initial plan:

- calls
    - main(event, context) -> Response:
        - parse_event(event) -> ParsedEvent
        - handle_prompt_request(ParsedEvent) -> Response
        - handle_behavior_crud(ParsedEvent) -> Response
- classes:
    - ParsedEvent:
        - prompt_id: str
        - context_id: str
        - version: str
        - behavior_json: dict
    - Response:
        - status_code: int
        - body: dict or str

##Function calls details

{
    "plan": [
        {
            "function": "parse_event",
            "description": "Parses the incoming event to extract necessary data",
            "input_format": {"event": "dict"},
            "output_format": {"ParsedEvent": "object"},
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "handle_prompt_request",
            "description": "Handles retrieval of prompt data from DynamoDB",
            "input_format": {"ParsedEvent": "object"},
            "output_format": {"Response": "object"},
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "handle_behavior_crud",
            "description": "Handles CRUD operations for behaviors in DynamoDB",
            "input_format": {"ParsedEvent": "object"},
            "output_format": {"Response": "object"},
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "serialize_response",
            "description": "Serializes the response data for the Web Interface",
            "input_format": {"status_code": "int", "body": "dict or str"},
            "output_format": {"Response": "object"},
            "filepath": "common/utils.py"
        },
        {
            "function": "log_error",
            "description": "Logs errors and exceptions",
            "input_format": {"error": "Exception"},
            "output_format": "None",
            "filepath": "common/locallogging.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> Response:
        - validate_request(event) -> ValidatedRequest
        - retrieve_secrets() -> AIModelCredentials
        - construct_behavior(behavior_name) -> AIModelBehavior
        - invoke_ai_model(prompt_data, context_data, AIModelBehavior) -> AIModelResponse
        - log_interaction(prompt_data, context_data, AIModelResponse):
- classes:
    - ValidatedRequest:
        - prompt_data: str
        - context_data: str
        - behavior_name: str
    - AIModelCredentials:
        - url: str
        - key: str
    - AIModelBehavior:
        - attempts: list
    - AIModelResponse:
        - content: str

##Function calls details

{
    "plan": [
        {
            "function": "validate_request",
            "description": "Validates the incoming request for required parameters",
            "input_format": {"event": "dict"},
            "output_format": "ValidatedRequest",
            "filepath": "lambda_ai_model_interaction_handler.py"
        },
        {
            "function": "retrieve_secrets",
            "description": "Retrieves AI Model credentials from AWS Secrets Manager",
            "input_format": {},
            "output_format": "AIModelCredentials",
            "filepath": "modules/secrets_manager_service.py"
        },
        {
            "function": "construct_behavior",
            "description": "Constructs an AI Model behavior object based on the behavior name",
            "input_format": {"behavior_name": "str"},
            "output_format": "AIModelBehavior",
            "filepath": "modules/behavior_service.py"
        },
        {
            "function": "invoke_ai_model",
            "description": "Invokes the AI Model with the prompt data, context data, and behavior",
            "input_format": {
                "prompt_data": "str",
                "context_data": "str",
                "AIModelBehavior": "AIModelBehavior"
            },
            "output_format": "AIModelResponse",
            "filepath": "lambda_ai_model_interaction_handler.py"
        },
        {
            "function": "log_interaction",
            "description": "Logs the interaction with the AI Model including request and response data",
            "input_format": {
                "prompt_data": "str",
                "context_data": "str",
                "AIModelResponse": "AIModelResponse"
            },
            "output_format": {},
            "filepath": "common/locallogging.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> AuthenticationResponse:
        - validate_token(event) -> Token:
        - get_user_data(Token) -> User:
        - generate_jwt(User) -> str:
- classes:
    - AuthenticationResponse:
        - jwt: str
        - user: User
    - User:
        - id: str
        - email: str
        - roles: List[str]
    - Token:
        - token: str

##Function calls details

{
    "plan": [
        {
            "function": "validate_token",
            "description": "Validates the code token received from AWS Cognito",
            "input_format": {"event": "dict"},
            "output_format": {"token": "Token"},
            "filepath": "lambda_authentication_handler.py"
        },
        {
            "function": "get_user_data",
            "description": "Retrieves user data from AWS Cognito using the validated token",
            "input_format": {"token": "Token"},
            "output_format": {"user": "User"},
            "filepath": "lambda_authentication_handler.py"
        },
        {
            "function": "generate_jwt",
            "description": "Generates a JWT token for the authenticated user",
            "input_format": {"user": "User"},
            "output_format": "str",
            "filepath": "lambda_authentication_handler.py"
        },
        {
            "function": "main",
            "description": "Main entry point for the lambda function, orchestrates the authentication process",
            "input_format": {"event": "dict", "context": "dict"},
            "output_format": {"AuthenticationResponse": "dict"},
            "filepath": "lambda_authentication_handler.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> Response:
        - parse_event(event) -> ParsedEvent
        - handle_operation(ParsedEvent) -> OperationResult:
            - perform_crud_operation(ParsedEvent) -> CRUDResult
        - construct_response(OperationResult) -> Response
- classes:
    - ParsedEvent:
        - operation: str
        - data: dict
    - OperationResult:
        - success: bool
        - message: str
        - data: dict or None
    - CRUDResult:
        - success: bool
        - message: str
        - data: dict or None
    - Response:
        - statusCode: int
        - body: str

##Function calls details

{
    "plan": [
        {
            "function": "parse_event",
            "description": "Parses the incoming event to extract the operation type and data",
            "input_format": {"event": "dict"},
            "output_format": {"operation": "str", "data": "dict"},
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "handle_operation",
            "description": "Determines the CRUD operation to perform based on the parsed event",
            "input_format": {"ParsedEvent": "object"},
            "output_format": {"OperationResult": "object"},
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "perform_crud_operation",
            "description": "Executes the CRUD operation on DynamoDB and returns the result",
            "input_format": {"ParsedEvent": "object"},
            "output_format": {"CRUDResult": "object"},
            "filepath": "modules/dynamodb_service.py"
        },
        {
            "function": "construct_response",
            "description": "Constructs the HTTP response to be returned to the API Gateway",
            "input_format": {"OperationResult": "object"},
            "output_format": {"Response": "object"},
            "filepath": "lambda_prompt_management_handler.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> Response:
        - validate_jwt_token(event) -> UserClaims
        - retrieve_prompt_data(prompt_id) -> PromptData
        - retrieve_context_data(context_id) -> ContextData
        - construct_ai_model_request(PromptData, ContextData, behavior_name) -> AIModelRequest
        - invoke_ai_model(AIModelRequest) -> AIModelResponse
        - format_response(AIModelResponse) -> UserResponse
- classes:
    - UserClaims:
        - user_id: str
    - PromptData:
        - prompt_id: str
        - prompt_text: str
    - ContextData:
        - context_id: str
        - context_text: str
    - AIModelRequest:
        - prompt_text: str
        - context_text: str
        - behavior: dict
    - AIModelResponse:
        - response_text: str
    - UserResponse:
        - result: str

##Function calls details

{
    "plan": [
        {
            "function": "validate_jwt_token",
            "description": "Validates the JWT token to authenticate the user and extract claims.",
            "input_format": {"event": "AWS Lambda event object"},
            "output_format": {"user_id": "str"},
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "retrieve_prompt_data",
            "description": "Retrieves prompt data from DynamoDB using the prompt_id.",
            "input_format": {"prompt_id": "str"},
            "output_format": {"prompt_text": "str"},
            "filepath": "modules/behavior_service.py"
        },
        {
            "function": "retrieve_context_data",
            "description": "Retrieves context data from DynamoDB using the context_id.",
            "input_format": {"context_id": "str"},
            "output_format": {"context_text": "str"},
            "filepath": "modules/behavior_service.py"
        },
        {
            "function": "construct_ai_model_request",
            "description": "Constructs the request to be sent to the AI model using prompt data, context data, and behavior.",
            "input_format": {
                "PromptData": {"prompt_text": "str"},
                "ContextData": {"context_text": "str"},
                "behavior_name": "str"
            },
            "output_format": {"AIModelRequest": "dict"},
            "filepath": "lambda_prompt_testing_handler.py"
        },
        {
            "function": "invoke_ai_model",
            "description": "Invokes the AI model with the constructed request and captures the response.",
            "input_format": {"AIModelRequest": "dict"},
            "output_format": {"AIModelResponse": "dict"},
            "filepath": "modules/behavior_service.py"
        },
        {
            "function": "format_response",
            "description": "Formats the AI model response into a user-friendly format.",
            "input_format": {"AIModelResponse": "dict"},
            "output_format": {"UserResponse": "dict"},
            "filepath": "lambda_prompt_testing_handler.py"
        }
    ]
}##Initial plan:

- calls:
    - main(event, context) -> dict:
        - validate_authentication_request(event) -> AuthenticationRequest
        - exchange_code_for_jwt(AuthenticationRequest) -> AuthenticationResponse
        - log_authentication_attempt(AuthenticationRequest, AuthenticationResponse):
- classes:
    - AuthenticationRequest:
        - code_token: str
    - AuthenticationResponse:
        - jwt_token: str
        - user_data: dict

##Function calls details

{
    "plan": [
        {
            "function": "validate_authentication_request",
            "description": "Validates the incoming authentication request and extracts the code token",
            "input_format": {"event": "dict"},
            "output_format": {"code_token": "str"},
            "filepath": "lambda_authentication_handler.py"
        },
        {
            "function": "exchange_code_for_jwt",
            "description": "Exchanges the code token with AWS Cognito for a JWT",
            "input_format": {"code_token": "str"},
            "output_format": {"jwt_token": "str", "user_data": "dict"},
            "filepath": "lambda_authentication_handler.py"
        },
        {
            "function": "log_authentication_attempt",
            "description": "Logs the authentication attempt and its outcome",
            "input_format": {"AuthenticationRequest": "AuthenticationRequest", "AuthenticationResponse": "AuthenticationResponse"},
            "output_format": "None",
            "filepath": "lambda_authentication_handler.py"
        }
    ]
}##Initial plan:

- calls
    - main(event, context) -> CRUDResponse:
        - parse_event(event) -> ParsedEvent
        - perform_crud_operation(ParsedEvent) -> CRUDResponse
- classes:
    - ParsedEvent:
        - operation: str
        - prompt_data: PromptData
        - behavior_data: BehaviorData
    - PromptData:
        - prompt_id: str
        - prompt_text: str
        - ...
    - BehaviorData:
        - behavior_id: str
        - behavior_json: dict
        - ...
    - CRUDResponse:
        - success: bool
        - message: str
        - data: dict

##Function calls details

{
    "plan": [
        {
            "function": "main",
            "description": "Entry point for the lambda function, orchestrates the CRUD operations.",
            "input_format": {"event": "AWS Lambda event object", "context": "AWS Lambda context object"},
            "output_format": "CRUDResponse",
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "parse_event",
            "description": "Parses the incoming event to extract the operation type and data.",
            "input_format": {"event": "dict"},
            "output_format": "ParsedEvent",
            "filepath": "lambda_prompt_management_handler.py"
        },
        {
            "function": "perform_crud_operation",
            "description": "Performs the specified CRUD operation on prompt data or behavior data.",
            "input_format": {"ParsedEvent": "ParsedEvent"},
            "output_format": "CRUDResponse",
            "filepath": "lambda_prompt_management_handler.py"
        }
    ]
}