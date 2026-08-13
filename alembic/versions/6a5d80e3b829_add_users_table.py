"""add users table

Revision ID: 6a5d80e3b829
Revises: 163274bcd9df
Create Date: 2026-08-13 15:54:00.028088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a5d80e3b829'
down_revision: Union[str, Sequence[str], None] = '163274bcd9df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # role is a plain string ("admin"/"customer"), not a DB enum/CHECK constraint,
    # matching TransactionRow.type's existing style of app-level validation.
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # Table starts empty, so no setval() seeding is needed (unlike customer_id_seq/
    # account_id_seq in 4cedf3848236, which had to seed off pre-existing rows).
    op.execute("CREATE SEQUENCE user_id_seq")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SEQUENCE user_id_seq")
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
