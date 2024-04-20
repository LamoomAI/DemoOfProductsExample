import logging
import uuid


LAMBDA_FORMAT = '[%(asctime)s] [TRACE_ID=%(trace_id)s] %(levelname)s - %(message)s'


def get_trace_id(event):
    # Check if trace_id is present in the event
    trace_id = event.get('trace_id', None)
    if trace_id is None:
        # Generate a new trace_id if not present
        trace_id = str(uuid.uuid4())
    return trace_id


class LambdaFormatter(logging.Formatter):
    def format(self, record):
        # The trace_id is now a part of the record
        return super(LambdaFormatter, self).format(record)


def setup_logging(event):
        # Configure logging
    logger = logging.getLogger()
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    # Get or generate trace_id
    trace_id = get_trace_id(event)

    # Configure the custom formatter with the trace_id
    formatter = LambdaFormatter(LAMBDA_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Set the trace_id in the log record
    logger = logging.LoggerAdapter(logger, {'trace_id': trace_id})
    logger.info("This is a log message with a trace_id.")
