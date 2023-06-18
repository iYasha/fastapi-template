import sqlalchemy as sa
from database import Base  # type: ignore

from sdk.models import AuditMixin
from sdk.models import UUIDModelMixin


class User(UUIDModelMixin, AuditMixin, Base):
    """User model"""

    __tablename__ = 'users'

    name = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=False, unique=True)
    email = sa.Column(sa.String, nullable=True)
    avatar = sa.Column(sa.String, nullable=True)
