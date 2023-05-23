import time
from typing import Callable

import uvicorn
from config import settings
from database import database  # type: ignore
from fastapi import FastAPI
from fastapi import Request
from fastapi import Security
from fastapi.openapi.models import Response
from sentry import init_sentry
from starlette.middleware.cors import CORSMiddleware

from api.router import api_router
from sdk.exceptions.exception_handler_mapping import exception_handler_mapping
from sdk.utils import fake_http_bearer

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.RELEASE,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    exception_handlers=exception_handler_mapping,
    dependencies=[
        Security(fake_http_bearer),
    ],
)

# Routers
app.include_router(api_router, prefix=settings.URL_SUBPATH + settings.API_VERSION)

if settings.SENTRY_DSN:
    app = init_sentry(app)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=tuple(map(str, settings.BACKEND_CORS_ORIGINS)),
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@app.on_event('startup')
async def startup() -> None:
    await database.connect()


@app.on_event('shutdown')
async def shutdown() -> None:
    await database.disconnect()


@app.middleware('http')
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response


def run() -> None:
    uvicorn.run('main:app', host='0.0.0.0', port=8000, access_log=False, reload=True)


if __name__ == '__main__':
    run()
