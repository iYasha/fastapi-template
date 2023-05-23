from fastapi import APIRouter
from starlette.responses import JSONResponse

from api.v1.auth.views import router as auth_router
from api.v1.files.views import router as files_router
from api.v1.healthcheck.views import router as healthcheck_router
from api.v1.users.views import router as users_router

api_router = APIRouter(default_response_class=JSONResponse)

api_router.include_router(healthcheck_router, prefix='/healthcheck', tags=['healthchecks'])
api_router.include_router(auth_router, prefix='/auth', tags=['auth'])
api_router.include_router(users_router, prefix='/users', tags=['users'])
api_router.include_router(files_router, prefix='/files', tags=['files'])
