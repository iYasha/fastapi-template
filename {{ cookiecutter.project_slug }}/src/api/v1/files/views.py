from dependencies import get_authenticated_user
from fastapi import Depends
from fastapi import File
from fastapi import Query
from fastapi import UploadFile
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from api.v1.files.services import FileService
from api.v1.users.schemas import User
from sdk.responses import DefaultResponse
from sdk.responses import DefaultResponseSchema

router = InferringRouter()


@cbv(router)
class FileViews:
    authenticated_user: User = Depends(get_authenticated_user)

    @router.post('/upload', name='files:upload', response_model=DefaultResponseSchema[str])
    async def upload_file(
        self,
        *,
        file: UploadFile = File(...),
        page: str = Query(..., min_length=2, max_length=20),
    ) -> DefaultResponse:
        file_name = await FileService.upload(file, page)
        return DefaultResponse(content=file_name)
