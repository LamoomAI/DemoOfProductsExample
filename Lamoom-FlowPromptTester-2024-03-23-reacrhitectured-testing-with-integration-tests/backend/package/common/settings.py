import os

def parse_boolean(value: str) -> bool:
    return value.lower() in ["true", "1"]

TEST_EVENTS_TABLE_NAME = os.environ.get("TEST_EVENTS_TABLE_NAME", "test_events")
LAST_TEST_EVENTS_TABLE_NAME = os.environ.get("LAST_TEST_EVENTS_TABLE_NAME", "last_test_event")
IS_QA_ENV = parse_boolean(os.environ.get("IS_QA_ENV"))

# Secret key for encoding JWT tokens. Should be kept secret and secure.
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')

# Algorithm used for encoding JWT tokens.
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

# Expiration time for JWT tokens in seconds.
JWT_EXPIRATION_DELTA_SECONDS = int(os.environ.get('JWT_EXPIRATION_DELTA_SECONDS', 3600))

# Define the DynamoDB table name for prompts
PROMPTS_TABLE_NAME = os.environ.get("PROMPTS_TABLE_NAME", "YourDynamoDBTableNameForPrompts")