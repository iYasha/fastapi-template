import asyncio

import sentry_sdk
from celery import Celery
from celery.signals import worker_process_init
from celery.signals import worker_process_shutdown
from config import settings
from database import database  # type: ignore
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


@worker_process_init.connect()
def init(*args, **kwargs) -> None:
    loop = asyncio.get_event_loop()
    if not database.is_connected:
        loop.run_until_complete(database.connect())
    if settings.SENTRY_DSN:
        sentry_sdk.init(  # type: ignore
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            release=settings.RELEASE,
            debug=settings.SENTRY_DEBUG,
            integrations=[
                LoggingIntegration(event_level=None),
                SqlalchemyIntegration(),
                CeleryIntegration(),
            ],
            request_bodies=settings.SENTRY_REQUEST_BODIES,
        )


@worker_process_shutdown.connect()
def shutdown(*args, **kwargs) -> None:
    loop = asyncio.get_event_loop()
    if database.is_connected:
        loop.run_until_complete(database.disconnect())


celery_app = Celery(settings.PROJECT_NAME, broker=settings.REDIS_URI, backend='rpc://')
