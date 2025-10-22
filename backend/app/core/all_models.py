from app.core import models as _models
from app.domain.listings import enhanced_real_estate_models  # noqa


def import_all_models() -> bool:
    """Ensure all ORM mappers are imported."""
    return True
