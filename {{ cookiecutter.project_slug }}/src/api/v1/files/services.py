import uuid
from typing import Optional
from typing import Type

from fastapi import UploadFile

from api.v1.files.repositories import FileRepository
from api.v1.files.validators import BaseValidator
from sdk.exceptions.exceptions import make_error
from sdk.responses import ResponseStatus


class FileService:
    repository = FileRepository

    @classmethod
    def get_unique_file_name(cls, file_name: str) -> str:
        """
        Method return unique file name.
        """
        uuid_part = str(uuid.uuid4())[:8]
        return f'{uuid_part}_{file_name}'

    @classmethod
    def get_validator(cls, page_name: str) -> Optional[Type['BaseValidator']]:
        return next(
            filter(
                lambda x: x and hasattr(x, 'page_name') and x.page_name == page_name,
                BaseValidator.validators,
            ),
            None,
        )

    @classmethod
    async def upload(cls, file: UploadFile, page: str) -> str:
        validator = cls.get_validator(page)
        if validator is None:
            raise make_error(
                custom_code=ResponseStatus.INVALID_FILE_PAGE_NAME,
                message='Invalid page name.',
            )
        validator.validate(file)
        file_name = cls.get_unique_file_name(file.filename)
        await cls.repository.tmp_store(file_name, await file.read())
        return file_name

    @classmethod
    async def save(cls, file_name: str) -> str:
        await cls.repository.save(file_name)
        return file_name

    @classmethod
    def exists(cls, file_name: str) -> bool:
        return cls.repository.exists(file_name)
