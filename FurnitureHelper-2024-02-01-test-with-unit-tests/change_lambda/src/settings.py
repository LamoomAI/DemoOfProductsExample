import os

# Add the DynamoDB table name to the settings
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'default_table_name')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')