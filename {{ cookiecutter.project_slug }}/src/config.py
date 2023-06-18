import os
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from passlib.context import CryptContext
from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import HttpUrl
from pydantic import validator
from pydantic.networks import PostgresDsn


class Environment(Enum):
    PROD = 'production'
    DEV = 'dev'
    LOCAL = 'local'


class HardSettings:
    SWAGGER_URL: str = '/{{ cookiecutter.docs_suffix }}/'
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_DIR: str = os.path.join(PROJECT_ROOT, 'media')
    CREDENTIALS_DIR: str = os.path.join(PROJECT_ROOT, 'credentials')
    TMP_MEDIA_DIR: str = os.path.join(PROJECT_ROOT, 'media/tmp')
    PWD_CONTEXT: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')


class EnvSettings(BaseSettings):
    """
    Настройки из переменных окружения
    """

    # Base configuration for the application.
    PROJECT_NAME: str = 'Fastapi default'
    ENVIRONMENT: Optional[Environment] = None
    FULL_DOMAIN: Optional[str] = None
    RELEASE: Optional[str] = None
    URL_SUBPATH: str = ''
    API_VERSION: str = '/api/v1'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    TESTING: bool = False

    # Authorization configuration.
    SECRET_KEY: str = ''
    OTP_RATE_LIMIT: int = 3
    OTP_EXPIRE: int = 60 * 5  # 5 minutes
    AUTH_JWT_ALGORITHM: str = 'HS256'
    AUTH_JWT_ACCESS_TOKEN_EXP_DELTA_MINUTES: int = 60 * 24 * 2  # 60 * 24 * 2  # 60 minutes * 24 hours * 2 days = 2 days
    JWT_REFRESH_TOKEN_EXP_DELTA_MINUTES: int = 60 * 24 * 14  # 60 minutes * 24 hours * 14 days = 2 week

    # API configuration.
    DEFAULT_DATETIME_FORMAT: str = '%Y-%m-%dT%H:%M:%S%z'

    # Database configuration.
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = 'app'
    DB_URI: Optional[str] = None

    @validator('POSTGRES_DB', pre=True)
    def get_actual_db_name(cls, v: str, values: Dict[str, Any]) -> str:  # noqa: RSPEC-5720
        test_postfix = '_test'

        if values.get('TESTING') and not v.endswith(test_postfix):
            v += test_postfix
        return v

    @validator('DB_URI', pre=True)
    def assemble_db_connection(
        cls,  # noqa: N805
        v: Optional[str],
        values: Dict[str, Any],  # noqa: RSPEC-5720
    ) -> str:
        if isinstance(v, str):
            return v

        path = values.get('POSTGRES_DB', '')
        return str(
            PostgresDsn.build(
                scheme='postgresql',
                user=values.get('POSTGRES_USER'),
                password=values.get('POSTGRES_PASSWORD'),
                host=values.get('POSTGRES_HOST'),
                port=str(values.get('POSTGRES_PORT')),
                path=f'/{path}',
            ),
        )

    # Redis configuration.
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: int = 6379
    REDIS_DB: str = '1'
    REDIS_URI: Optional[str] = None

    @validator('REDIS_URI', pre=True)
    def assemble_redis_uri(
        cls,  # noqa: N805
        v: Optional[str],
        values: Dict[str, Any],  # noqa: RSPEC-5720
    ) -> Optional[str]:
        if isinstance(v, str):
            return v

        host = values.get('REDIS_HOST')

        if not host:
            return None

        return 'redis://{}:{}/{}'.format(
            host,
            values.get('REDIS_PORT'),
            values.get('REDIS_DB'),
        )

    # Email configuration.
    EMAIL_SENDER: Optional[str] = None
    EMAIL_HOST: Optional[str] = None
    EMAIL_PORT: Optional[int] = None
    EMAIL_TLS: bool = True
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    @validator('EMAIL_PORT', pre=True)
    def validate_email_port(
        cls,  # noqa: N805
        v: Optional[Union[str, int]],
    ) -> Optional[int]:
        if not v:
            return None

        return int(v)

    # Sentry configuration.
    SENTRY_DSN: Optional[HttpUrl] = None
    SENTRY_DEBUG: bool = False
    SENTRY_REQUEST_BODIES: str = 'always'
    SENTRY_SEND_DEFAULT_PII: bool = False

    @validator('SENTRY_DSN', pre=True)
    def empty_string_validate(
        cls,  # noqa: N805
        value: Optional[str],
        values: Dict[str, Any],  # noqa: N805
    ) -> Optional[str]:  # noqa: RSPEC-5720
        if not value:
            return None

        return value

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class Settings(HardSettings, EnvSettings):
    @property
    def docs_url(self) -> str:
        return self.URL_SUBPATH + self.SWAGGER_URL

    @property
    def openapi_url(self) -> str:
        return self.URL_SUBPATH + self.SWAGGER_URL + 'openapi.json'


settings = Settings()
