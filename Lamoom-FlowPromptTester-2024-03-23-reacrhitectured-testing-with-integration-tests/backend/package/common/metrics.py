from datetime import datetime
import logging
import boto3
from common.constants import CLOUDWATCH_NAMESPACE

cloudwatch = boto3.client("cloudwatch")
logger = logging.getLogger(__name__)


def send_metric_to_cloudwatch(error_type, metric_value):
    try:
        cloudwatch.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=[
                {
                    "MetricName": error_type,
                    "Timestamp": datetime.now(),
                    "Value": metric_value,
                    "Unit": "Count",
                }
            ],
        )
    except Exception as error:
        logger.exception(f"Failed to send metric to CloudWatch: {error}")
