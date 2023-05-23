from dependencies import get_authenticated_user
from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv

from api.v1.users.schemas import User
from api.v1.users.schemas import UserUpdate
from api.v1.users.services import UserService
from sdk.responses import DefaultResponse
from sdk.responses import DefaultResponseSchema

router = APIRouter()


@cbv(router)
class UserViews:
    authenticated_user: User = Depends(get_authenticated_user)

    @router.get(
        '/me',
        name='users:me',
        response_model=DefaultResponseSchema[User],
    )
    async def get_me(
        self,
    ) -> DefaultResponse:
        return DefaultResponse(
            content=await UserService.get_user(uuid=self.authenticated_user.uuid),
        )

    @router.patch(
        '/me',
        name='users:update',
        response_model=DefaultResponseSchema[bool],
    )
    async def update_me(
        self,
        *,
        data: UserUpdate,
    ) -> DefaultResponse:
        await UserService.update_me(
            user_uuid=self.authenticated_user.uuid,
            update_data=data,
        )
        return DefaultResponse(content=True)
