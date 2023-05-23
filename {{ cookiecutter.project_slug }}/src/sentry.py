from typing import Callable

import sentry_sdk
from config import settings
from fastapi import FastAPI
from fastapi import Request
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from sdk.exceptions.helpers import get_error_type


class SentryMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self: 'SentryMiddleware',
        request: Request,
        call_next: Callable,
    ) -> Response:
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag('app', 'backend')
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag('error_type', get_error_type(e))
            raise e


def init_sentry(app: FastAPI) -> FastAPI:
    sentry_sdk.init(  # type: ignore
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.RELEASE,
        send_default_pii=settings.SENTRY_SEND_DEFAULT_PII,
        debug=settings.SENTRY_DEBUG,
        integrations=[
            RedisIntegration(),
            CeleryIntegration(),
        ],
        request_bodies=settings.SENTRY_REQUEST_BODIES,
        traces_sample_rate=1.0,
    )

    app.add_middleware(SentryMiddleware)

    return app
