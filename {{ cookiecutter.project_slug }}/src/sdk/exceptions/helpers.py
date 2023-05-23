from asyncpg import PostgresError


def get_error_type(exc: Exception) -> str:
    if isinstance(exc, ConnectionError):
        return 'connection_error'
    elif isinstance(exc, TimeoutError):
        return 'timeout_error'
    elif isinstance(exc, PostgresError):
        return 'postgres_error'
    else:
        return 'unknown_error'
