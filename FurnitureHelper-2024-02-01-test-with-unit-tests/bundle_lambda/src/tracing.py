import logging
import uuid

LAMBDA_FORMAT = '[%(asctime)s] [TRACE_ID=%(trace_id)s] %(levelname)s - %(message)s'

def get_trace_id(event):
    trace_id = event.get('trace_id', None)
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    return trace_id

class LambdaFormatter(logging.Formatter):
    def format(self, record):
        return super(LambdaFormatter, self).format(record)

def setup_logging(event):
    logger = logging.getLogger()
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    trace_id = get_trace_id(event)

    formatter = LambdaFormatter(LAMBDA_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger = logging.LoggerAdapter(logger, {'trace_id': trace_id})
    logger.info("This is a log message with a trace_id.")