from common.metrics import send_metric_to_cloudwatch
from unittest.mock import patch


class MockCloudWatch:
    def put_metric_data(self, Namespace, MetricData):
        pass


def test_send_metric_to_cloudwatch_success():
    with patch("src.metrics.cloudwatch", new=MockCloudWatch()):
        send_metric_to_cloudwatch("TestError", 1)
