# Custom Error Classes
class CustomError(Exception):
    STATUS_CODE = 500
    ERROR_TYPE = "custom_error"
    MESSAGE = "Internal error occurred"

    def __init__(self, message=None, status_code=None, error_type=None, trace_id=None):
        self.status_code = status_code if status_code is not None else self.STATUS_CODE
        self.error_type = error_type if error_type else self.ERROR_TYPE
        self.message = message if message else self.MESSAGE
        self.trace_id = trace_id  # Added trace_id to store the trace information
        super().__init__(self.message)

    def to_dict(self):
        return {
            'message': self.message,
            'status_code': self.status_code,
            'error_type': self.error_type,
            'trace_id': self.trace_id  # Include trace_id in the response
        }

class ValidationError(CustomError):
    STATUS_CODE = 400
    ERROR_TYPE = "validation_error"
    MESSAGE = "Validation error occurred"

class InternalError(CustomError):
    STATUS_CODE = 500
    ERROR_TYPE = "internal_error"