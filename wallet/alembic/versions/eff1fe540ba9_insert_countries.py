"""insert_countries

Revision ID: eff1fe540ba9
Revises: 8a46cbf0cdfe
Create Date: 2021-03-25 20:05:20.464332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy import table, column, Integer, String, delete
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE, COUNTRY_CODES_FOR_NON_GEO_REGIONS

revision = 'eff1fe540ba9'
down_revision = '8a46cbf0cdfe'
branch_labels = None
depends_on = None


country = table(
    "country",
    column("id", Integer),
    column("iso_code", String),
    column("country_code", Integer),
)


def upgrade():
    data = []
    for country_code, iso_codes in COUNTRY_CODE_TO_REGION_CODE.items():
        if country_code not in COUNTRY_CODES_FOR_NON_GEO_REGIONS:
            for iso_code in iso_codes:
                data.append({
                    "iso_code": iso_code,
                    "country_code": country_code
                })
    op.bulk_insert(country, data)


def downgrade():
    query = (delete(country))
    op.execute(query)
