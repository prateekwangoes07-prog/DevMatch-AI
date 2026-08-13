"""update_appointment_and_call_ondelete_to_restrict

Revision ID: 7dd0cae82323
Revises: 896296321246
Create Date: 2026-08-13 09:20:50.496764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7dd0cae82323'
down_revision: Union[str, Sequence[str], None] = '896296321246'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('appointments_client_id_fkey', 'appointments', type_='foreignkey')
    op.create_foreign_key('appointments_client_id_fkey', 'appointments', 'clients', ['client_id'], ['id'], ondelete='RESTRICT')
    op.drop_constraint('calls_client_id_fkey', 'calls', type_='foreignkey')
    op.create_foreign_key('calls_client_id_fkey', 'calls', 'clients', ['client_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('calls_client_id_fkey', 'calls', type_='foreignkey')
    op.create_foreign_key('calls_client_id_fkey', 'calls', 'clients', ['client_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('appointments_client_id_fkey', 'appointments', type_='foreignkey')
    op.create_foreign_key('appointments_client_id_fkey', 'appointments', 'clients', ['client_id'], ['id'], ondelete='CASCADE')
