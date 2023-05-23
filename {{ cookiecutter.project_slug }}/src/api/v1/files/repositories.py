import os

import aiofiles
import aioshutil
from config import settings


class FileRepository:
    media_path: str = settings.MEDIA_DIR
    tmp_path: str = settings.TMP_MEDIA_DIR

    @classmethod
    def exists(cls, file_name: str) -> bool:
        return os.path.exists(os.path.join(cls.tmp_path, file_name))

    @classmethod
    async def save(cls, file_name: str) -> None:
        """Save file from tmp to media folder."""
        await aioshutil.move(
            os.path.join(cls.tmp_path, file_name),
            os.path.join(cls.media_path, file_name),
        )

    @classmethod
    async def tmp_store(cls, file_name: str, content: bytes) -> None:
        """Store file in temporary directory."""
        async with aiofiles.open(os.path.join(cls.tmp_path, file_name), 'wb') as out_file:
            await out_file.write(content)

    @classmethod
    async def store(cls, file_name: str, content: bytes) -> None:
        """Store file in media directory."""
        async with aiofiles.open(os.path.join(cls.media_path, file_name), 'wb') as out_file:
            await out_file.write(content)
