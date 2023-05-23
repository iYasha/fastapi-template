from datetime import datetime
from datetime import timedelta

from config import settings

from sdk.schemas import BaseSchema


class Session(BaseSchema):
    access_token: str
    refresh_token: str
    expires_in: datetime
    token_type: str = 'bearer'

    @staticmethod
    def get_access_token_expires() -> datetime:
        return datetime.now() + timedelta(minutes=settings.AUTH_JWT_ACCESS_TOKEN_EXP_DELTA_MINUTES)

    @staticmethod
    def get_refresh_token_expires() -> datetime:
        return datetime.now() + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXP_DELTA_MINUTES)
