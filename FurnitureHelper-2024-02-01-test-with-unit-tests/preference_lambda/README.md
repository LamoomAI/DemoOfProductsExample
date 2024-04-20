# PreferenceLambda
Collects and validates user's room details and preferences, interacts with GPT-4 to structure the preferences, and stores them in DynamoDB.

### Triggers
API Gateway room_details User provides room details and preferences as a string.

### Downstream Dependencies
OpenAI GPT-4 get_structured_preferences Converts user input into structured preferences.; DynamoDB store_structured_preferences Stores the structured preferences for future reference.
##Initial plan:

- calls:
    - main(event, context) -> Response:
        - authenticate_user(event.headers.Authorization) -> User
        - validate_input(event.body) -> ValidatedInput
        - get_structured_preferences(ValidatedInput) -> StructuredPreferences:
            - call_gpt4_api(ValidatedInput)
        - store_preferences(User, StructuredPreferences)
- classes:
    - User:
        - user_id: str
    - ValidatedInput:
        - room_details: str
        - preferences: dict
    - StructuredPreferences:
        - preferences: dict
    - GPT4Service:
        - call_api(input: str) -> dict
    - DynamoDBService:
        - store_data(user_id: str, data: dict)

##Function calls details

{
    "plan": [
        {
            "function": "authenticate_user",
            "description": "Authenticates the user based on the provided authorization header",
            "input_format": {"authorization_header": "string"},
            "output_format": "User",
            "filepath": "src/utils.py"
        },
        {
            "function": "validate_input",
            "description": "Validates the user's input and converts it into a structured format",
            "input_format": {"user_input": "string"},
            "output_format": "ValidatedInput",
            "filepath": "src/utils.py"
        },
        {
            "function": "call_gpt4_api",
            "description": "Calls the GPT-4 API to get structured preferences from the user's input",
            "input_format": {"validated_input": "ValidatedInput"},
            "output_format": "StructuredPreferences",
            "filepath": "src/gpt4_service.py"
        },
        {
            "function": "store_preferences",
            "description": "Stores the structured preferences in DynamoDB",
            "input_format": {"user": "User", "structured_preferences": "StructuredPreferences"},
            "output_format": "None",
            "filepath": "src/dynamodb_service.py"
        }
    ]
}
