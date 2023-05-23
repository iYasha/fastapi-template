from typing import AsyncGenerator
from typing import Optional
from typing import Union

import sentry_sdk
from cache import RedisBackend
from config import settings
from database import database  # type: ignore
from databases.core import Transaction
from fastapi import Depends
from fastapi import Header
from fastapi import Request
from fastapi.security import OAuth2AuthorizationCodeBearer

from api.v1.auth.services import TokenService
from api.v1.users.schemas import User
from sdk.exceptions.exceptions import make_error
from sdk.responses import ResponseStatus
from sdk.schemas import TrackingSchemaMixin

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl='login',
    tokenUrl='login',
)


async def cache_storage() -> Union[RedisBackend, AsyncGenerator]:
    pool = await RedisBackend.create_pool(settings.REDIS_URI)
    try:
        yield pool
    finally:
        await pool.close()


async def get_tracking_data(
    request: Request,
    user_agent: Optional[str] = Header(None, alias='User-Agent'),
) -> TrackingSchemaMixin:
    return TrackingSchemaMixin(
        ip_address=request.client.host,  # type: ignore[union-attr]
        user_agent=user_agent,
    )


def get_transaction() -> Transaction:
    return database.transaction()


def get_access_token(
    token: str = Depends(oauth2_scheme),
) -> str:
    return token


async def get_authenticated_user(
    token: str = Depends(get_access_token),
    redis: RedisBackend = Depends(cache_storage),
) -> User:
    auth_error = make_error(
        custom_code=ResponseStatus.UNAUTHORIZED,
        message='Not authenticated',
    )
    user = TokenService.get_payload(token)
    if user is None:
        raise auth_error
    in_blacklist = await redis.get(f'bl:{token}')
    if in_blacklist:
        raise auth_error
    with sentry_sdk.configure_scope() as scope:
        scope.set_user(user['data'])
    return User(**user['data'])
