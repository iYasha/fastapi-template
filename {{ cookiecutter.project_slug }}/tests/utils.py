import contextlib
import os
from argparse import Namespace
from types import SimpleNamespace
from typing import Iterable
from typing import Optional
from typing import Union

from alembic.config import Config
from config import settings


def make_alembic_config(
    cmd_opts: Union[Namespace, SimpleNamespace],
    base_path: str = settings.PROJECT_ROOT,
) -> Config:
    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name, cmd_opts=cmd_opts)

    # Replace path to alembic folder to absolute
    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location', os.path.join(base_path, alembic_location))
    if cmd_opts.pg_url:
        config.set_main_option('sqlalchemy.url', cmd_opts.pg_url)

    return config


def alembic_config_from_url(pg_url: Optional[str] = None) -> Config:
    """
    Provides Python object, representing alembic.ini file.
    """
    cmd_options = SimpleNamespace(
        config='alembic.ini',
        name='alembic',
        pg_url=pg_url,
        raiseerr=False,
        x=None,
    )
    return make_alembic_config(cmd_options)


class MockCacheBackend:
    """Mock Cache Backend"""

    def __init__(self) -> None:
        self._db = {}

    async def get(self, key: str) -> Optional[str]:
        return self._db.get(key)

    async def delete(self, key: str) -> None:
        with contextlib.suppress(KeyError):
            self._db.pop(key)

    async def keys(self, match: str) -> Iterable[str]:
        keywords = match.split('*')
        return [k for k in self._db.keys() if all(kw in k for kw in keywords)]

    async def set(self, key: str, value: Union[str, bytes, int], expire: int) -> None:
        self._db[key] = value

    async def setnx(self, key: str, value: Union[str, bytes, int], expire: int) -> None:
        v = self._db.get(key)  # pragma: no cover
        if v is None:  # pragma: no cover
            self._db[key] = value  # pragma: no cover

    async def incr(self, key: str) -> str:
        v = self._db.get(key)
        if v is not None:
            self._db[key] = int(v) + 1

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        return


class StringIOMock:
    async def __aenter__(self: 'StringIOMock') -> 'StringIOMock':
        return self

    async def __aexit__(self: 'StringIOMock', *args, **kwargs) -> None:
        return

    def __init__(self, default_data: str = '') -> None:
        self.data = default_data

    async def read(self) -> str:
        return self.data

    async def write(self, data: str) -> None:
        self.data += data
        return
