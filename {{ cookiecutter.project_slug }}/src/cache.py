from typing import List
from typing import Union

from aioredis import Redis


class RedisBackend:
    """Setup the Redis connection for the backend using aioredis"""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    @staticmethod
    async def create_pool(uri: str) -> 'RedisBackend':
        redis = await Redis.from_url(uri)
        return RedisBackend(redis)

    async def close(self) -> None:
        await self._redis.close()

    async def get(self: 'RedisBackend', key: Union[str, bytes]) -> bytes:
        return await self._redis.get(key)

    async def delete(self: 'RedisBackend', key: Union[str, bytes]) -> None:
        await self._redis.delete(key)

    async def keys(self: 'RedisBackend', match: Union[str, bytes]) -> List[bytes]:
        return await self._redis.keys(match)

    async def set(
        self: 'RedisBackend',
        key: str,
        value: Union[str, bytes, int],
        expire: int = 0,
    ) -> None:
        await self._redis.set(key, value, ex=expire)

    async def setnx(
        self: 'RedisBackend',
        key: str,
        value: Union[str, bytes, int],
        expire: int,
    ) -> None:
        await self._redis.setnx(key, value)
        await self._redis.expire(key, expire)

    async def incr(self: 'RedisBackend', key: str) -> str:
        return await self._redis.incr(key)

    async def ping(self) -> bool:
        return await self._redis.ping()
