#Project description:

Please add in existing project the following functionality:

Prompt Tester.
User has prompts available to them. User can go in logs (request & Response from AI Model), and it references on the Context object.
You need to add:
1. User clicks on test prompt with context from log page;
2. Frontend add in get parameter context_id, prompt_id, version. It loads the prompt data and context from the database;
3. When user clicks on test prompt, it sends prompt_data and context_data, prompt_data and context_data could be constantly change, on each test. It returns response from AI Model.
4. User can create behaviours to test prompt. This behaviours are created as, please add for that a database table storing that in json format;
default_behaviour = AIModelsBehaviour(
    attempts=[
        AttemptToCall(
            ai_model=AzureAIModel(
                realm='westus',
                deployment_name="gpt-4-turbo",
                max_tokens=C_128K,
                support_functions=True,
            ),
            weight=100,
        )
    ]
)
5. User need to have a possibility to CRUD behaviours;
6. Please add for that CRUD using best practices for storing secure data; User need to add secrets for AI Models with keys:
AZURE_OPENAI_KEYS={"westus":{"url": "https://", "key": ""}}
OPENAI_ORG=
OPENAI_API_KEY=
7. When user clicks on test prompt, it sends a request to the backend, which sends a request to the AI Model, and returns the result to the user;
The request should contain name of behaviour, prompt_data, context; Backend uses the flow-prompt library to call Openai API;
8. It creates for user api token, which is used to call flow-prompt library; That secret should be automatically deleted after 24 hours; and be not availabel for user through API access;
9. Please reuse for authentication cognitoUserPool. So it means you do not need to add authentication in architecture, it will be made by API GW automatically. Which will be used as authorizer for the API Gateway:
### lambda_stack.ts
```
const userPoolArn = "arn:aws:cognito-idp:us-east-1:471112856175:userpool/us-east-1_QpTOyabdH";
const cognitoUserPool = UserPool.fromUserPoolArn(this, 'CognitoUserPool', userPoolArn);
const cognitoUserPoolsAuthorizer = new CognitoUserPoolsAuthorizer(this, "CognitoUserPoolsAuthorizer", {
    cognitoUserPools: [cognitoUserPool],
    resultsCacheTtl: Duration.seconds(0),
});
props.restApi.root.resourceForPath(props.path).addMethod(
    'GET',
    lambdaIntegration,
    {
        authorizer: cognitoUserPoolsAuthorizer,
        authorizationType: AuthorizationType.COGNITO,
    }
);
```
### lambda_smth.py
in Lambda just simply call:
```
def lambda_handler(event, context):
    logger = setup_logging_for_event(event, metrics_namespace)
    claims = event['requestContext']['authorizer']['claims']
    user_id = claims['sub']
```

10. 
## Databases:
### ddb_stack.ts
```
'ApiTokens', 'env_id', 'secret_key';
'LatestPrompts', 'env_id', 'prompt_id';
'PromptHistory', 'env_id_prompt_id', 'version', {
    additional_indexes: [
    {
        indexName: 'env_id_prompt_id_hash_key',
        partitionKey: { name: 'env_id_prompt_id_hash_key', type: dynamodb.AttributeType.STRING },
        readCapacity: 1,
        writeCapacity: 1,
    }
    ]
});
'Logs', 'env_id_prompt_id', 'timestamp', {typeSk: dynamodb.AttributeType.NUMBER, 
    additional_indexes: [
    {
        indexName: 'env_id',
        partitionKey: { name: 'env_id', type: dynamodb.AttributeType.STRING},
        sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER},
        readCapacity: 1,
        writeCapacity: 1,
    }]
}
);
'Organizations', 'org_id', 'created_tms', {typeSk: dynamodb.AttributeType.NUMBER});
'Environments', 'org_id', 'env_name';
'UserRoles', 'user_id', 'org_id';
'Invitations', 'org_id', 'email';
```

In Logs - there are stored the history of the prompts. 
In LatestPrompts - the latest version of prompt for optimization of the access to the latest version of the prompt.
PromptHistory - prompts with versions ;

11. You need to use flow-prompt library to call Openai API, similar to that:
### call_openai.py
```
flow_prompt = FlowPrompt()

gpt4_behaviour = behaviour.AIModelsBehaviour(
    attempts=[
        AttemptToCall(
            ai_model=AzureAIModel(
                realm='westus',
                deployment_name="gpt-4-turbo",
                max_tokens=C_128K,
                support_functions=True,
            ),
            weight=100,
        ),
    ]
)
from flow_prompt import PipePrompt

prompt = PipePrompt(id=data.prompt_id)
PipePrompt.service_load(data.prompt_data)
result = flow_prompt.call(prompt_to_evaluate_prompt.id, context, gpt4_behaviour)
return result.content

```


##Architecture:
## "UML Sequence Diagram for Prompt Testing System"

### 1. Introduction:
The Prompt Testing System is designed to allow users to interact with AI models by sending prompts and receiving responses. The system also enables users to create, update, delete, and test different behaviors for AI model interactions.

```
Web -> System: authenticate(email, password). RETURNS: JWT token
Web -> System: get_logs(JWT token). RETURNS: logs
Web -> System: test_prompt_with_context(JWT token, context_id, prompt_id, version). RETURNS: AI model response
Web -> System: CRUD_behaviours(JWT token, behaviour_data). RETURNS: success/failure response
Web -> System: add_secrets(JWT token, secrets). RETURNS: success/failure response
Web -> System: test_prompt(JWT token, prompt_data, context_data, behaviour_name). RETURNS: AI model response
```

1.1. Criticize your understanding about business logic:
The business logic seems to be centered around the interaction with AI models using prompts and the ability to define behaviors for these interactions. It is important to ensure that the system is secure, scalable, and provides a seamless user experience. There might be additional considerations such as rate limiting, caching of frequent prompts, and ensuring that the system can handle different AI model providers.

### 2. Detailed data flow:

```
Web -> System: authenticate request -> RETURNS: redirect to cognito_redirect_url;
Cognito -> System: redirect to Web & returns code token; RETURNS: code_token;
System -> Cognito: retrieve get_jwt_token(code_token) & get_user_data(); RETURNS: JWT Token, User data;
Web -> System: get_logs(JWT token)
Web -> System: test_prompt_with_context(JWT token, context_id, prompt_id, version)
Web -> System: CRUD_behaviours(JWT token, behaviour_data)
Web -> System: add_secrets(JWT token, secrets)
Web -> System: test_prompt(JWT token, prompt_data, context_data, behaviour_name)
```

2.1. Criticize your understanding about business logic:
The detailed data flow should account for the possibility of multiple AI model providers and the need to store and manage API keys securely. The system should also be designed to handle potential errors gracefully and provide meaningful feedback to the user.

#### 2.2. What mistakes could make Junior Software developer for that architecture?
- Overlooking security best practices, especially when handling API keys and tokens.
- Not considering scalability and potential bottlenecks in the system.
- Failing to implement proper error handling and logging mechanisms.

#### 2.3. What mistakes doesn't make Principal Software developer for that architecture?
- A Principal Software Developer would ensure that the system is designed with security, scalability, and maintainability in mind.
- They would also ensure that the system is well-documented and that the architecture is flexible enough to accommodate future changes or additional AI model providers.

### 3. ALL SEQUENCES OF SYSTEM INTERACTIONS:

#### 3.1. Authenticate User (Web -> Cognito -> System):
Full business logic: User logs in via the web interface, which redirects to Cognito for authentication. Upon successful authentication, Cognito redirects back to the web interface with a code token, which is then exchanged for a JWT token.
All Data Transformations: Code token to JWT token.
Storage & Database optimizations: Use Cognito for user management and authentication.
Upstream Dependencies: Cognito service.
Downstream Dependencies: JWT token used for subsequent requests.
Cadence: On user login.
Note:
    - Caching strategies: None required for authentication.
    - Error handling: Redirect to error page on failure.
    - Monitoring: Logins should be monitored for unusual activity.
    - Feedback loop for improvement: User feedback on the login process.
    - Database keys: N/A.

#### 3.2 Test Prompt with Context (Web -> System -> AI Model -> System -> Web):
Full business logic: User selects a prompt to test with a specific context from the logs. The system retrieves the prompt and context data from the database and sends it to the AI model. The AI model returns a response, which is then displayed to the user.
Any Data Transformations: Prompt and context data to AI model request format.
Storage & Database optimizations: Cache frequently accessed prompts and contexts.
Upstream Dependencies: DynamoDB for prompt and context retrieval.
Downstream Dependencies: AI model provider (e.g., Azure, OpenAI).
Cadence: On user request.
Note:
    - Caching strategies: Cache prompt and context data.
    - Error handling: Display error message to user on failure.
    - Monitoring: Track AI model response times and errors.
    - Feedback loop for improvement: User feedback on the testing experience.
    - Database keys: 'LatestPrompts', 'PromptHistory'.

#### 3.3 CRUD Behaviours (Web -> System -> DynamoDB):
Full business logic: User can create, read, update, and delete behaviors for AI model interactions. The behaviors are stored in JSON format in a DynamoDB table.
Any Data Transformations: Behavior data to JSON format for storage.
Storage & Database optimizations: Use DynamoDB for flexible JSON storage.
Upstream Dependencies: None.
Downstream Dependencies: Behavior data used for AI model interactions.
Cadence: On user CRUD operations.
Note:
    - Caching strategies: None required.
    - Error handling: Display error message to user on failure.
    - Monitoring: Track CRUD operation success rates.
    - Feedback loop for improvement: User feedback on behavior management.
    - Database keys: New table for behaviors.

#### 3.4 Add Secrets (Web -> System -> Secrets Manager):
Full business logic: User adds API keys for AI models, which are securely stored in AWS Secrets Manager.
Any Data Transformations: None.
Storage & Database optimizations: Use AWS Secrets Manager for secure key storage.
Upstream Dependencies: None.
Downstream Dependencies: API keys used for AI model interactions.
Cadence: On user submission of new keys.
Note:
    - Caching strategies: None required.
    - Error handling: Display error message to user on failure.
    - Monitoring: Track secret addition success rates.
    - Feedback loop for improvement: User feedback on secret management.
    - Database keys: N/A.

#### 3.5 Test Prompt (Web -> System -> AI Model -> System -> Web):
Full business logic: User tests a prompt with the selected behavior. The system retrieves the behavior and secrets, constructs the request, and sends it to the AI model. The AI model returns a response, which is then displayed to the user.
Any Data Transformations: Construct AI model request from prompt, context, and behavior data.
Storage & Database optimizations: Use DynamoDB and Secrets Manager as described.
Upstream Dependencies: DynamoDB for behavior retrieval, Secrets Manager for API keys.
Downstream Dependencies: AI model provider.
Cadence: On user request.
Note:
    - Caching strategies: Cache behavior data.
    - Error handling: Display error message to user on failure.
    - Monitoring: Track AI model response times and errors.
    - Feedback loop for improvement: User feedback on the testing experience.
    - Database keys: 'LatestPrompts', 'PromptHistory', 'ApiTokens'.

### 4. Any Data/Services are missing?:
- Is some data not described how it is retrieved? If yes:
- What data? API tokens retrieval process is not fully described.
- Bias for actions: Suggest using AWS Secrets Manager for secure retrieval of API tokens.
- Add it as a new action/event here below.

#### 4.i+1. Retrieve API Tokens (System -> Secrets Manager):
Full business logic: The system retrieves API tokens from AWS Secrets Manager when needed for AI model interactions.
Any Data Transformations: None.
Storage & Database optimizations: Use AWS Secrets Manager for secure key storage.
Upstream Dependencies: None.
Downstream Dependencies: API tokens used for AI model interactions.
Cadence: On demand, when AI model interactions are initiated.
Note:
    - Caching strategies: None required.
    - Error handling: Log and alert on failure to retrieve tokens.
    - Monitoring: Track token retrieval success rates.
    - Feedback loop for improvement: Monitor for frequent retrieval failures and investigate.
    - Database keys: N/A.

### 5. Suggestions for Improvement:
As a picky customer, I would expect the system to be highly responsive and provide clear feedback on the success or failure of my actions. Improvements could include better error messages, faster load times for logs and prompt testing, and a more intuitive interface for managing behaviors and secrets.

### 6. Summarize the key points of the architecture and its data flow. Write DETAILED UML sequence diagram with detailed data flow with input and output examples and events:

```uml
@startuml
actor User
participant "Web Interface" as Web
participant "AWS Cognito" as Cognito
participant "API Gateway" as API
participant "Lambda Functions" as Lambda
participant "DynamoDB" as DDB
participant "AI Model" as AI
participant "AWS Secrets Manager" as Secrets

User -> Web: Authenticate
Web -> Cognito: Redirect for auth
Cognito -> Web: Return code token
Web -> API: Exchange code token for JWT
API -> Lambda: Validate token
Lambda -> User: Return JWT

User -> Web: Request logs
Web -> API: Get logs (JWT)
API -> Lambda: Fetch logs
Lambda -> DDB: Query 'Logs'
DDB -> Lambda: Return logs
Lambda -> User: Display logs

User -> Web: Test prompt with context
Web -> API: Send test request (JWT, context_id, prompt_id, version)
API -> Lambda: Construct AI request
Lambda -> DDB: Retrieve prompt and context
DDB -> Lambda: Return data
Lambda -> AI: Send prompt
AI -> Lambda: Return response
Lambda -> User: Display AI response

User -> Web: CRUD behaviours
Web -> API: Send CRUD request (JWT, behaviour_data)
API -> Lambda: Process CRUD
Lambda -> DDB: Update 'Behaviours'
DDB -> Lambda: Confirm update
Lambda -> User: Display success/failure

User -> Web: Add secrets
Web -> API: Send secrets (JWT, secrets)
API -> Lambda: Store secrets
Lambda -> Secrets: Save API keys
Secrets -> Lambda: Confirm save
Lambda -> User: Display success/failure

User -> Web: Test prompt
Web -> API: Send test request (JWT, prompt_data, context_data, behaviour_name)
API -> Lambda: Construct AI request
Lambda -> DDB: Retrieve behaviour
DDB -> Lambda: Return behaviour
Lambda -> Secrets: Retrieve API keys
Secrets -> Lambda: Return keys
Lambda -> AI: Send prompt
AI -> Lambda: Return response
Lambda -> User: Display AI response

@enduml
```

This UML sequence diagram outlines the key interactions within the Prompt Testing System, including user authentication, log retrieval, prompt testing with context, CRUD operations for behaviors, secret management, and the actual testing of prompts with AI models. The diagram also shows the flow of data between the user, web interface, API Gateway, Lambda functions, DynamoDB, AI models, and AWS Secrets Manager.

##Lambdas to build:
[
    {
        "lambda_name": "AuthenticationHandler",
        "lambda_slug": "lambda_authentication_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "Web Interface",
                "event": "User Login Attempt",
                "event_details": "User initiates login process through the web interface."
            }
        ],
        "lambda_upstream_dependencies_str": "Web Interface User Login Attempt User initiates login process through the web interface.",
        "lambda_downstream_dependencies": [
            {
                "name": "AWS Cognito",
                "event": "Authentication",
                "event_details": "Exchange code token for JWT and retrieve user data."
            }
        ],
        "lambda_downstream_dependencies_str": "AWS Cognito Authentication Exchange code token for JWT and retrieve user data.",
        "lambda_full_business_logic": "Handles user authentication by interfacing with AWS Cognito to exchange code tokens for JWT tokens and retrieve user data.",
        "lambda_notes": {
            "caching_strategies": "N/A",
            "error_handling": "Redirect to error page on failure and log the event.",
            "monitoring": "Track login attempts, successes, and failures.",
            "metrics_with_feedback_loop": "Monitor authentication latency and failure rates.",
            "database_keys": "N/A"
        },
        "lambda_cadence": "On user login attempt.",
        "lambda_data_transformations": "Code token to JWT token and user data extraction."
    },
    {
        "lambda_name": "PromptManagementHandler",
        "lambda_slug": "lambda_prompt_management_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "Web Interface",
                "event": "Prompt Data Request",
                "event_details": "User requests prompt data and context."
            },
            {
                "name": "Web Interface",
                "event": "CRUD Behaviors",
                "event_details": "User performs CRUD operations on behaviors."
            }
        ],
        "lambda_upstream_dependencies_str": "Web Interface Prompt Data Request User requests prompt data and context.; Web Interface CRUD Behaviors User performs CRUD operations on behaviors.",
        "lambda_downstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "Data Retrieval and Storage",
                "event_details": "Retrieve or store prompt data, context, and behaviors."
            }
        ],
        "lambda_downstream_dependencies_str": "DynamoDB Data Retrieval and Storage Retrieve or store prompt data, context, and behaviors.",
        "lambda_full_business_logic": "Manages prompt data and behaviors, including retrieval, creation, updating, and deletion from DynamoDB.",
        "lambda_notes": {
            "caching_strategies": "Cache frequently accessed prompts and behaviors.",
            "error_handling": "Return error message on failure and log the event.",
            "monitoring": "Track CRUD operations and access patterns.",
            "metrics_with_feedback_loop": "Monitor latency and error rates for CRUD operations.",
            "database_keys": "'LatestPrompts', 'PromptHistory', 'Behaviors'"
        },
        "lambda_cadence": "On user request for prompt data or behavior CRUD operations.",
        "lambda_data_transformations": "CRUD operations on prompt data and behaviors."
    },
    {
        "lambda_name": "PromptTestingHandler",
        "lambda_slug": "lambda_prompt_testing_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "Web Interface",
                "event": "Test Prompt",
                "event_details": "User sends prompt data, context data, and behavior name for testing."
            }
        ],
        "lambda_upstream_dependencies_str": "Web Interface Test Prompt User sends prompt data, context data, and behavior name for testing.",
        "lambda_downstream_dependencies": [
            {
                "name": "AI Model",
                "event": "Invoke AI Model",
                "event_details": "Call AI Model with behavior and return response."
            }
        ],
        "lambda_downstream_dependencies_str": "AI Model Invoke AI Model Call AI Model with behavior and return response.",
        "lambda_full_business_logic": "Handles the testing of prompts by invoking the AI Model with the provided prompt data, context data, and behavior name, and returns the AI model response.",
        "lambda_notes": {
            "caching_strategies": "N/A",
            "error_handling": "Retry mechanism, error logging, and user notification on failure.",
            "monitoring": "Track AI model invocation success and failure rates.",
            "metrics_with_feedback_loop": "Monitor AI model response times and accuracy.",
            "database_keys": "'ApiTokens'"
        },
        "lambda_cadence": "On user request to test a prompt.",
        "lambda_data_transformations": "Invoke AI Model with prompt and behavior data."
    },
    {
        "lambda_name": "AuthenticationHandler",
        "lambda_slug": "lambda_authentication_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "Web Interface",
                "event": "User Login Attempt",
                "event_details": "User initiates login process through the web interface."
            }
        ],
        "lambda_upstream_dependencies_str": "Web Interface User Login Attempt User initiates login process through the web interface.",
        "lambda_downstream_dependencies": [
            {
                "name": "AWS Cognito",
                "event": "Authentication Request",
                "event_details": "Lambda exchanges code token for JWT and retrieves user data."
            }
        ],
        "lambda_downstream_dependencies_str": "AWS Cognito Authentication Request Lambda exchanges code token for JWT and retrieves user data.",
        "lambda_full_business_logic": "Handles user authentication by interfacing with AWS Cognito to exchange code tokens for JWTs and retrieve user data.",
        "lambda_notes": {
            "caching_strategies": "N/A",
            "error_handling": "Redirect to error page on failure, log authentication errors.",
            "monitoring": "Track login attempts, success rates, and authentication errors.",
            "metrics_with_feedback_loop": "User feedback on login process, authentication latency metrics.",
            "database_keys": "N/A"
        },
        "lambda_cadence": "On user login attempt.",
        "lambda_data_transformations": "Code token to JWT, user data retrieval."
    },
    {
        "lambda_name": "PromptManagementHandler",
        "lambda_slug": "lambda_prompt_management_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "Web Interface",
                "event": "Prompt Data Request",
                "event_details": "User requests prompt data and context."
            },
            {
                "name": "Web Interface",
                "event": "CRUD Behaviors",
                "event_details": "User performs create, read, update, delete operations on behaviors."
            }
        ],
        "lambda_upstream_dependencies_str": "Web Interface Prompt Data Request User requests prompt data and context.; Web Interface CRUD Behaviors User performs create, read, update, delete operations on behaviors.",
        "lambda_downstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "Data Retrieval and Storage",
                "event_details": "Lambda queries and updates the 'LatestPrompts', 'PromptHistory', and 'Behaviors' tables."
            }
        ],
        "lambda_downstream_dependencies_str": "DynamoDB Data Retrieval and Storage Lambda queries and updates the 'LatestPrompts', 'PromptHistory', and 'Behaviors' tables.",
        "lambda_full_business_logic": "Manages retrieval, creation, updating, and deletion of prompt data and behaviors in DynamoDB.",
        "lambda_notes": {
            "caching_strategies": "Cache frequently accessed prompts and behaviors.",
            "error_handling": "Return error message on failure, log CRUD operation errors.",
            "monitoring": "Track prompt data and behavior CRUD operation metrics.",
            "metrics_with_feedback_loop": "User feedback on prompt management and behavior CRUD operations.",
            "database_keys": "'LatestPrompts', 'PromptHistory', 'Behaviors'"
        },
        "lambda_cadence": "On user request for prompt data or behavior CRUD operations.",
        "lambda_data_transformations": "CRUD operations on prompt data and behaviors."
    },
    {
        "lambda_name": "AIModelInteractionHandler",
        "lambda_slug": "lambda_ai_model_interaction_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "Web Interface",
                "event": "Test Prompt",
                "event_details": "User sends prompt data, context data, and behavior name for testing."
            }
        ],
        "lambda_upstream_dependencies_str": "Web Interface Test Prompt User sends prompt data, context data, and behavior name for testing.",
        "lambda_downstream_dependencies": [
            {
                "name": "AI Model",
                "event": "Model Invocation",
                "event_details": "Lambda calls the AI Model with behavior and returns the response."
            }
        ],
        "lambda_downstream_dependencies_str": "AI Model Model Invocation Lambda calls the AI Model with behavior and returns the response.",
        "lambda_full_business_logic": "Handles the interaction with the AI Model by sending prompt data and context and returning the model's response.",
        "lambda_notes": {
            "caching_strategies": "N/A",
            "error_handling": "Retry mechanism and error logging for AI Model invocation failures.",
            "monitoring": "Track AI Model invocation success rates and latency.",
            "metrics_with_feedback_loop": "User feedback on AI Model interaction experience.",
            "database_keys": "'ApiTokens'"
        },
        "lambda_cadence": "On user request to test prompt.",
        "lambda_data_transformations": "Invoke AI Model with prompt data and context, process model response."
    },
    {
        "lambda_name": "AuthenticationHandler",
        "lambda_slug": "lambda_authentication_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "AWS Cognito",
                "event": "User Authentication",
                "event_details": "Redirects to Cognito and handles token exchange"
            }
        ],
        "lambda_upstream_dependencies_str": "AWS Cognito User Authentication Redirects to Cognito and handles token exchange",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "Handles user authentication, token validation, and JWT token generation.",
        "lambda_notes": {
            "caching_strategies": "None required for authentication.",
            "error_handling": "Redirect to error page on failure.",
            "monitoring": "Logins should be monitored for unusual activity.",
            "metrics_with_feedback_loop": "User feedback on the login process.",
            "database_keys": "N/A"
        },
        "lambda_cadence": "On user login.",
        "lambda_data_transformations": "Code token to JWT token."
    },
    {
        "lambda_name": "LogsRetrievalHandler",
        "lambda_slug": "lambda_logs_retrieval_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "Query Logs",
                "event_details": "Retrieves logs based on user request"
            }
        ],
        "lambda_upstream_dependencies_str": "DynamoDB Query Logs Retrieves logs based on user request",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "Fetches logs from DynamoDB for the user.",
        "lambda_notes": {
            "caching_strategies": "Cache frequently accessed logs.",
            "error_handling": "Display error message to user on failure.",
            "monitoring": "Track log retrieval times and errors.",
            "metrics_with_feedback_loop": "User feedback on log retrieval experience.",
            "database_keys": "'Logs'"
        },
        "lambda_cadence": "On user request for logs.",
        "lambda_data_transformations": "DynamoDB log entries to user-readable format."
    },
    {
        "lambda_name": "PromptTestingHandler",
        "lambda_slug": "lambda_prompt_testing_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "Retrieve Prompt and Context",
                "event_details": "Gets prompt and context data for testing"
            },
            {
                "name": "AI Model",
                "event": "Send Prompt",
                "event_details": "Sends constructed prompt to AI model"
            }
        ],
        "lambda_upstream_dependencies_str": "DynamoDB Retrieve Prompt and Context Gets prompt and context data for testing; AI Model Send Prompt Sends constructed prompt to AI model",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "Handles testing prompts with context and behaviors, constructs AI model requests, and processes responses.",
        "lambda_notes": {
            "caching_strategies": "Cache behavior data and frequently tested prompts.",
            "error_handling": "Display error message to user on failure.",
            "monitoring": "Track AI model response times and errors.",
            "metrics_with_feedback_loop": "User feedback on the testing experience.",
            "database_keys": "'LatestPrompts', 'PromptHistory', 'Behaviours'"
        },
        "lambda_cadence": "On user request for prompt testing.",
        "lambda_data_transformations": "Prompt, context, and behavior data to AI model request format."
    },
    {
        "lambda_name": "SecretsManagementHandler",
        "lambda_slug": "lambda_secrets_management_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "AWS Secrets Manager",
                "event": "Save API Keys",
                "event_details": "Stores and retrieves API keys for AI models"
            }
        ],
        "lambda_upstream_dependencies_str": "AWS Secrets Manager Save API Keys Stores and retrieves API keys for AI models",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "Manages the addition and retrieval of API keys and secrets for AI model interactions.",
        "lambda_notes": {
            "caching_strategies": "None required.",
            "error_handling": "Display error message to user on failure.",
            "monitoring": "Track secret addition and retrieval success rates.",
            "metrics_with_feedback_loop": "Monitor for frequent retrieval failures and investigate.",
            "database_keys": "N/A"
        },
        "lambda_cadence": "On user action to add or retrieve secrets.",
        "lambda_data_transformations": "None."
    },
    {
        "lambda_name": "AuthenticationHandler",
        "lambda_slug": "lambda_authentication_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "AWS Cognito",
                "event": "User Authentication",
                "event_details": "Handles user authentication and token exchange"
            }
        ],
        "lambda_upstream_dependencies_str": "AWS Cognito User Authentication Handles user authentication and token exchange",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "This lambda handles the exchange of the code token for a JWT after the user is authenticated by Cognito.",
        "lambda_notes": {
            "caching_strategies": "None required for authentication",
            "error_handling": "Redirect to error page on failure",
            "monitoring": "Logins should be monitored for unusual activity",
            "metrics_with_feedback_loop": "User feedback on the login process",
            "database_keys": "N/A"
        },
        "lambda_cadence": "On user login",
        "lambda_data_transformations": "Code token to JWT token"
    },
    {
        "lambda_name": "LogsRetrievalHandler",
        "lambda_slug": "lambda_logs_retrieval_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "Query Logs",
                "event_details": "Retrieves logs based on user request"
            }
        ],
        "lambda_upstream_dependencies_str": "DynamoDB Query Logs Retrieves logs based on user request",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "This lambda fetches logs from DynamoDB for the user to view.",
        "lambda_notes": {
            "caching_strategies": "Cache frequently accessed logs",
            "error_handling": "Display error message to user on failure",
            "monitoring": "Track log retrieval times and errors",
            "metrics_with_feedback_loop": "User feedback on log retrieval experience",
            "database_keys": "'Logs'"
        },
        "lambda_cadence": "On user request for logs",
        "lambda_data_transformations": "None"
    },
    {
        "lambda_name": "PromptTestingHandler",
        "lambda_slug": "lambda_prompt_testing_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "Retrieve Prompt and Context",
                "event_details": "Fetches prompt and context data for testing"
            },
            {
                "name": "AI Model",
                "event": "Send Prompt",
                "event_details": "Sends the constructed prompt to the AI model"
            }
        ],
        "lambda_upstream_dependencies_str": "DynamoDB Retrieve Prompt and Context Fetches prompt and context data for testing; AI Model Send Prompt Sends the constructed prompt to the AI model",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "This lambda handles the testing of prompts with context by sending requests to the AI model and returning the response.",
        "lambda_notes": {
            "caching_strategies": "Cache prompt and context data",
            "error_handling": "Display error message to user on failure",
            "monitoring": "Track AI model response times and errors",
            "metrics_with_feedback_loop": "User feedback on the testing experience",
            "database_keys": "'LatestPrompts', 'PromptHistory'"
        },
        "lambda_cadence": "On user request to test prompt with context",
        "lambda_data_transformations": "Prompt and context data to AI model request format"
    },
    {
        "lambda_name": "BehaviorsCRUDHandler",
        "lambda_slug": "lambda_behaviors_crud_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "CRUD Behaviors",
                "event_details": "Performs create, read, update, delete operations on behaviors"
            }
        ],
        "lambda_upstream_dependencies_str": "DynamoDB CRUD Behaviors Performs create, read, update, delete operations on behaviors",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "This lambda manages CRUD operations for behaviors that define AI model interactions.",
        "lambda_notes": {
            "caching_strategies": "None required",
            "error_handling": "Display error message to user on failure",
            "monitoring": "Track CRUD operation success rates",
            "metrics_with_feedback_loop": "User feedback on behavior management",
            "database_keys": "New table for behaviors"
        },
        "lambda_cadence": "On user CRUD operations for behaviors",
        "lambda_data_transformations": "Behavior data to JSON format for storage"
    },
    {
        "lambda_name": "SecretsManagerHandler",
        "lambda_slug": "lambda_secrets_manager_handler",
        "lambda_upstream_dependencies": [
            {
                "name": "AWS Secrets Manager",
                "event": "Save API Keys",
                "event_details": "Stores API keys securely"
            }
        ],
        "lambda_upstream_dependencies_str": "AWS Secrets Manager Save API Keys Stores API keys securely",
        "lambda_downstream_dependencies": [],
        "lambda_downstream_dependencies_str": "",
        "lambda_full_business_logic": "This lambda handles the addition of new API keys for AI models, storing them securely in AWS Secrets Manager.",
        "lambda_notes": {
            "caching_strategies": "None required",
            "error_handling": "Display error message to user on failure",
            "monitoring": "Track secret addition success rates",
            "metrics_with_feedback_loop": "User feedback on secret management",
            "database_keys": "N/A"
        },
        "lambda_cadence": "On user submission of new keys",
        "lambda_data_transformations": "None"
    }
]