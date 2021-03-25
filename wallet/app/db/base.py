# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.users import *  # noqa
from app.models.wallets import *  # noqa
from app.models.settings import *  # noqa
