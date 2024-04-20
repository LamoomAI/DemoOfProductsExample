class CustomError(Exception):
    STATUS_CODE = 500
    ERROR_TYPE = "custom_error"
    MESSAGE = "Internal error occurred"

    def __init__(self, message=None, status_code=None, error_type=None):
        self.status_code = self.STATUS_CODE
        self.error_type = self.ERROR_TYPE
        self.message = self.MESSAGE

        if status_code is not None and isinstance(status_code, int):
            self.status_code = status_code
        if error_type:
            self.error_type = error_type
        if message:
            self.message = message
        super().__init__(self.message)

class ValidationError(CustomError):
    STATUS_CODE = 400
    ERROR_TYPE = "validation_error"
    MESSAGE = "Validation error occurred"

class AIModelInvocationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class UnauthorizedError(CustomError):
    STATUS_CODE = 403
    ERROR_TYPE = "unauthorized_error"
    MESSAGE = "User does not have permission to perform this operation."