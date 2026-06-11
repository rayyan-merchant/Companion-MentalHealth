"""Initial production schema.

Revision ID: 20260611_0001
Revises:
Create Date: 2026-06-11
"""
from alembic import op

from backend.database import Base
from backend import models  # noqa: F401


revision = "20260611_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
