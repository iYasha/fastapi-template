from typing import Any
from typing import Dict
from typing import Optional

from config import settings
from pydantic import EmailStr
from pydantic import validator

from sdk.schemas import BaseSchema
from sdk.schemas import PhoneNumberSchemaMixin
from sdk.schemas import UUIDSchemaMixin


class UserUpdate(BaseSchema):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None


class UserCreate(PhoneNumberSchemaMixin):
    name: str
    email: Optional[EmailStr] = None


class User(UUIDSchemaMixin):
    name: str
    phone_number: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    avatar_url: Optional[str] = None

    @validator('avatar_url', pre=True, always=True)
    def assemble_avatar_full_path(
        cls,  # noqa: RSPEC-5720
        v: Optional[str],  # noqa: RSPEC-5720
        values: Dict[str, Any],  # noqa: RSPEC-5720
    ) -> Optional[str]:
        avatar = values.get('avatar')
        if not avatar:
            return None
        return f'{settings.FULL_DOMAIN}/files/{avatar}'
