import logging
from typing import List
from src.utils import UserPreferences
from src.errors import ValidationError
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

def get_search_client():
    host = 'your-opensearch-cluster-endpoint'  # e.g., search-mydomain.us-west-1.es.amazonaws.com
    region = 'us-west-1'  # e.g., us-west-1
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    # OpenSearch client
    search_client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return search_client

search_client = get_search_client()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def query_opensearch(layout_id: str, user_preferences: UserPreferences) -> List[dict]:
    try:
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"layout_id": layout_id}},
                        {"range": {"price": {"lte": user_preferences.budget}}}
                    ],
                    "filter": [
                        {"terms": {"color": user_preferences.color_preferences}},
                        {"terms": {"material": user_preferences.material_preferences}}
                    ]
                }
            }
        }

        logger.info(f"Sending query to OpenSearch: {query}")

        response = search_client.search(
            body=query,
            index="furniture_index"
        )

        logger.info(f"Received response from OpenSearch: {response}")

        hits = response['hits']['hits']
        furniture_items = [
            {
                'furniture_id': hit['_id'],
                'type': hit['_source']['type'],
                'color': hit['_source']['color'],
                'material': hit['_source']['material'],
                'price': hit['_source']['price']
            }
            for hit in hits
        ]

        return furniture_items

    except Exception as e:
        logger.exception("Failed to query OpenSearch")
        raise ValidationError(f"Failed to query OpenSearch: {str(e)}", status_code=500)