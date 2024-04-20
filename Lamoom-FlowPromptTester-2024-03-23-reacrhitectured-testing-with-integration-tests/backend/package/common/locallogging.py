import json
import logging
import uuid
import traceback
from .utils import get_trace_id_from_event
from modules.behavior_service import AIModelResponse

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        json_record = {
            'logger': record.name,
            'level': record.levelname,
            'filename': record.pathname,
            'func': record.funcName,
            'lineno': record.lineno,
            'asctime': (
                self.formatTime(record, self.datefmt)
                if hasattr(record, 'asctime')
                else ''
            ),
            'message': record.message,
        }
        if hasattr(record, 'namespace'):
            json_record['namespace'] = record.namespace
        if hasattr(record, 'trace_id'):
            json_record['trace_id'] = record.trace_id

        if record.exc_info:
            exc_class_module = record.exc_info[1].__class__.__module__
            exc_class_name = record.exc_info[1].__class__.__name__
            exc_type = exc_class_module + '.' + exc_class_name

            json_record['exc'] = {
                'traceback': self.formatException(record.exc_info),
                'value': str(record.exc_info[1]),
                'type': exc_type,
            }

        return json.dumps(json_record)


def get_trace_id(event):
    # Check if trace_id is present in the event
    trace_id = event.get('trace_id', None)
    if trace_id is None:
        # Generate a new trace_id if not present
        trace_id = str(uuid.uuid4())
        event['trace_id'] = trace_id
    return trace_id


class LambdaFormatter(logging.Formatter):
    def format(self, record):
        # The trace_id is now a part of the record
        return super(LambdaFormatter, self).format(record)


def setup_logging_for_event(event, namespace: str):
    # Configure logging
    logger = logging.getLogger()
    # Get or generate trace_id
    trace_id = get_trace_id(event)
    event['namespace'] = namespace
    # Set the trace_id and namespace in the log record
    logger = logging.LoggerAdapter(logger, {'trace_id': trace_id, 'namespace': namespace})
    try:
        logger.info(json.dumps(event)[:10_000])
    except Exception as e:
        logger.exception(e)
    return logger


def setup_logging(namespace: str):
    # Configure logging
    logger = logging.getLogger()
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    # Configure the custom formatter with the trace_id
    formatter = JsonFormatter()  # Use JsonFormatter here
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Set the trace_id and namespace in the log record
    logger = logging.LoggerAdapter(logger, {'namespace': namespace})
    return logger

# Configure the logger
logger = setup_logging('lambda_error_logging')

def log_error(error: Exception):
    """
    Logs errors and exceptions with the trace_id if available.

    :param error: The exception object to log.
    """
    try:
        # Attempt to retrieve a trace_id from the error object, if it has one
        trace_id = getattr(error, 'trace_id', 'N/A')

        # Log the error message with the trace_id
        logger.error(f"Error occurred with trace_id: {trace_id} - {str(error)}")

        # Log the stack trace for detailed debugging information
        logger.error(f"Stack Trace: {traceback.format_exc()}")

    except Exception as log_error_exception:
        # If an error occurs while logging, log that error as well (but without causing a loop)
        logger.error(f"An error occurred while logging an error: {log_error_exception}")
        logger.error(f"Original error: {error}")
        logger.error(f"Original stack trace: {traceback.format_exc(limit=2)}")  # Limit stack trace to prevent large logs

def log_results(ai_model_response: AIModelResponse, event: dict):
    """
    Logs the results of the AI Model invocation.

    :param ai_model_response: The response object from the AI Model.
    :param event: The event object containing the trace_id.
    """
    # Extract the content from the AIModelResponse object
    response_content = ai_model_response.content

    # Retrieve or generate a trace_id
    trace_id = get_trace_id_from_event(event) if 'trace_id' in event else str(uuid.uuid4())

    # Construct the log message
    log_message = {
        "trace_id": trace_id,
        "ai_model_response": response_content
    }

    # Log the message with structured logging
    logger.info(f"AI Model Response: {log_message}")