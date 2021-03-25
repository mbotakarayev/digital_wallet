"""insert_tariffs

Revision ID: 1852409fd74a
Revises: 2fb9ca7c5a27
Create Date: 2021-03-24 02:22:25.904188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import column, delete, table, Integer, Numeric

revision = '1852409fd74a'
down_revision = '2fb9ca7c5a27'
branch_labels = None
depends_on = None


wallet_tariff = table(
    "wallettariff",
    column("id", Integer),
    column("balance_limit", Numeric),
    column("price", Numeric),
    column("one_transfer_limit", Numeric),
)


def upgrade():
    op.bulk_insert(wallet_tariff, [
        {"balance_limit": 10000.0, "price": 0.0, "one_transfer_limit": 1000.0},
        {"balance_limit": 25000.0, "price": 5.0, "one_transfer_limit": 2500.0},
        {"balance_limit": 50000.0, "price": 7.0, "one_transfer_limit": 5000.0},
    ])


def downgrade():
    query = (delete(wallet_tariff))
    op.execute(query)
