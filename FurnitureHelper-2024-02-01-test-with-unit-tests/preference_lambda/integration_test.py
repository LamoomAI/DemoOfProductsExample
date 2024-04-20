import logging
import dotenv

dotenv.load_dotenv()
from lambda_function import lambda_handler

logger = logging.getLogger(__name__)
# Simulated event data
test_event = {}

def test():
    # Runs lambda_handler with test data and AWS role
    response = lambda_handler(test_event, {})
    logger.info("Lambda Response:")
    logger.info(response)

if __name__ == "__main__":
    test()