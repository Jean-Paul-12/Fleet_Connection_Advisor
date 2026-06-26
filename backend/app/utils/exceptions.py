class AppError(Exception):
    status_code = 500
    error_code = "internal_error"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AppError):
    status_code = 400
    error_code = "validation_error"


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ExternalServiceError(AppError):
    status_code = 502
    error_code = "external_service_error"


class DatabaseError(AppError):
    status_code = 500
    error_code = "database_error"
