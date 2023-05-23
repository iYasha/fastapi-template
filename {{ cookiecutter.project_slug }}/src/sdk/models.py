import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


class UUIDModelMixin:
    uuid = sa.Column(UUID, primary_key=True, default=uuid.uuid4)


class SoftDeleteMixin:
    deleted_at = sa.Column(sa.DateTime(timezone=True), nullable=True)


class AuditMixin:
    created_at = sa.Column(sa.DateTime(timezone=True), default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())


class TrackingMixin:
    ip_address = sa.Column(sa.String, nullable=True)
    user_agent = sa.Column(sa.String, nullable=True)


class ExpireMixin:
    start_at = sa.Column(sa.DateTime(timezone=True))
    end_at = sa.Column(sa.DateTime(timezone=True))
