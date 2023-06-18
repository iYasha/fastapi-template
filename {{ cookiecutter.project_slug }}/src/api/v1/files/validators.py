from fastapi import UploadFile

from sdk.exceptions.exceptions import make_error
from sdk.responses import ResponseStatus


class BaseValidator:
    validators = []
    page_name: str

    @classmethod
    def validate(cls, file: UploadFile) -> None:
        """
        Method raise exception if file is invalid.
        """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        BaseValidator.validators.append(cls)


class AvatarValidator(BaseValidator):
    page_name = 'avatar'

    @classmethod
    def validate(cls, file: UploadFile) -> None:
        max_mb_file_size = 5
        if file.content_type not in ['image/jpeg', 'image/png']:
            raise make_error(
                custom_code=ResponseStatus.INVALID_FILE_TYPE,
                message='Invalid file type. Only jpeg and png are allowed.',
            )
        if file.spool_max_size > max_mb_file_size * 1024**2:
            raise make_error(
                custom_code=ResponseStatus.INVALID_FILE_SIZE,
                message=f'Invalid file size. Max size is {max_mb_file_size} MB.',
            )
