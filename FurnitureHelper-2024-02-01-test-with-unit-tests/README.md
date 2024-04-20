#Project description:


You build an AI helper to to choose the furniture to customer's apartment. 
Customer starts with writing what room the user wants to furniture, or what speicific space, they can write budget, rooom and goals, color, material.

Our database:
- furniture type, like chair, table, sofa, bed, and each furniture has a type. Which has tags, like size, goals, room. And they have a png picture of bird view of the furniture in a scetch format.
-  all furniture from providers, and each furniture has tags, like color, material, price, size, goals, room.
- layouts - pictures of the furniture in the room, and each layout has description of the furniture_type and quantity, room specification, like living room.

AI service:
- use Openai GPT4 for AI  inetraction.
- use Openai model encoding for vector representation of the text.

When User says what room, and what goals, and what budget, we RAG all the furniture types that can be used, and ask LLM to suggest 4 layouts of the furniture type and quantities.
After that we go in our database of layouts and get the most similar layouts, that were suggested by LLM. And we show them to the user.

User chooses the layout, and we suggest to the user 20 bundles of furniture. 
Getting color palettes - we have 20 default palettes, or if user had color preferences, we get 1-20 palettes based on the color preferences using RAG.
For all palettes we generate up to 20 bundles, where the furniture suggested by color, budget, material. 
Layout has the average price per item which should be used on calculating the weight per item, when we're restricted by budget.

User can ask to change item in the bundle, which should searched by RAG with palette of the bundle, price, material and paginated.
User chooses the bundle, and adds to the cart.


##Architecture:


# Notes:
## We're AI driven company, we use s additional intelligence needed you're using OpenAI GPT-4, 
which is a language model that can be used for text generation. Please think out of the box, when you're seeing unusual tasks.
## We use RAG for searching layouts, and furniture items, using vector representation of the text, 
by getting  embedding from `text-embedding-ada-002`, and OpenSearch as storage.
! You do not need authentication , it's already implemented, please skip that part for while. Imagine you get clear user_id in the request.

1. The best customer experience 
```
Client -> System: provide_room_details(user_str_preferences) -> GPT4: structured preferences -> based on preferences searched layouts by RAG. RETURNS: layout_suggestions
Client -> System: select_layout(layout_id). RETURNS: bundle_suggestions
Client -> System: request_item_change(bundle_id, item_change_request). RETURNS: updated_bundle
Client -> System: add_to_cart(bundle_id). RETURNS: cart_confirmation
```

### 2. Actors and Systems:
Actors and Systems:
- User (Customer)
- API Gateway (Entry point for user requests)
- AWS Lambda (Processes business logic)
- Amazon DynamoDB (Stores data)
- Amazon OpenSearch (stores Vector Data, and makes a similarity search)
- Amazon S3 (Hosts images and static content)
- Amazon EventBridge (Coordinates events)
- Amazon Simple Notification Service (SNS) (Manages notifications)
- Amazon Simple Queue Service (SQS) (Handles message queuing)
- OpenAI GPT-4 (Provides AI interaction and suggestions)

### 3. ALL SEQUENCES OF SYSTEM INTERACTIONS:


#### 3.2. Receive Room Details (User -> API Gateway -> Lambda):
Full business logic: Collect and validate user's room details and preferences, takes user’s input, ask GPT4 to gather details, like color, materials, budget and room, by choosing from our variants.
Any Data Transformations: Convert user input into a structured format for processing.
Storage & Database optimizations: Store user preferences in DynamoDB with efficient indexing. !!! Layouts are stored in OpenSearch.
Upstream Dependencies: User input; example format: string like "living room with budget under 1000 natural materials"
Downstream Dependencies: GPT-4 to get Structured preferences; example format: { "room_type": "living_room", "budget": 1000, "color_preferences": ["blue"], "material": "wood", "goals": ["cozy"] }
Cadence: When user provides room details.
Note:
    - Caching strategies: Cache frequent combinations of preferences.
    - Error handling: Validate input and provide user feedback for incorrect data.
    - Monitoring: Track the types of preferences users submit.
    - Feedback loop for improvement: Use data to refine suggestion algorithms.
    - Database keys: Composite key of user ID and room type.

#### 3.3. Suggest Layouts (Lambda -> OpenAI GPT-4 -> Lambda -> DynamoDB):
Full business logic: Use AI to generate layout suggestions based on user preferences.
Any Data Transformations: Encode preferences into a vector using OpenAI model encoding.
Storage & Database optimizations: Index layouts in DynamoDB for efficient similarity searches.
Upstream Dependencies: Encoded preferences; example format: { "encoded_vector": [0.12, 0.75, ...] }
Downstream Dependencies: Suggested layouts; example format: { "layouts": [{ "layout_id": "layout123", "description": "Cozy living room with a sofa and two chairs" }] }
Cadence: After receiving room details.
Note:
    - Caching strategies: Cache popular layouts.
    - Error handling: Handle AI service outages with fallback recommendations.
    - Monitoring: Use CloudWatch to monitor AI interactions.
    - Feedback loop for improvement: Analyze user choices to improve AI suggestions.
    - Database keys: Layout ID as the primary key.

#### 3.4. Generate Furniture Bundles (Lambda -> DynamoDB -> Lambda):
Full business logic: Create furniture bundles based on the selected layout and user preferences.
Any Data Transformations: Match furniture items with layout requirements and user preferences.
Storage & Database optimizations: Use DynamoDB's query and scan operations efficiently.
Upstream Dependencies: Selected layout and preferences; example format: { "layout_id": "layout123", "budget": 1000, "color_preferences": ["blue"], "material": "wood" }
Downstream Dependencies: Furniture bundles; example format: { "bundles": [{ "bundle_id": "bundle456", "items": [{ "furniture_id": "chair789", "price": 150 }] }] }
Cadence: When user selects a layout.
Note:
    - Caching strategies: Cache bundles for similar preferences.
    - Error handling: Provide alternative suggestions if no exact matches are found.
    - Monitoring: Track bundle generation performance.
    - Feedback loop for improvement: Collect user feedback on bundle satisfaction.
    - Database keys: Bundle ID as the primary key.

#### 3.5. Handle Item Changes (User -> API Gateway -> Lambda -> DynamoDB):
Full business logic: Process user requests to change items in the bundle.
Any Data Transformations: Identify suitable replacements based on user requests.
Storage & Database optimizations: Use DynamoDB global secondary indexes for item attributes.
Upstream Dependencies: User change request; example format: { "bundle_id": "bundle456", "item_to_replace": "chair789", "new_color": "red" }
Downstream Dependencies: Updated bundle; example format: { "bundle_id": "bundle456", "items": [{ "furniture_id": "chair101", "price": 160 }] }
Cadence: When user requests an item change.
Note:
    - Caching strategies: Cache similar change requests.
    - Error handling: Suggest the closest match if an exact match is not available.
    - Monitoring: Monitor the frequency and types of change requests.
    - Feedback loop for improvement: Analyze change requests to improve initial suggestions.
    - Database keys: Furniture ID and attributes as keys.

#### 3.6. Add to Cart (User -> API Gateway -> Lambda -> DynamoDB):
Full business logic: Add the finalized bundle to the user's shopping cart.
Any Data Transformations: N/A
Storage & Database optimizations: Update the user's cart in DynamoDB atomically.
Upstream Dependencies: Finalized bundle; example format: { "bundle_id": "bundle456" }
Downstream Dependencies: Cart confirmation; example format: { "cart_updated": true }
Cadence: When user finalizes the bundle.
Note:
    - Caching strategies: N/A
    - Error handling: Confirm cart update and handle any failures.
    - Monitoring: Track cart updates for successful transactions.
    - Feedback loop for improvement: Ensure a smooth checkout process.
    - Database keys: User ID as the primary key for the cart.

### 4. Any Data/Services are missing?:
- No critical data or services appear to be missing at this stage.

### 5. Suggestions for Improvement:
- Implement a cost optimization strategy by using AWS Lambda reserved concurrency for predictable workloads and AWS Savings Plans for consistent usage.
- Introduce AWS Step Functions to orchestrate complex workflows, improving error handling and reducing the number of Lambda invocations.
- Utilize Amazon CloudFront with S3 for faster delivery of static content and images.
- Explore the use of AWS Lambda@Edge for low-latency user interactions and data processing closer to the user.
- Consider using Amazon Personalize to enhance the recommendation engine with machine learning capabilities.

### 6. Summarize the key points of the architecture and its data flow. Write DETAILED UML sequence diagram with detailed data flow with input and output examples and events, you need to be sure that Junior developer will understand how to implement it.:
```uml
@startuml
actor User
participant "API Gateway" as API
participant "Authentication Lambda" as AuthLambda
participant "Cognito" as Cognito
participant "Preference Lambda" as PrefLambda
participant "DynamoDB" as DB
participant "AI Suggestion Lambda" as AILambda
participant "OpenAI GPT-4" as GPT4
participant "Bundle Generation Lambda" as BundleLambda
participant "Item Change Lambda" as ChangeLambda
participant "Cart Lambda" as CartLambda

User -> API: Provide room details and preferences
API -> PrefLambda: room_details(user_input), like 'i wanna living room with budget under 1000 natural materials'
PrefLambda -> OPENAI_GPT4: get_structured_preferences(user_input), like {'room': 'living_room', 'budget': 1000, 'color_preferences': ['blue'], 'materials': ['wood', 'glass'], 'goals': ['cozy']}
OPENAI_GPT4 -> PrefLambda: parse response and get structured_preferences
PrefLambda -> DB: store_structured_preferences
PrefLambda -> AILambda: suggest_layouts(room_type, materails, budget, color, size, other preferences)
AILambda -> EncodeModel: get_vectorized_encoded_preferences
EncodeModel -> AILambda: vectorized_encoded_preferences
AILambda -> OpenSearch: query_similar_layouts(vectorized_encoded_preferences)
OpenSearch -> AILambda: 4 similar_layouts
AILambda -> User: layout_options

User -> API: Select layout
API -> BundleLambda: generate_bundles(layout_id, preferences)
BundleLambda -> GPT4: Generate 20 bundles, with color palette, and different ideas, but based on user preference. Like colorful, comfortable sofa, sofa-bed, modern, elegant… 
BundleLambda -> OpenSearch: For each bundle query_furniture_items based on the furniture types and bundle’s keywords.
BundleLambda -> Redis: Cache results of each search, user would likely try to change the item. for 1 day
BundleLambda -> User: bundle_options

User -> API: Request item change
API -> ChangeLambda: change_item(bundle_id, item_change_request)
ChangeLambda -> Redis: get_next_item(item_type, bundle_id)
Redis -> ChangeLambda: replacement_items
ChangeLambda -> DB: update_bundle
ChangeLambda -> User: updated_bundle

User -> API: Add to cart
API -> CartLambda: add_to_cart(bundle_id)
CartLambda -> DB: update_cart
DB -> CartLambda: cart_confirmation
CartLambda -> User: cart_updated

@enduml
```


##Lambdas to build:
[
    {
        "lambda_name": "PreferenceLambda",
        "lambda_slug": "preference_lambda",
        "lambda_upstream_dependencies": [
            {
                "name": "API Gateway",
                "event": "room_details",
                "event_details": "User provides room details and preferences as a string."
            }
        ],
        "lambda_downstream_dependencies": [
            {
                "name": "OpenAI GPT-4",
                "event": "get_structured_preferences",
                "event_details": "Converts user input into structured preferences."
            },
            {
                "name": "DynamoDB",
                "event": "store_structured_preferences",
                "event_details": "Stores the structured preferences for future reference."
            }
        ],
        "lambda_full_business_logic": "Collects and validates user's room details and preferences, interacts with GPT-4 to structure the preferences, and stores them in DynamoDB.",
        "lambda_notes": {
            "caching_strategies": "Cache frequent combinations of preferences.",
            "error_handling": "Validate input and provide user feedback for incorrect data.",
            "monitoring": "Track the types of preferences users submit.",
            "metrics_with_feedback_loop": "Use data to refine suggestion algorithms.",
            "database_keys": "Composite key of user ID and room type."
        },
        "lambda_cadence": "Triggered when the user provides room details.",
        "lambda_data_transformations": "Converts user input string into a structured JSON format."
    },
    {
        "lambda_name": "AILambda",
        "lambda_slug": "ai_lambda",
        "lambda_upstream_dependencies": [
            {
                "name": "PreferenceLambda",
                "event": "suggest_layouts",
                "event_details": "Receives structured preferences to suggest layouts."
            }
        ],
        "lambda_downstream_dependencies": [
            {
                "name": "OpenSearch",
                "event": "query_similar_layouts",
                "event_details": "Queries for similar layouts based on vectorized preferences."
            }
        ],
        "lambda_full_business_logic": "Uses AI to generate layout suggestions based on user preferences, encodes preferences into a vector using OpenAI model encoding, and queries OpenSearch for similar layouts.",
        "lambda_notes": {
            "caching_strategies": "Cache popular layouts.",
            "error_handling": "Handle AI service outages with fallback recommendations.",
            "monitoring": "Use CloudWatch to monitor AI interactions.",
            "metrics_with_feedback_loop": "Analyze user choices to improve AI suggestions.",
            "database_keys": "Layout ID as the primary key."
        },
        "lambda_cadence": "Triggered after receiving room details.",
        "lambda_data_transformations": "Encodes preferences into a vector using OpenAI model encoding."
    },
    {
        "lambda_name": "BundleLambda",
        "lambda_slug": "bundle_lambda",
        "lambda_upstream_dependencies": [
            {
                "name": "API Gateway",
                "event": "generate_bundles",
                "event_details": "Receives layout ID and preferences to generate furniture bundles."
            }
        ],
        "lambda_downstream_dependencies": [
            {
                "name": "OpenSearch",
                "event": "query_furniture_items",
                "event_details": "Queries for furniture items based on the furniture types and bundle\u2019s keywords."
            }
        ],
        "lambda_full_business_logic": "Creates furniture bundles based on the selected layout and user preferences, interacts with OpenSearch to find matching furniture items, and caches results.",
        "lambda_notes": {
            "caching_strategies": "Cache bundles for similar preferences.",
            "error_handling": "Provide alternative suggestions if no exact matches are found.",
            "monitoring": "Track bundle generation performance.",
            "metrics_with_feedback_loop": "Collect user feedback on bundle satisfaction.",
            "database_keys": "Bundle ID as the primary key."
        },
        "lambda_cadence": "Triggered when user selects a layout.",
        "lambda_data_transformations": "Matches furniture items with layout requirements and user preferences."
    },
    {
        "lambda_name": "ChangeLambda",
        "lambda_slug": "change_lambda",
        "lambda_upstream_dependencies": [
            {
                "name": "API Gateway",
                "event": "change_item",
                "event_details": "Receives bundle ID and item change request from the user."
            }
        ],
        "lambda_downstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "update_bundle",
                "event_details": "Updates the bundle with the new item changes."
            }
        ],
        "lambda_full_business_logic": "Processes user requests to change items in the bundle, identifies suitable replacements, and updates the bundle in DynamoDB.",
        "lambda_notes": {
            "caching_strategies": "Cache similar change requests.",
            "error_handling": "Suggest the closest match if an exact match is not available.",
            "monitoring": "Monitor the frequency and types of change requests.",
            "metrics_with_feedback_loop": "Analyze change requests to improve initial suggestions.",
            "database_keys": "Furniture ID and attributes as keys."
        },
        "lambda_cadence": "Triggered when user requests an item change.",
        "lambda_data_transformations": "Identifies suitable replacements based on user requests."
    },
    {
        "lambda_name": "CartLambda",
        "lambda_slug": "cart_lambda",
        "lambda_upstream_dependencies": [
            {
                "name": "API Gateway",
                "event": "add_to_cart",
                "event_details": "Receives finalized bundle ID from the user."
            }
        ],
        "lambda_downstream_dependencies": [
            {
                "name": "DynamoDB",
                "event": "update_cart",
                "event_details": "Updates the user's shopping cart with the finalized bundle."
            }
        ],
        "lambda_full_business_logic": "Adds the finalized bundle to the user's shopping cart and confirms the update.",
        "lambda_notes": {
            "caching_strategies": "Not applicable.",
            "error_handling": "Confirm cart update and handle any failures.",
            "monitoring": "Track cart updates for successful transactions.",
            "metrics_with_feedback_loop": "Ensure a smooth checkout process.",
            "database_keys": "User ID as the primary key for the cart."
        },
        "lambda_cadence": "Triggered when user finalizes the bundle.",
        "lambda_data_transformations": "None required."
    }
]