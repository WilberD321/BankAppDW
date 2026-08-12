"""id sequences for customers and accounts

Revision ID: 4cedf3848236
Revises: ee6c5fc5ceba
Create Date: 2026-08-11 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4cedf3848236'
down_revision: Union[str, Sequence[str], None] = 'ee6c5fc5ceba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add a Postgres SEQUENCE per id prefix, seeded from the current max id in each table."""
    op.execute("CREATE SEQUENCE customer_id_seq")
    op.execute("CREATE SEQUENCE account_id_seq")

    # Seed each sequence so the next nextval() continues right after the highest
    # id already in the table. Sequences have MINVALUE 1, so setval(seq, 0) is
    # invalid on an empty table -- use the 3-arg form (value, is_called=false)
    # instead, which makes the *next* nextval() return exactly 1.
    op.execute(
        "SELECT setval('customer_id_seq', "
        "COALESCE((SELECT MAX(substring(id from 2)::int) FROM customers WHERE id ~ '^c[0-9]+$'), 1), "
        "(SELECT MAX(substring(id from 2)::int) FROM customers WHERE id ~ '^c[0-9]+$') IS NOT NULL)"
    )
    op.execute(
        "SELECT setval('account_id_seq', "
        "COALESCE((SELECT MAX(substring(id from 2)::int) FROM accounts WHERE id ~ '^a[0-9]+$'), 1), "
        "(SELECT MAX(substring(id from 2)::int) FROM accounts WHERE id ~ '^a[0-9]+$') IS NOT NULL)"
    )


def downgrade() -> None:
    op.execute("DROP SEQUENCE customer_id_seq")
    op.execute("DROP SEQUENCE account_id_seq")
