import asyncio

import sentry_sdk
from background import celery_app
from config import settings
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(  # type: ignore
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    release=settings.RELEASE,
    send_default_pii=settings.SENTRY_SEND_DEFAULT_PII,
    debug=settings.SENTRY_DEBUG,
    integrations=[
        CeleryIntegration(),
    ],
    request_bodies=settings.SENTRY_REQUEST_BODIES,
    traces_sample_rate=1.0,
)


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:  # type: ignore[return-value]
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if 'There is no current event loop in thread' in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


@celery_app.task(name='test_celery', acks_late=True)  # type: ignore
def test_celery(word: str) -> str:
    return f'Ok {word}'
