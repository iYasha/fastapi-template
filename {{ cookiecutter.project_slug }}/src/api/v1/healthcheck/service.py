import os
import uuid

import aiofiles
import psutil

{% if cookiecutter.add_celery == 'y' %}
from background import celery_app
{% endif %}
from cache import RedisBackend
from database import database

from api.v1.healthcheck.config import HealthCheck


async def check_database() -> str:
    query = 'SELECT 1'
    try:
        await database.execute(query)
    except Exception as e:
        return str(e)
    return HealthCheck.OK_STATUS


def check_memory_usage() -> str:
    memory = psutil.virtual_memory()
    if HealthCheck.MEMORY_MIN and memory.available < (HealthCheck.MEMORY_MIN * 1024 * 1024):
        avail = '{:n}'.format(int(memory.available / 1024 / 1024))
        threshold = '{:n}'.format(HealthCheck.MEMORY_MIN)
        return '{avail} MB available RAM below {threshold} MB'.format(
            avail=avail,
            threshold=threshold,
        )
    return HealthCheck.OK_STATUS


def check_disk_usage() -> str:
    du = psutil.disk_usage('/')
    if HealthCheck.DISK_USAGE_MAX and du.percent >= HealthCheck.DISK_USAGE_MAX:
        return '{percent}% disk usage exceeds {disk_usage}%'.format(
            percent=du.percent,
            disk_usage=HealthCheck.DISK_USAGE_MAX,
        )
    return HealthCheck.OK_STATUS


async def check_file_storage() -> str:
    file_name = f'test-{uuid.uuid4()}.txt'
    content = 'this is the healthtest file content'

    try:
        async with aiofiles.open(file_name, mode='w') as f:
            await f.write(content)

        if not os.path.exists(file_name):
            raise Exception('File not exist')

        async with aiofiles.open(file_name, mode='r') as f:
            result = await f.read()

        if result != content:
            raise Exception('File content does not match')
        os.remove(file_name)

    except Exception as e:
        return str(e)

    return HealthCheck.OK_STATUS


def readiness_check() -> str:
    return 'Ok'


def sentry_debug() -> None:
    raise Exception


async def check_redis(redis_client: RedisBackend) -> str:
    resp = await redis_client.ping()
    if not resp:
        return 'Redis is not available'
    return HealthCheck.OK_STATUS

{% if cookiecutter.add_celery == 'y' %}
def celery_check() -> str:
    task = celery_app.send_task(
        'test_celery',
        args=['hello'],
        queue='main-queue',
        routing_key='main-queue',
    )
    return str(task)
{% endif %}
