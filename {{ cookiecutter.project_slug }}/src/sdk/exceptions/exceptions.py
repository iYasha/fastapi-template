from typing import Optional

from httpx import Response

from sdk.responses import FieldErrorSchema
from sdk.responses import FieldErrorsSchema
from sdk.responses import ResponseStatus

__all__ = ['AppException', 'make_error']


class AppException(Exception):
    """Базовый класс ошибок"""

    app_code: ResponseStatus
    message: Optional[str]
    field_errors: Optional[FieldErrorsSchema]

    def __init__(
        self,
        custom_code: ResponseStatus,
        message: Optional[str] = None,
        field_errors: FieldErrorsSchema = None,
    ) -> None:
        self.message = message
        self.custom_code = custom_code
        self.field_errors = field_errors


class ExternalServiceError(Exception):
    """Ошибка внешнего сервиса"""

    service_name = 'unknown'

    def __init__(self, *args, response: Response) -> None:
        super().__init__(*args)
        self.response = response


def make_error(
    custom_code: ResponseStatus,
    message: Optional[str] = None,
    **details,
) -> AppException:
    """Raise HTTP exception with custom response."""

    return AppException(
        custom_code=custom_code,
        message=message,
        field_errors=[FieldErrorSchema(field=field, message=details[field]) for field in details],
    )
