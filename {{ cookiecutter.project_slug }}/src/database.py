from typing import TypeVar

import databases
from config import settings
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

__all__ = ('database', 'metadata', 'Base')

database: databases.core.Database
if settings.TESTING:
    database = databases.Database(str(settings.DB_URI), force_rollback=True)
else:
    database = databases.Database(str(settings.DB_URI))

meta = MetaData(
    naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    },
)

Base = declarative_base(metadata=meta)
ModelType = TypeVar('ModelType', bound=Base)  # type: ignore
metadata = Base.metadata
