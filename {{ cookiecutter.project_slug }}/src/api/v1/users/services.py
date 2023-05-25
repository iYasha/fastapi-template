import uuid
from uuid import UUID

from api.v1.files.services import FileService
from api.v1.users.repositories import UserRepository
from api.v1.users.schemas import User
from api.v1.users.schemas import UserCreate
from api.v1.users.schemas import UserUpdate
from sdk.exceptions.exceptions import make_error
from sdk.responses import ResponseStatus


class UserService:
    repository = UserRepository

    @classmethod
    async def update_me(
        cls,
        user_uuid: UUID,
        update_data: UserUpdate,
    ) -> None:
        data = update_data.dict(exclude_unset=True)
        if not data:
            return
        await cls.repository.update(**data).where(uuid=user_uuid).execute()
        if update_data.avatar is not None:
            await FileService.save(update_data.avatar)

    @classmethod
    async def get_user(
        cls,
        **kwargs,
    ) -> User:
        user = await cls.repository.get().where(**kwargs).execute()
        if not user:
            raise make_error(
                custom_code=ResponseStatus.USER_NOT_FOUND,
                message='User not found',
            )
        return User(**user)

    @classmethod
    async def create_user(
        cls,
        user_data: UserCreate,
    ) -> User:
        if await cls.repository.count().where(phone_number=user_data.phone_number).execute():
            raise make_error(
                custom_code=ResponseStatus.USER_ALREADY_EXISTS,
                message='User with this phone number already exists',
            )
        user_uuid = uuid.uuid4()
        await cls.repository.create(**user_data.dict(), uuid=user_uuid).execute()
        return User(**user_data.dict(), uuid=user_uuid)
