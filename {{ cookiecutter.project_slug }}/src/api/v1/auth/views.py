from cache import RedisBackend
from config import Environment
from config import settings
from dependencies import cache_storage
from dependencies import get_access_token
from dependencies import get_authenticated_user
from dependencies import get_tracking_data
from dependencies import get_transaction
from fastapi import Body
from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from transaction import Transaction

from api.v1.auth.schemas import Session
from api.v1.auth.services import AuthorizationService
from api.v1.auth.services import SessionService
from api.v1.users.schemas import UserCreate
from api.v1.users.services import UserService
from sdk.responses import DefaultResponse
from sdk.responses import DefaultResponseSchema
from sdk.schemas import PhoneNumberSchemaMixin
from sdk.schemas import TrackingSchemaMixin

router = InferringRouter()


@cbv(router)
class AuthorizationViews:
    tracking_params: TrackingSchemaMixin = Depends(get_tracking_data)

    @router.post('/register', name='auth:register', response_model=DefaultResponseSchema[bool])
    async def register(
        self,
        *,
        transaction: Transaction = Depends(get_transaction),
        redis: RedisBackend = Depends(cache_storage),
        user_data: UserCreate,
    ) -> DefaultResponse:
        async with transaction:
            success = await AuthorizationService.register(
                user_data,
                self.tracking_params,
                redis,
            )

        return DefaultResponse(content=success)

    @router.post('/login', name='auth:login', response_model=DefaultResponseSchema[bool])
    async def login(
        self,
        *,
        redis: RedisBackend = Depends(cache_storage),
        user_data: PhoneNumberSchemaMixin,
    ) -> DefaultResponse:
        if (  # For testing purposes only
            settings.ENVIRONMENT in (Environment.DEV, Environment.LOCAL) and user_data.phone_number == '+380501234567'
        ):
            return DefaultResponse(content=True)

        user = await UserService.get_user(phone_number=user_data.phone_number)
        success = await AuthorizationService.send_otp(
            phone_number=user.phone_number,
            ip=self.tracking_params.ip_address,
            redis=redis,
        )

        return DefaultResponse(content=success)

    @router.post('/verify', name='auth:verify', response_model=DefaultResponseSchema[Session])
    async def verify(
        self,
        *,
        redis: RedisBackend = Depends(cache_storage),
        code: str = Body(..., embed=True, min_length=6, max_length=6),
    ) -> DefaultResponse:
        if settings.ENVIRONMENT in (Environment.DEV, Environment.LOCAL) and code == '111111':
            phone_number = '+380501234567'  # For testing purposes only
        else:
            phone_number = await AuthorizationService.verify_code(
                code=code,
                ip=self.tracking_params.ip_address,
                redis=redis,
            )
        user = await UserService.get_user(phone_number=phone_number)
        session = await SessionService.create_session(
            redis,
            user,
        )
        return DefaultResponse(content=session)

    @router.post(
        '/refresh-token',
        name='auth:refresh-token',
        response_model=DefaultResponseSchema[Session],
        dependencies=[Depends(get_authenticated_user)],
    )
    async def refresh_token(
        self,
        *,
        redis: RedisBackend = Depends(cache_storage),
        transaction: Transaction = Depends(get_transaction),
        access_token: str = Depends(get_access_token),
        refresh_token: str = Body(..., embed=True),
    ) -> DefaultResponse:
        async with transaction:
            session = await SessionService.refresh_session(
                access_token=access_token,
                refresh_token=refresh_token,
                redis=redis,
            )
            return DefaultResponse(content=session)

    @router.delete(
        '/logout',
        name='auth:logout',
        response_model=DefaultResponseSchema,
        dependencies=[Depends(get_authenticated_user)],
    )
    async def logout(
        self,
        *,
        redis: RedisBackend = Depends(cache_storage),
        access_token: str = Depends(get_access_token),
    ) -> DefaultResponse:
        await SessionService.logout(access_token, redis)
        return DefaultResponse()
