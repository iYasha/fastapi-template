import random
import string
import uuid
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional

import jwt
from cache import RedisBackend
from config import Environment
from config import settings

from api.v1.auth.schemas import Session
from api.v1.users.schemas import User
from api.v1.users.schemas import UserCreate
from api.v1.users.services import UserService
from sdk.exceptions.exceptions import make_error
from sdk.responses import ResponseStatus
from sdk.schemas import TrackingSchemaMixin
from sdk.utils import DefaultJSONEncoder


class NotificationService:
    @classmethod
    async def send_sms(
        cls,
        phone_number: str,
        message: str,
    ) -> bool:
        pass


class TokenService:
    @classmethod
    def create_access(
        cls,
        payload: Dict[str, Any],
        secret_key: str,
        sub: str,
        expires_in: datetime,
        algorithm: str,
    ) -> str:
        body = {
            'iat': datetime.utcnow(),
            'exp': expires_in,
            'sub': sub,
            'data': payload,
        }
        return jwt.encode(
            payload=body,
            key=secret_key,
            algorithm=algorithm,
            json_encoder=DefaultJSONEncoder,
        )

    @classmethod
    def create_refresh(
        cls,
        secret_key: str,
        sub: str,
        expires_in: datetime,
        algorithm: str,
    ) -> str:
        body = {
            'iat': datetime.utcnow(),
            'exp': expires_in,
            'sub': sub,
        }
        return jwt.encode(
            payload=body,
            key=secret_key,
            algorithm=algorithm,
            json_encoder=DefaultJSONEncoder,
        )

    @classmethod
    def get_payload(
        cls,
        token: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.AUTH_JWT_ALGORITHM])
        except jwt.PyJWTError:
            return None


class SessionService:
    user_schema: User = User

    @classmethod
    async def create_session(
        cls,
        redis: RedisBackend,
        user: user_schema,
    ) -> Session:
        expires_in = Session.get_access_token_expires()
        access_token = TokenService.create_access(
            payload=user.dict(),
            secret_key=settings.SECRET_KEY,
            sub=str(user.uuid),
            expires_in=expires_in,
            algorithm=settings.AUTH_JWT_ALGORITHM,
        )
        refresh_token = TokenService.create_refresh(
            secret_key=settings.SECRET_KEY,
            sub=str(user.uuid),
            expires_in=Session.get_refresh_token_expires(),
            algorithm=settings.AUTH_JWT_ALGORITHM,
        )
        await redis.set(
            f'{refresh_token}:{access_token}:{user.uuid}',
            str(user.uuid),
            expire=settings.JWT_REFRESH_TOKEN_EXP_DELTA_MINUTES,
        )
        return Session(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    @classmethod
    async def logout(cls, access_token: str, redis: RedisBackend) -> None:
        payload = TokenService.get_payload(access_token)
        expires_in = payload['exp'] if payload else 0
        await redis.set(
            f'bl:{access_token}',
            access_token,
            expire=expires_in,
        )

    @classmethod
    async def logout_all(
        cls,
        user_id: uuid.UUID,
        redis: RedisBackend,
    ) -> None:
        key = f'*:*:{user_id}'
        keys = await redis.keys(key)
        expire = (datetime.now() - Session.get_access_token_expires()).seconds
        for key in keys:
            access_token = key.decode('utf-8').split(':')[2]
            await redis.set(
                f'bl:{access_token}',
                access_token,
                expire=expire,
            )

    @classmethod
    async def refresh_session(
        cls,
        redis: RedisBackend,
        access_token: str,
        refresh_token: str,
    ) -> Session:
        token_invalid = make_error(
            custom_code=ResponseStatus.INVALID_ACCESS_OR_REFRESH_TOKEN,
            message='Token invalid or expired',
        )
        refresh_payload = TokenService.get_payload(refresh_token)
        if refresh_payload is None:
            raise token_invalid
        user_id = refresh_payload.get('sub')
        if user_id is None:
            raise token_invalid
        user = await UserService.get_user(uuid=user_id)
        in_blacklist = await redis.get(f'bl:{access_token}')
        if in_blacklist:
            raise token_invalid
        session = await redis.get(f'{refresh_token}:{access_token}:{user_id}')
        if session is None:
            raise token_invalid
        await cls.logout(access_token, redis)
        return await cls.create_session(user=user, redis=redis)


class AuthorizationService:
    @classmethod
    def generate_code(
        cls,
    ) -> str:
        return ''.join(random.choices(string.digits, k=6))

    @classmethod
    async def is_blocked(
        cls,
        service_name: str,
        ip: str,
        redis: RedisBackend,
    ) -> bool:
        timeout_key = f'{service_name}:timeout:{ip}'
        timeout = await redis.get(timeout_key)

        if timeout is not None:
            return True

        rate_key = f'{service_name}:rate:{ip}'
        rate = await redis.get(rate_key)

        if rate is not None:
            rate = int(rate)
            if rate > settings.OTP_RATE_LIMIT:
                await redis.set(timeout_key, 1, expire=60 * 5)
                return True
        else:
            await redis.set(rate_key, 1, expire=60)

        await redis.incr(rate_key)
        return False

    @classmethod
    async def send_otp(
        cls,
        phone_number: str,
        ip: str,
        redis: RedisBackend,
    ) -> bool:
        if await cls.is_blocked('login', ip, redis):
            raise make_error(
                custom_code=ResponseStatus.TOO_MANY_REQUESTS,
                message='Too many attempts. Try again in 5 minutes',
            )
        code = cls.generate_code()
        await redis.set(
            f'otp:attempt:{phone_number}:{code}',
            phone_number,
            expire=settings.OTP_EXPIRE,
        )
        sms_message = f'Code: {code}'
        if settings.ENVIRONMENT == Environment.LOCAL:
            print(f'Phone Number: {phone_number}, Code: {code}')  # noqa: T201
            return True
        return await NotificationService.send_sms(phone_number, sms_message)

    @classmethod
    async def verify_code(
        cls,
        code: str,
        ip: str,
        redis: RedisBackend,
    ) -> str:
        if await cls.is_blocked('verify', ip, redis):
            raise make_error(
                custom_code=ResponseStatus.TOO_MANY_REQUESTS,
                message='Too many requests',
            )
        pattern = f'otp:attempt:*:{code}'
        attempts = await redis.keys(pattern)
        if not attempts:
            raise make_error(
                custom_code=ResponseStatus.AUTHORIZATION_CODE_INVALID,
                message='Invalid authorization code.',
                code='Invalid code.',
            )
        key = attempts[0]
        phone_number = await redis.get(key)
        await redis.delete(key)
        return phone_number.decode()  # noqa: R504

    @classmethod
    async def register(
        cls,
        user: UserCreate,
        tracking_params: TrackingSchemaMixin,
        redis: RedisBackend,
    ) -> bool:
        user = await UserService.create_user(user_data=user)
        return await cls.send_otp(
            phone_number=user.phone_number,
            ip=tracking_params.ip_address,
            redis=redis,
        )
