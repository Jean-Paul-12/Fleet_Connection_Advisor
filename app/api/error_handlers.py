from flask import Flask
from marshmallow import ValidationError as MarshmallowValidationError

from app.utils.exceptions import AppError
from app.utils.response import error_response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return error_response(
            message=error.message,
            error_code=error.error_code,
            status_code=error.status_code,
            details=error.details,
        )

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_error(error: MarshmallowValidationError):
        return error_response(
            message="Validation failed.",
            error_code="validation_error",
            status_code=400,
            details=error.messages,
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response(
            message="Resource not found.",
            error_code="not_found",
            status_code=404,
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        return error_response(
            message="Internal server error.",
            error_code="internal_error",
            status_code=500,
        )
