import asyncio
from typing import Generator

import pytest
import pytest_asyncio
from alembic.command import upgrade as alembic_upgrade
from config import settings
from database import database
from fastapi import FastAPI
from httpx import AsyncClient
from requests import Session as RequestSession
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import drop_database
from transaction import Transaction
from utils import MockCacheBackend
from utils import alembic_config_from_url

from sdk.schemas import TrackingSchemaMixin

if not settings.TESTING:
    raise ValueError('Please, set TESTING=True in core/config.py to run tests')


@pytest_asyncio.fixture()
async def db_connection() -> Generator:
    if not database_exists(settings.DB_URI):
        create_database(settings.DB_URI)
        alembic_config = alembic_config_from_url(settings.DB_URI)
        alembic_upgrade(alembic_config, 'head')
    if not database.is_connected:
        await database.connect()
    transaction = await database.transaction()
    try:
        yield transaction
    finally:
        await transaction.rollback()


@pytest_asyncio.fixture()
async def client(app: FastAPI) -> Generator[RequestSession, None, None]:
    async with AsyncClient(app=app, base_url='http://localhost') as c:
        yield c


@pytest.fixture(scope='session')
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def app(db_connection: Transaction) -> FastAPI:
    from main import app as fastapi_app

    fastapi_app.router.on_startup = []
    fastapi_app.router.on_shutdown = []

    return fastapi_app


@pytest.fixture()
def tracking_params() -> TrackingSchemaMixin:
    return TrackingSchemaMixin(
        ip='192.168.0.1',
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1',
    )


@pytest.fixture()
def redis() -> MockCacheBackend:
    return MockCacheBackend()


def pytest_sessionfinish() -> None:
    if database_exists(settings.DB_URI):
        drop_database(settings.DB_URI)
