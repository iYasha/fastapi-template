from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from sdk.exceptions.exceptions import AppException
from sdk.exceptions.exceptions import ExternalServiceError
from sdk.exceptions.handlers import app_exception_handler
from sdk.exceptions.handlers import external_service_exception_handler
from sdk.exceptions.handlers import fastapi_exception_error_handler
from sdk.exceptions.handlers import request_validation_exception_handler
from sdk.exceptions.handlers import unexpected_exception_handler

exception_handler_mapping = {
    ExternalServiceError: external_service_exception_handler,
    RequestValidationError: request_validation_exception_handler,
    AppException: app_exception_handler,
    HTTPException: fastapi_exception_error_handler,
    Exception: unexpected_exception_handler,
}
