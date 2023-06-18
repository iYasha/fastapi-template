from cache import RedisBackend
from dependencies import cache_storage
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from api.v1.healthcheck import schemas
from api.v1.healthcheck import service
from sdk.responses import DefaultResponse
from sdk.responses import DefaultResponseSchema

router = APIRouter()


@router.get('/readiness', response_model=DefaultResponseSchema[str])
def readiness() -> DefaultResponse:
    """Простейший эндпоинт для проверки работоспособности сервиса"""
    return DefaultResponse(content=service.readiness_check())


@router.get('/check_database', response_model=DefaultResponseSchema[str])
async def check_database() -> DefaultResponse:
    """Эндпоинт для проверки коннекта к БД"""
    return DefaultResponse(content=await service.check_database())


@router.get('/sentry_debug')
def sentry_debug() -> None:
    """Простейший эндпоинт для проверки работоспособности отправки ошибок в Sentry"""
    service.sentry_debug()


@router.get('/redis', response_model=DefaultResponseSchema[str])
async def redis_check(redis_client: RedisBackend = Depends(cache_storage)) -> DefaultResponse:
    return DefaultResponse(content=await service.check_redis(redis_client))


@router.get('/celery', response_model=DefaultResponseSchema[str])
async def celery_check() -> DefaultResponse:
    return DefaultResponse(content=service.celery_check())


@router.get('/liveness', response_model=DefaultResponseSchema[schemas.HealthCheckStatuses])
async def liveness(redis_client: RedisBackend = Depends(cache_storage)) -> DefaultResponse:
    """Сводная информация по работоспособности различных компонентов, используемых сервисом"""

    status_code = status.HTTP_200_OK
    hc_statuses = schemas.HealthCheckStatuses(
        database_backend=await service.check_database(),
        default_file_storage_health_check=await service.check_file_storage(),
        disk_usage=service.check_disk_usage(),
        memory_usage=service.check_memory_usage(),
        redis_health_check=await service.check_redis(redis_client),
    )
    if not hc_statuses.is_all_success():
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return DefaultResponse(content=hc_statuses, status_code=status_code)
